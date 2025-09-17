"""
Tests for authentication functionality.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from revos.auth.core import RevosTokenManager
from revos.auth.exceptions import RevosAuthenticationError, RevosAPIError
from revos.auth.tokens import get_revos_token, invalidate_revos_token


class TestRevosTokenManager:
    """Test cases for RevosTokenManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.settings_mock = Mock()
        self.settings_mock.revos.client_id = "test-client-id"
        self.settings_mock.revos.client_secret = "test-client-secret"
        self.settings_mock.revos.token_url = "https://test.com/oauth/token"
        self.settings_mock.revos.base_url = "https://test.com/api"
        self.settings_mock.revos.token_buffer_minutes = 5
        self.settings_mock.revos.max_retries = 3
        self.settings_mock.revos.request_timeout = 30
        
        # Add token_manager config
        self.settings_mock.token_manager.max_failures_before_fallback = 1
        
        with patch('revos.auth.core.get_settings', return_value=self.settings_mock):
            self.token_manager = RevosTokenManager()
    
    def test_init(self):
        """Test RevosTokenManager initialization."""
        assert self.token_manager._token is None
        assert self.token_manager._token_expires_at is None
        assert self.token_manager.consecutive_failures == 0
        assert self.token_manager.max_failures_before_fallback == 1
        assert self.token_manager._buffer_minutes == 5
    
    def test_invalidate_token(self):
        """Test token invalidation."""
        # Set some initial state
        self.token_manager._token = "test-token"
        self.token_manager._token_expires_at = datetime.now() + timedelta(hours=1)
        self.token_manager.consecutive_failures = 2
        
        # Invalidate token
        self.token_manager.invalidate_token()
        
        # Check state is reset
        assert self.token_manager._token is None
        assert self.token_manager._token_expires_at is None
        assert self.token_manager.consecutive_failures == 0
    
    @patch('requests.post')
    def test_fetch_new_token_success(self, mock_post):
        """Test successful token fetch."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test-access-token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        mock_post.return_value = mock_response
        
        # Fetch token
        result = self.token_manager._fetch_new_token()
        
        # Verify result
        assert result["access_token"] == "test-access-token"
        assert result["expires_in"] == 3600
        assert result["token_type"] == "Bearer"
        
        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://test.com/oauth/token"  # First positional arg is URL
        assert call_args[1]["data"]["client_id"] == "test-client-id"
        assert call_args[1]["data"]["client_secret"] == "test-client-secret"
    
    @patch('requests.post')
    def test_fetch_new_token_failure(self, mock_post):
        """Test token fetch failure."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = Exception("Unauthorized")
        mock_post.return_value = mock_response
        
        # Attempt to fetch token
        with pytest.raises(Exception):
            self.token_manager._fetch_new_token()
    
    @patch('httpx.Client')
    def test_fetch_new_token_fallback_success(self, mock_client_class):
        """Test successful fallback token fetch."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test-fallback-token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        
        # Mock the client context manager
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Fetch token using fallback
        result = self.token_manager._fetch_new_token_fallback()
        
        # Verify result
        assert result["access_token"] == "test-fallback-token"
        assert result["expires_in"] == 3600
    
    def test_get_token_no_token(self):
        """Test getting token when none exists."""
        with patch.object(self.token_manager, '_fetch_and_update_token') as mock_fetch:
            mock_fetch.return_value = None
            self.token_manager._token = "test-token"
            
            result = self.token_manager.get_token(force_refresh=True)
            
            assert result == "test-token"
            mock_fetch.assert_called_once_with(False)
    
    def test_get_token_expired(self):
        """Test getting token when current token is expired."""
        # Set expired token
        self.token_manager._token = "expired-token"
        self.token_manager._token_expires_at = datetime.now() - timedelta(minutes=1)
        
        with patch.object(self.token_manager, '_fetch_and_update_token') as mock_fetch:
            mock_fetch.return_value = None
            
            result = self.token_manager.get_token()
            
            assert result == "expired-token"
            mock_fetch.assert_called_once_with(False)
    
    def test_get_token_valid(self):
        """Test getting token when current token is valid."""
        # Set valid token
        self.token_manager._token = "valid-token"
        self.token_manager._token_expires_at = datetime.now() + timedelta(hours=1)
        
        result = self.token_manager.get_token()
        
        assert result == "valid-token"
    
    @patch.object(RevosTokenManager, '_fetch_new_token')
    def test_fetch_and_update_token_success(self, mock_fetch):
        """Test successful token fetch and update."""
        # Mock successful token fetch
        mock_fetch.return_value = {
            "access_token": "new-token",
            "expires_in": 3600
        }
        
        # Fetch and update token
        self.token_manager._fetch_and_update_token()
        
        # Verify token was updated
        assert self.token_manager._token == "new-token"
        assert self.token_manager._token_expires_at is not None
        assert self.token_manager.consecutive_failures == 0
    
    @patch.object(RevosTokenManager, '_fetch_new_token')
    def test_fetch_and_update_token_failure_with_fallback(self, mock_fetch):
        """Test token fetch failure with fallback success."""
        # Mock original method failure
        mock_fetch.side_effect = Exception("Original method failed")
        
        # Mock fallback success
        with patch.object(self.token_manager, '_fetch_new_token_fallback') as mock_fallback:
            mock_fallback.return_value = {
                "access_token": "fallback-token",
                "expires_in": 3600
            }
            
            # Set up for fallback
            self.token_manager.consecutive_failures = 1
            self.token_manager.max_failures_before_fallback = 1
            
            # Fetch and update token
            self.token_manager._fetch_and_update_token()
            
            # Verify fallback token was used
            assert self.token_manager._token == "fallback-token"
            mock_fallback.assert_called_once()


class TestTokenFunctions:
    """Test cases for token utility functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Clear any existing token manager
        with patch('revos.auth.tokens._token_manager', None):
            pass
    
    @patch('revos.auth.tokens._token_manager')
    def test_get_revos_token(self, mock_token_manager):
        """Test get_revos_token function."""
        mock_token_manager.get_token.return_value = "test-token"
        
        result = get_revos_token()
        
        assert result == "test-token"
        mock_token_manager.get_token.assert_called_once_with(
            force_refresh=False, 
            use_fallback=False
        )
    
    @patch('revos.auth.tokens._token_manager')
    def test_get_revos_token_with_params(self, mock_token_manager):
        """Test get_revos_token function with parameters."""
        mock_token_manager.get_token.return_value = "test-token"
        
        result = get_revos_token(force_refresh=True, use_fallback=True)
        
        assert result == "test-token"
        mock_token_manager.get_token.assert_called_once_with(
            force_refresh=True, 
            use_fallback=True
        )
    
    @patch('revos.auth.tokens._token_manager')
    def test_invalidate_revos_token(self, mock_token_manager):
        """Test invalidate_revos_token function."""
        invalidate_revos_token()
        
        mock_token_manager.invalidate_token.assert_called_once()


class TestExceptions:
    """Test cases for custom exceptions."""
    
    def test_revo_authentication_error(self):
        """Test RevosAuthenticationError exception."""
        error = RevosAuthenticationError("Authentication failed")
        assert str(error) == "Authentication failed"
        assert isinstance(error, Exception)
    
    def test_revo_api_error(self):
        """Test RevosAPIError exception."""
        error = RevosAPIError("API call failed")
        assert str(error) == "API call failed"
        assert isinstance(error, Exception)
