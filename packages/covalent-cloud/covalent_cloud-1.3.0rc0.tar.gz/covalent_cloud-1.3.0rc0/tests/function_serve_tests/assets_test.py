# Copyright 2024 Agnostiq Inc.

"""Unit tests for function serve assets"""

from unittest.mock import Mock, patch

import pytest
import requests

from covalent_cloud.function_serve.assets import AssetsMediator
from covalent_cloud.function_serve.common import ServeAssetType
from covalent_cloud.function_serve.models import ServeAsset
from covalent_cloud.shared.classes.settings import AuthSettings, Settings


class TestAssetsMediator:
    """Tests for the AssetsMediator class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_settings = Settings(
            auth=AuthSettings(
                dr_api_token="test-dr-token",
            )
        )
        
        self.mock_legacy_settings = Settings(
            auth=AuthSettings(
                api_key="test-api-key",
            )
        )
        
        self.expected_auth_headers = {
            "Authorization": "Bearer test-dr-token",
            "x-dr-region": "",
        }
        
        self.expected_legacy_auth_headers = {
            "x-api-key": "test-api-key",
        }

    @patch("covalent_cloud.function_serve.assets.requests.Session")
    @patch("covalent_cloud.function_serve.assets.APIClient")
    def test_upload_asset_with_auth_headers_json_type(self, mock_api_client_class, mock_session_class):
        """Test uploading a JSON type asset includes auth headers"""
        # Setup mocks
        mock_api_client = Mock()
        mock_api_client.get_global_headers.return_value = self.expected_auth_headers
        mock_api_client_class.return_value = mock_api_client
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create a test ServeAsset
        test_asset = ServeAsset(
            type=ServeAssetType.JSON,
            serialized_object=b'{"test": "data"}',
            url="https://example.com/upload/test-asset"
        )
        
        # Store original values before they get cleared
        original_url = test_asset.url
        original_data = test_asset.serialized_object
        
        # Call the function
        with patch("covalent_cloud.function_serve.assets.settings", self.mock_settings):
            AssetsMediator.upload_asset(test_asset, self.mock_settings)
        
        # Verify APIClient was created with dummy URI and settings
        mock_api_client_class.assert_called_once_with("http://dummy", settings=self.mock_settings)
        mock_api_client.get_global_headers.assert_called_once()
        
        # Verify session.put was called with auth headers
        mock_session.put.assert_called_once_with(
            original_url, 
            headers=self.expected_auth_headers, 
            data=original_data
        )
        
        # Verify response was checked
        mock_response.raise_for_status.assert_called_once()
        
        # Verify asset fields were cleared after upload
        assert test_asset.url is None
        assert test_asset.serialized_object is None

    @patch("covalent_cloud.function_serve.assets.requests.Session")
    @patch("covalent_cloud.function_serve.assets.APIClient")
    @patch("covalent_cloud.function_serve.assets.ct.TransportableObject")
    def test_upload_asset_with_auth_headers_asset_type(self, mock_transportable_object_class, mock_api_client_class, mock_session_class):
        """Test uploading an ASSET type includes auth headers"""
        # Setup mocks
        mock_api_client = Mock()
        mock_api_client.get_global_headers.return_value = self.expected_auth_headers
        mock_api_client_class.return_value = mock_api_client
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Mock TransportableObject
        mock_transportable_obj = Mock()
        mock_serialized_data = b'serialized_asset_data'
        mock_transportable_obj.serialize.return_value = mock_serialized_data
        mock_transportable_object_class.deserialize.return_value = mock_transportable_obj
        
        # Create a test ServeAsset
        test_asset = ServeAsset(
            type=ServeAssetType.ASSET,
            serialized_object="mock_serialized_transportable_object",
            url="https://example.com/upload/test-asset"
        )
        
        # Store original values before they get cleared
        original_url = test_asset.url
        original_serialized_object = test_asset.serialized_object
        
        # Call the function
        with patch("covalent_cloud.function_serve.assets.settings", self.mock_settings):
            AssetsMediator.upload_asset(test_asset, self.mock_settings)
        
        # Verify APIClient was created and headers were retrieved
        mock_api_client_class.assert_called_once_with("http://dummy", settings=self.mock_settings)
        mock_api_client.get_global_headers.assert_called_once()
        
        # Verify TransportableObject was deserialized and serialized
        mock_transportable_object_class.deserialize.assert_called_once_with(original_serialized_object)
        mock_transportable_obj.serialize.assert_called_once()
        
        # Verify session.put was called with auth headers and serialized data
        mock_session.put.assert_called_once_with(
            original_url, 
            headers=self.expected_auth_headers, 
            data=mock_serialized_data
        )

    @patch("covalent_cloud.function_serve.assets.requests.Session")
    @patch("covalent_cloud.function_serve.assets.APIClient")
    def test_upload_asset_with_legacy_auth_headers(self, mock_api_client_class, mock_session_class):
        """Test uploading with legacy API key authentication"""
        # Setup mocks
        mock_api_client = Mock()
        mock_api_client.get_global_headers.return_value = self.expected_legacy_auth_headers
        mock_api_client_class.return_value = mock_api_client
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create a test ServeAsset
        test_asset = ServeAsset(
            type=ServeAssetType.JSON,
            serialized_object=b'{"test": "data"}',
            url="https://example.com/upload/test-asset"
        )
        
        # Store original values before they get cleared
        original_url = test_asset.url
        original_data = test_asset.serialized_object
        
        # Call the function with legacy settings
        with patch("covalent_cloud.function_serve.assets.settings", self.mock_legacy_settings):
            AssetsMediator.upload_asset(test_asset, self.mock_legacy_settings)
        
        # Verify APIClient was created with legacy settings
        mock_api_client_class.assert_called_once_with("http://dummy", settings=self.mock_legacy_settings)
        mock_api_client.get_global_headers.assert_called_once()
        
        # Verify session.put was called with legacy auth headers
        mock_session.put.assert_called_once_with(
            original_url, 
            headers=self.expected_legacy_auth_headers, 
            data=original_data
        )

    @patch("covalent_cloud.function_serve.assets.requests.Session")
    @patch("covalent_cloud.function_serve.assets.APIClient")
    @patch("covalent_cloud.function_serve.assets.get_deployment_client")
    def test_upload_asset_with_none_url_gets_presigned_url(self, mock_get_deployment_client, mock_api_client_class, mock_session_class):
        """Test that when URL is None, a presigned URL is obtained from deployment client"""
        # Setup mocks
        mock_api_client = Mock()
        mock_api_client.get_global_headers.return_value = self.expected_auth_headers
        mock_api_client_class.return_value = mock_api_client
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Mock deployment client response
        mock_deployment_client = Mock()
        mock_presigned_response = Mock()
        mock_presigned_response.json.return_value = [{"url": "https://presigned.url/upload", "id": "asset-id-123"}]
        mock_deployment_client.post.return_value = mock_presigned_response
        mock_get_deployment_client.return_value = mock_deployment_client
        
        # Create a test ServeAsset with no URL
        test_asset = ServeAsset(
            type=ServeAssetType.JSON,
            serialized_object=b'{"test": "data"}',
            url=None  # No URL provided
        )
        
        # Store original data before it gets cleared
        original_data = test_asset.serialized_object
        
        # Call the function
        with patch("covalent_cloud.function_serve.assets.settings", self.mock_settings):
            AssetsMediator.upload_asset(test_asset, self.mock_settings)
        
        # Verify deployment client was used to get presigned URL
        mock_get_deployment_client.assert_called_once_with(self.mock_settings)
        mock_deployment_client.post.assert_called_once_with("/assets")
        mock_presigned_response.json.assert_called_once()
        
        # Verify auth headers were still included in the upload
        mock_session.put.assert_called_once_with(
            "https://presigned.url/upload",  # The presigned URL
            headers=self.expected_auth_headers, 
            data=original_data
        )

    @patch("covalent_cloud.function_serve.assets.requests.Session")
    @patch("covalent_cloud.function_serve.assets.APIClient")
    def test_upload_asset_http_error_propagates(self, mock_api_client_class, mock_session_class):
        """Test that HTTP errors are properly propagated"""
        # Setup mocks
        mock_api_client = Mock()
        mock_api_client.get_global_headers.return_value = self.expected_auth_headers
        mock_api_client_class.return_value = mock_api_client
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Upload failed")
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create a test ServeAsset
        test_asset = ServeAsset(
            type=ServeAssetType.JSON,
            serialized_object=b'{"test": "data"}',
            url="https://example.com/upload/test-asset"
        )
        
        # Store original values before they might get cleared
        original_url = test_asset.url
        original_data = test_asset.serialized_object
        
        # Call the function and expect HTTPError to be raised
        with patch("covalent_cloud.function_serve.assets.settings", self.mock_settings):
            with pytest.raises(requests.exceptions.HTTPError):
                AssetsMediator.upload_asset(test_asset, self.mock_settings)
        
        # Verify that auth headers were still included in the failed request
        mock_session.put.assert_called_once_with(
            original_url, 
            headers=self.expected_auth_headers, 
            data=original_data
        )

    def test_upload_asset_unsupported_type_raises_error(self):
        """Test that unsupported asset types raise ValueError"""
        # Create a test ServeAsset with unsupported type
        test_asset = ServeAsset(
            type="UNSUPPORTED_TYPE",  # Invalid type
            serialized_object=b'{"test": "data"}',
            url="https://example.com/upload/test-asset"
        )
        
        # Call the function and expect ValueError to be raised
        with pytest.raises(ValueError, match="Unsupported asset type: 'UNSUPPORTED_TYPE'"):
            AssetsMediator.upload_asset(test_asset, self.mock_settings)

    @patch("covalent_cloud.function_serve.assets.requests.Session")
    @patch("covalent_cloud.function_serve.assets.APIClient")
    def test_upload_asset_retry_configuration(self, mock_api_client_class, mock_session_class):
        """Test that retry strategy is properly configured"""
        # Setup mocks
        mock_api_client = Mock()
        mock_api_client.get_global_headers.return_value = self.expected_auth_headers
        mock_api_client_class.return_value = mock_api_client
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create a test ServeAsset
        test_asset = ServeAsset(
            type=ServeAssetType.JSON,
            serialized_object=b'{"test": "data"}',
            url="https://example.com/upload/test-asset"
        )
        
        # Call the function
        with patch("covalent_cloud.function_serve.assets.settings", self.mock_settings):
            AssetsMediator.upload_asset(test_asset, self.mock_settings)
        
        # Verify session mount was called for both HTTP and HTTPS with retry strategy
        assert mock_session.mount.call_count == 2
        mount_calls = [call[0] for call in mock_session.mount.call_args_list]
        protocols = [call[0] for call in mount_calls]
        assert "https://" in protocols
        assert "http://" in protocols