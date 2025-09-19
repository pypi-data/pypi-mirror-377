# Copyright 2023 Agnostiq Inc.

"""Unit tests for dispatch helpers"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest
import requests
from rich.progress import Progress

from covalent_cloud.dispatch_management.helpers import _upload_asset
from covalent_cloud.shared.classes.settings import AuthSettings, Settings


class TestUploadAsset:
    """Tests for the _upload_asset function"""

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

    @patch("covalent_cloud.dispatch_management.helpers.requests.Session")
    @patch("covalent_cloud.dispatch_management.helpers.APIClient")
    def test_upload_asset_empty_file_with_auth_headers(self, mock_api_client_class, mock_session_class):
        """Test uploading an empty file includes auth headers"""
        # Setup mocks
        mock_api_client = Mock()
        mock_api_client.get_global_headers.return_value = self.expected_auth_headers
        mock_api_client_class.return_value = mock_api_client
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create temporary empty file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            local_uri = f"file://{temp_file_path}"
            remote_uri = "https://example.com/upload"
            
            # Mock progress objects
            mock_task = Mock()
            mock_progress = Mock(spec=Progress)
            
            # Call the function
            with patch("covalent_cloud.dispatch_management.helpers.settings", self.mock_settings):
                _upload_asset(local_uri, remote_uri, mock_task, mock_progress)
            
            # Verify APIClient was created with dummy URI
            mock_api_client_class.assert_called_once_with("http://dummy", settings=self.mock_settings)
            mock_api_client.get_global_headers.assert_called_once()
            
            # Verify session.put was called with auth headers and Content-Length for empty file
            expected_headers = {**self.expected_auth_headers, "Content-Length": "0"}
            mock_session.put.assert_called_once_with(
                remote_uri, 
                headers=expected_headers, 
                data=""
            )
            
            # Verify progress was updated
            mock_progress.advance.assert_called_once_with(mock_task, advance=1)
            mock_progress.refresh.assert_called_once()
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    @patch("covalent_cloud.dispatch_management.helpers.requests.Session")
    @patch("covalent_cloud.dispatch_management.helpers.APIClient")
    def test_upload_asset_non_empty_file_with_auth_headers(self, mock_api_client_class, mock_session_class):
        """Test uploading a non-empty file includes auth headers"""
        # Setup mocks
        mock_api_client = Mock()
        mock_api_client.get_global_headers.return_value = self.expected_auth_headers
        mock_api_client_class.return_value = mock_api_client
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create temporary file with content
        test_content = b"test file content"
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            local_uri = f"file://{temp_file_path}"
            remote_uri = "https://example.com/upload"
            
            # Mock progress objects
            mock_task = Mock()
            mock_progress = Mock(spec=Progress)
            
            # Call the function
            with patch("covalent_cloud.dispatch_management.helpers.settings", self.mock_settings):
                _upload_asset(local_uri, remote_uri, mock_task, mock_progress)
            
            # Verify APIClient was created and headers were retrieved
            mock_api_client_class.assert_called_once_with("http://dummy", settings=self.mock_settings)
            mock_api_client.get_global_headers.assert_called_once()
            
            # Verify session.put was called with auth headers
            mock_session.put.assert_called_once()
            call_args = mock_session.put.call_args
            assert call_args[0][0] == remote_uri  # First positional arg is remote_uri
            assert call_args[1]["headers"] == self.expected_auth_headers  # headers kwarg
            
            # Verify progress was updated
            mock_progress.advance.assert_called_once_with(mock_task, advance=1)
            mock_progress.refresh.assert_called_once()
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    @patch("covalent_cloud.dispatch_management.helpers.requests.Session")
    @patch("covalent_cloud.dispatch_management.helpers.APIClient")
    def test_upload_asset_with_legacy_auth_headers(self, mock_api_client_class, mock_session_class):
        """Test uploading with legacy API key authentication"""
        # Setup mocks
        mock_api_client = Mock()
        mock_api_client.get_global_headers.return_value = self.expected_legacy_auth_headers
        mock_api_client_class.return_value = mock_api_client
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create temporary empty file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            local_uri = f"file://{temp_file_path}"
            remote_uri = "https://example.com/upload"
            
            # Mock progress objects
            mock_task = Mock()
            mock_progress = Mock(spec=Progress)
            
            # Call the function with legacy settings
            with patch("covalent_cloud.dispatch_management.helpers.settings", self.mock_legacy_settings):
                _upload_asset(local_uri, remote_uri, mock_task, mock_progress)
            
            # Verify APIClient was created with legacy settings
            mock_api_client_class.assert_called_once_with("http://dummy", settings=self.mock_legacy_settings)
            mock_api_client.get_global_headers.assert_called_once()
            
            # Verify session.put was called with legacy auth headers
            expected_headers = {**self.expected_legacy_auth_headers, "Content-Length": "0"}
            mock_session.put.assert_called_once_with(
                remote_uri, 
                headers=expected_headers, 
                data=""
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    @patch("covalent_cloud.dispatch_management.helpers.requests.Session")
    @patch("covalent_cloud.dispatch_management.helpers.APIClient")
    def test_upload_asset_without_file_prefix(self, mock_api_client_class, mock_session_class):
        """Test uploading when local_uri doesn't have file:// prefix"""
        # Setup mocks
        mock_api_client = Mock()
        mock_api_client.get_global_headers.return_value = self.expected_auth_headers
        mock_api_client_class.return_value = mock_api_client
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create temporary empty file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # Use local path directly without file:// prefix
            local_uri = temp_file_path
            remote_uri = "https://example.com/upload"
            
            # Mock progress objects
            mock_task = Mock()
            mock_progress = Mock(spec=Progress)
            
            # Call the function
            with patch("covalent_cloud.dispatch_management.helpers.settings", self.mock_settings):
                _upload_asset(local_uri, remote_uri, mock_task, mock_progress)
            
            # Verify auth headers were still included
            expected_headers = {**self.expected_auth_headers, "Content-Length": "0"}
            mock_session.put.assert_called_once_with(
                remote_uri, 
                headers=expected_headers, 
                data=""
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    @patch("covalent_cloud.dispatch_management.helpers.requests.Session")
    @patch("covalent_cloud.dispatch_management.helpers.APIClient")
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
        
        # Create temporary empty file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            local_uri = f"file://{temp_file_path}"
            remote_uri = "https://example.com/upload"
            
            # Mock progress objects
            mock_task = Mock()
            mock_progress = Mock(spec=Progress)
            
            # Call the function and expect HTTPError to be raised
            with patch("covalent_cloud.dispatch_management.helpers.settings", self.mock_settings):
                with pytest.raises(requests.exceptions.HTTPError):
                    _upload_asset(local_uri, remote_uri, mock_task, mock_progress)
            
            # Verify that auth headers were still included in the failed request
            expected_headers = {**self.expected_auth_headers, "Content-Length": "0"}
            mock_session.put.assert_called_once_with(
                remote_uri, 
                headers=expected_headers, 
                data=""
            )
            
            # Verify progress was not updated on failure
            mock_progress.advance.assert_not_called()
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    @patch("covalent_cloud.dispatch_management.helpers.requests.Session")
    @patch("covalent_cloud.dispatch_management.helpers.APIClient")
    def test_upload_asset_retry_configuration(self, mock_api_client_class, mock_session_class):
        """Test that retry strategy is properly configured"""
        # Setup mocks
        mock_api_client = Mock()
        mock_api_client.get_global_headers.return_value = self.expected_auth_headers
        mock_api_client_class.return_value = mock_api_client
        
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_session.put.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Create temporary empty file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            local_uri = f"file://{temp_file_path}"
            remote_uri = "https://example.com/upload"
            
            # Mock progress objects
            mock_task = Mock()
            mock_progress = Mock(spec=Progress)
            
            # Call the function
            with patch("covalent_cloud.dispatch_management.helpers.settings", self.mock_settings):
                _upload_asset(local_uri, remote_uri, mock_task, mock_progress)
            
            # Verify session mount was called for HTTPS with retry strategy
            mock_session.mount.assert_called()
            # Check that mount was called with HTTPAdapter
            mount_calls = mock_session.mount.call_args_list
            https_mount_found = any("https://" in str(call) for call in mount_calls)
            assert https_mount_found, "Expected HTTPS mount with retry strategy"
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)