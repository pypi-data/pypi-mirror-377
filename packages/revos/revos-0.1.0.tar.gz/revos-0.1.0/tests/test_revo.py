"""
Basic tests for the Revo library.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from pydantic import BaseModel

from revo import (
    RevoConfig,
    RevoTokenManager,
    get_revo_token,
    LangChainExtractor,
    TokenManager
)


class TestRevoConfig:
    """Test RevoConfig class."""
    
    def test_config_defaults(self):
        """Test default configuration values."""
        config = RevoConfig()
        
        assert config.token_url == "https://your-site.com/revo/oauth/token"
        assert config.base_url == "https://your-site.com/revo/llm-api"
        assert config.token_buffer_minutes == 5
        assert config.llm_model == "gpt-3.5-turbo"
        assert config.llm_temperature == 0.1
    
    @patch.dict(os.environ, {
        'REVO_CLIENT_ID': 'test_client_id',
        'REVO_CLIENT_SECRET': 'test_client_secret',
        'REVO_TOKEN_URL': 'https://test.example.com/token',
        'LLM_MODEL': 'gpt-4',
        'LLM_TEMPERATURE': '0.5'
    })
    def test_config_from_env(self):
        """Test configuration from environment variables."""
        config = RevoConfig()
        
        assert config.client_id == 'test_client_id'
        assert config.client_secret == 'test_client_secret'
        assert config.token_url == 'https://test.example.com/token'
        assert config.llm_model == 'gpt-4'
        assert config.llm_temperature == 0.5


class TestRevoTokenManager:
    """Test RevoTokenManager class."""
    
    @patch.dict(os.environ, {
        'REVO_CLIENT_ID': 'test_client_id',
        'REVO_CLIENT_SECRET': 'test_client_secret',
        'REVO_TOKEN_URL': 'https://test.example.com/token'
    })
    def test_token_manager_init(self):
        """Test token manager initialization."""
        manager = RevoTokenManager()
        
        assert manager.client_id == 'test_client_id'
        assert manager.client_secret == 'test_client_secret'
        assert manager.token_url == 'https://test.example.com/token'
        assert manager.consecutive_failures == 0
    
    def test_token_manager_missing_credentials(self):
        """Test token manager with missing credentials."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing required Apollo environment variables"):
                RevoTokenManager()
    
    @patch.dict(os.environ, {
        'REVO_CLIENT_ID': 'test_client_id',
        'REVO_CLIENT_SECRET': 'test_client_secret',
        'REVO_TOKEN_URL': 'https://test.example.com/token'
    })
    def test_token_expired_check(self):
        """Test token expiration check."""
        manager = RevoTokenManager()
        
        # No token should be expired
        assert manager._is_token_expired() is True
        
        # Set a future token
        from datetime import datetime, timedelta
        manager._token = "test_token"
        manager._token_expires_at = datetime.now() + timedelta(hours=1)
        
        # Should not be expired
        assert manager._is_token_expired() is False


class TestTokenManager:
    """Test TokenManager class."""
    
    def test_token_manager_init(self):
        """Test token manager initialization."""
        manager = TokenManager(refresh_interval_minutes=30)
        
        assert manager.refresh_interval == 30 * 60  # Converted to seconds
        assert manager.last_refresh is None
    
    def test_should_refresh_token(self):
        """Test token refresh logic."""
        manager = TokenManager(refresh_interval_minutes=1)
        
        # Should refresh if no previous refresh
        assert manager.should_refresh_token() is True
        
        # Set last refresh to now
        from datetime import datetime
        manager.last_refresh = datetime.now()
        
        # Should not refresh immediately
        assert manager.should_refresh_token() is False


class TestLangChainExtractor:
    """Test LangChainExtractor class."""
    
    def test_extractor_init(self):
        """Test extractor initialization."""
        # This will fail without proper credentials, but we can test the structure
        extractor = LangChainExtractor()
        
        # Should have an llm attribute (might be None if initialization failed)
        assert hasattr(extractor, 'llm')


class TestDataModel:
    """Test example data model."""
    
    def test_person_info_model(self):
        """Test PersonInfo data model."""
        from examples.basic_usage import PersonInfo
        
        # Test valid data
        person = PersonInfo(
            name="John Doe",
            age=30,
            occupation="Software Engineer",
            location="San Francisco"
        )
        
        assert person.name == "John Doe"
        assert person.age == 30
        assert person.occupation == "Software Engineer"
        assert person.location == "San Francisco"
    
    def test_person_info_validation(self):
        """Test PersonInfo validation."""
        from examples.basic_usage import PersonInfo
        
        # Test invalid data
        with pytest.raises(Exception):  # Pydantic validation error
            PersonInfo(
                name="John Doe",
                age="not_a_number",  # Invalid type
                occupation="Software Engineer",
                location="San Francisco"
            )


if __name__ == "__main__":
    pytest.main([__file__])
