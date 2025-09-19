# Copyright 2024 Agnostiq Inc.

"""Integration tests for asset upload authentication"""

import os
import tempfile
from unittest.mock import Mock, patch

import requests

from covalent_cloud.dispatch_management.helpers import _upload_asset
from covalent_cloud.function_serve.assets import AssetsMediator
from covalent_cloud.function_serve.common import ServeAssetType
from covalent_cloud.function_serve.models import ServeAsset
from covalent_cloud.shared.classes.settings import AuthSettings, Settings


class TestAssetUploadAuthIntegration:
    """Integration tests to verify auth headers are included in asset uploads"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_settings = Settings(
            auth=AuthSettings(
                dr_api_token="integration-test-token",
            )
        )

    @patch("covalent_cloud.dispatch_management.helpers.requests.Session")
    def test_dispatch_upload_includes_auth_headers_integration(self, mock_session_class):
        """Integration test: verify dispatch_management _upload_asset includes auth headers end-to-end"""
        # Mock the session and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test file content")
            temp_file_path = temp_file.name
            
        try:
            # Call the actual _upload_asset function with real settings
            with patch("covalent_cloud.dispatch_management.helpers.settings", self.mock_settings):
                _upload_asset(
                    f"file://{temp_file_path}", 
                    "https://test-upload-endpoint.com/file", 
                    Mock(), 
                    Mock()
                )
            
            # Verify the PUT request was made with auth headers
            mock_session.put.assert_called_once()
            call_args = mock_session.put.call_args
            
            # Check that headers were provided and contain auth info
            assert "headers" in call_args[1]
            headers = call_args[1]["headers"]
            
            # Should contain either Bearer token or API key
            has_bearer_auth = "Authorization" in headers and headers["Authorization"].startswith("Bearer")
            has_api_key_auth = "x-api-key" in headers
            
            assert has_bearer_auth or has_api_key_auth, f"Missing auth headers in: {headers}"
            
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    @patch("covalent_cloud.function_serve.assets.requests.Session")
    def test_function_serve_upload_includes_auth_headers_integration(self, mock_session_class):
        """Integration test: verify function_serve asset upload includes auth headers end-to-end"""
        # Mock the session and response
        mock_session = Mock()
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create a test asset
        test_asset = ServeAsset(
            type=ServeAssetType.JSON,
            serialized_object=b'{"integration": "test"}',
            url="https://test-upload-endpoint.com/serve-asset"
        )
        
        # Call the actual AssetsMediator.upload_asset function
        with patch("covalent_cloud.function_serve.assets.settings", self.mock_settings):
            AssetsMediator.upload_asset(test_asset, self.mock_settings)
        
        # Verify the PUT request was made with auth headers
        mock_session.put.assert_called_once()
        call_args = mock_session.put.call_args
        
        # Check that headers were provided and contain auth info
        assert "headers" in call_args[1]
        headers = call_args[1]["headers"]
        
        # Should contain either Bearer token or API key
        has_bearer_auth = "Authorization" in headers and headers["Authorization"].startswith("Bearer")
        has_api_key_auth = "x-api-key" in headers
        
        assert has_bearer_auth or has_api_key_auth, f"Missing auth headers in: {headers}"

    @patch("covalent_cloud.dispatch_management.helpers.requests.Session")
    def test_auth_headers_consistent_between_modules(self, mock_session_class):
        """Integration test: verify both modules use the same auth header format"""
        # Mock the session and response for dispatch management
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Test dispatch management headers
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test")
            temp_file_path = temp_file.name
            
        try:
            with patch("covalent_cloud.dispatch_management.helpers.settings", self.mock_settings):
                _upload_asset(
                    f"file://{temp_file_path}", 
                    "https://test.com/dispatch", 
                    Mock(), 
                    Mock()
                )
            
            # Get headers from dispatch management call
            dispatch_headers = mock_session.put.call_args[1]["headers"]
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        # Reset mock for function serve test
        mock_session.reset_mock()
        
        # Test function serve headers  
        with patch("covalent_cloud.function_serve.assets.requests.Session") as mock_serve_session_class:
            mock_serve_session = Mock()
            mock_serve_response = Mock()
            mock_serve_response.raise_for_status = Mock()
            mock_serve_session.put.return_value = mock_serve_response
            mock_serve_session_class.return_value = mock_serve_session
            
            test_asset = ServeAsset(
                type=ServeAssetType.JSON,
                serialized_object=b'{"test": "data"}',
                url="https://test.com/serve"
            )
            
            with patch("covalent_cloud.function_serve.assets.settings", self.mock_settings):
                AssetsMediator.upload_asset(test_asset, self.mock_settings)
            
            # Get headers from function serve call
            serve_headers = mock_serve_session.put.call_args[1]["headers"]
        
        # Verify both modules use the same auth headers
        assert dispatch_headers == serve_headers, (
            f"Auth headers differ between modules: "
            f"dispatch={dispatch_headers}, serve={serve_headers}"
        )

    def test_auth_header_types_with_different_settings(self):
        """Integration test: verify different settings produce appropriate auth headers"""
        
        # Test modern DR token settings
        dr_settings = Settings(auth=AuthSettings(dr_api_token="dr-test-token"))
        
        # Test legacy API key settings  
        api_key_settings = Settings(auth=AuthSettings(api_key="api-key-test"))
        
        with patch("covalent_cloud.dispatch_management.helpers.requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status_code = requests.codes.ok
            mock_session.put.return_value = mock_response
            mock_session_class.return_value = mock_session
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(b"test")
                temp_file_path = temp_file.name
            
            try:
                # Test DR token produces Bearer auth
                with patch("covalent_cloud.dispatch_management.helpers.settings", dr_settings):
                    _upload_asset(f"file://{temp_file_path}", "https://test.com/dr", Mock(), Mock())
                
                dr_headers = mock_session.put.call_args[1]["headers"]
                assert "Authorization" in dr_headers
                assert dr_headers["Authorization"].startswith("Bearer")
                
                # Reset mock
                mock_session.reset_mock()
                
                # Test API key produces x-api-key auth
                with patch("covalent_cloud.dispatch_management.helpers.settings", api_key_settings):
                    _upload_asset(f"file://{temp_file_path}", "https://test.com/api", Mock(), Mock())
                
                api_key_headers = mock_session.put.call_args[1]["headers"]
                assert "x-api-key" in api_key_headers
                
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)