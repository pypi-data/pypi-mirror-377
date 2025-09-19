# Copyright 2024 Agnostiq Inc.

import inspect
import typing
from typing import Any, Callable, Union

from covalent._workflow.lattice import Lattice

from covalent_cloud.function_serve.assets import AssetsMediator
from covalent_cloud.function_serve.common import wait_for_deployment_to_be_active
from covalent_cloud.function_serve.models import Deployment
from covalent_cloud.service_account_interface.client import get_deployment_client
from covalent_cloud.shared.classes.settings import Settings, settings
from covalent_cloud.shared.schemas.volume import Volume

if typing.TYPE_CHECKING:
    from covalent_cloud.function_serve.service_class import FunctionService

__all__ = [
    "deploy",
    "get_deployment",
]


def deploy(
    function_service: "FunctionService", volume: Volume = None, settings: Settings = settings
) -> Callable[[Any], Deployment]:
    """Deploy a function service to Covalent Cloud.

    Args:
        function_service: A function decorated with `@cc.service`.
        volume: Grant access to a cloud storage volume in Covalent Cloud. Defaults to None.
        settings: User settings for Covalent Cloud. Defaults to settings on the client machine.

    Returns:
        A callable which launches the deployment and has the same signature as the initializer
        for `function_service`.
    """

    if isinstance(function_service, Lattice):
        raise TypeError("Lattices cannot be deployed. Please use `cc.dispatch()` instead.")

    def deploy_wrapper(*args, **kwargs) -> Deployment:

        # Force a TypeError if the arguments are invalid.
        # If not done here, error will be raised in remote host.
        sig = inspect.signature(function_service.init_func)
        sig.bind(*args, **kwargs)

        if volume is not None:
            # Override the volume for the function service
            function_service.volume = volume

        fn_service_model = function_service.get_model(*args, **kwargs)

        assets_mediator = AssetsMediator()
        fn_service_model = assets_mediator.hydrate_assets_from_model(
            fn_service_model, settings=settings
        )

        assets_mediator.upload_all()

        dumped_model = fn_service_model.model_dump()

        deployment_client = get_deployment_client(settings)
        response = deployment_client.post(
            "/functions",
            request_options={
                "json": dumped_model,
            },
        )

        deployment = Deployment.from_function_record(response.json())

        # Attach route methods for ease of use
        deployment.attach_route_methods()

        return deployment

    return deploy_wrapper


def get_deployment(
    function_id: Union[str, Deployment],
    wait: Union[bool, int, float] = False,
    settings: Settings = settings,
) -> Deployment:
    """Retrieve or refresh a client object for a deployed function service.

    Args:
        function_id: ID string or client object for the target deployment.
        wait: Option to wait for the deployment to be active. Defaults to False.
            Numerical values represent the approximate time to wait (in seconds)
            for the deployment to finish initializing, before raising a client-side `TimeoutError`.
            The boolean value True corresponds to 3600, i.e. 1 hour.
        settings: User settings for Covalent Cloud. Defaults to settings on the client machine.

    Returns:
        Deployment: Deployment object for the function service.
    """

    if isinstance(function_id, Deployment):
        function_id = function_id.function_id

    deployment_client = get_deployment_client(settings)
    response = deployment_client.get(f"/functions/{function_id}")
    deployment = Deployment.from_function_record(response.json())

    # Attach route methods for ease of use
    deployment.attach_route_methods()

    if not wait:
        return deployment

    if isinstance(wait, bool):
        wait_time_max = 3600
    elif isinstance(wait, (int, float)) and wait > 0:
        wait_time_max = wait
    else:
        raise ValueError("Invalid value for `wait`. Must be a boolean or a positive int or float.")

    return wait_for_deployment_to_be_active(deployment, wait_time_max=wait_time_max)
