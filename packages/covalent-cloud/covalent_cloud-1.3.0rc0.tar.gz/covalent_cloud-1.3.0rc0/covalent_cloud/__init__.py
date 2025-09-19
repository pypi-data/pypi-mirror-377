# Copyright 2023 Agnostiq Inc.


from importlib import metadata

from . import cloud_executor
from .cloud_executor.cloud_executor import CloudExecutor
from .cloud_executor.oci_cloud_executor import OCICloudExecutor
from .dispatch_management import cancel, dispatch, get_result, redispatch
from .function_serve.decorators import service
from .function_serve.deployment import deploy, get_deployment
from .function_serve.models import Deployment
from .service_account_interface.auth_config_manager import (
    get_api_key,
    get_dr_api_token,
    save_api_key,
    save_dr_api_token,
)
from .service_account_interface.client import get_client
from .shared.classes.settings import settings
from .swe_management.secrets_manager import delete_secret, list_secrets, store_secret
from .swe_management.swe_manager import create_env, delete_env, get_envs
from .volume.volume import volume

__version__ = metadata.version("covalent_cloud")

__all__ = [
    "cloud_executor",
    "CloudExecutor",
    "OCICloudExecutor",
    "cancel",
    "dispatch",
    "get_result",
    "redispatch",
    "get_api_key",
    "save_api_key",
    "get_dr_api_token",
    "save_dr_api_token",
    "get_client",
    "settings",
    "delete_secret",
    "list_secrets",
    "store_secret",
    "create_env",
    "get_envs",
    "delete_env",
    "volume",
    "deploy",
    "get_deployment",
    "Deployment",
    "service",
]
