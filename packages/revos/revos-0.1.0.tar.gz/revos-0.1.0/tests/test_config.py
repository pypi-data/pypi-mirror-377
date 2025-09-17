"""
Tests for configuration functionality.
"""

import pytest
import os
import tempfile
import yaml
import json
from unittest.mock import patch, Mock

from revo.config.main import RevoMainConfig, get_settings, load_config_from_file
from revo.config.api import RevoConfig
from revo.config.llm import LLMConfig
from revo.config.llm_models import LLMModelConfig, LLMModelsConfig
from revo.config.logging import LoggingConfig
from revo.config.token import TokenManagerConfig
from revo.config.factory import (
    create_config_with_prefixes,
    create_minimal_config,
    create_development_config,
    create_production_config
)


class TestRevoConfig:
    """Test cases for RevoConfig."""
    
    def test_init_with_required_fields(self):
        """Test RevoConfig initialization with required fields."""
        config = RevoConfig(
            client_id="test-client-id",
            client_secret="test-client-secret"
        )
        
        assert config.client_id == "test-client-id"
        assert config.client_secret == "test-client-secret"
        assert config.token_url == "https://your-site.com/revo/oauth/token"
        assert config.base_url == "https://your-site.com/revo/llm-api"
    
    def test_init_with_custom_urls(self):
        """Test RevoConfig initialization with custom URLs."""
        config = RevoConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
            token_url="https://custom.com/oauth/token",
            base_url="https://custom.com/api"
        )
        
        assert config.token_url == "https://custom.com/oauth/token"
        assert config.base_url == "https://custom.com/api"


class TestLLMConfig:
    """Test cases for LLMConfig."""
    
    def test_init_with_defaults(self):
        """Test LLMConfig initialization with defaults."""
        config = LLMConfig()
        
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.1
        assert config.max_tokens is None
        assert config.top_p == 1.0
        assert config.frequency_penalty == 0.0
        assert config.presence_penalty == 0.0
    
    def test_init_with_custom_values(self):
        """Test LLMConfig initialization with custom values."""
        config = LLMConfig(
            model="gpt-4",
            temperature=0.8,
            max_tokens=2000,
            top_p=0.9,
            frequency_penalty=0.3,
            presence_penalty=0.3
        )
        
        assert config.model == "gpt-4"
        assert config.temperature == 0.8
        assert config.max_tokens == 2000
        assert config.top_p == 0.9
        assert config.frequency_penalty == 0.3
        assert config.presence_penalty == 0.3


class TestLLMModelConfig:
    """Test cases for LLMModelConfig."""
    
    def test_init_with_required_fields(self):
        """Test LLMModelConfig initialization with required fields."""
        config = LLMModelConfig(
            model="gpt-4",
            description="Test model"
        )
        
        assert config.model == "gpt-4"
        assert config.description == "Test model"
        assert config.temperature == 0.1  # Default value
        assert config.custom_params == {}  # Default value
    
    def test_init_with_all_fields(self):
        """Test LLMModelConfig initialization with all fields."""
        config = LLMModelConfig(
            model="gpt-4",
            temperature=0.8,
            max_tokens=2000,
            description="Creative model",
            custom_params={"test": "value"}
        )
        
        assert config.model == "gpt-4"
        assert config.temperature == 0.8
        assert config.max_tokens == 2000
        assert config.description == "Creative model"
        assert config.custom_params == {"test": "value"}


class TestLLMModelsConfig:
    """Test cases for LLMModelsConfig."""
    
    def test_init_with_defaults(self):
        """Test LLMModelsConfig initialization with defaults."""
        config = LLMModelsConfig()
        
        assert "gpt-3.5-turbo" in config.models
        assert "gpt-4" in config.models
        assert "gpt-4-turbo" in config.models
        assert "claude-3" in config.models
    
    def test_get_model_existing(self):
        """Test getting an existing model."""
        config = LLMModelsConfig()
        
        model = config.get_model("gpt-4")
        
        assert model.model == "gpt-4"
        assert isinstance(model, LLMModelConfig)
    
    def test_get_model_nonexistent(self):
        """Test getting a non-existent model."""
        config = LLMModelsConfig()
        
        with pytest.raises(ValueError, match="Model 'nonexistent' not found"):
            config.get_model("nonexistent")
    
    def test_list_available_models(self):
        """Test listing available models."""
        config = LLMModelsConfig()
        
        models = config.list_available_models()
        
        assert isinstance(models, dict)
        assert "gpt-3.5-turbo" in models
        assert "gpt-4" in models
        assert len(models) == 4
    
    def test_add_model(self):
        """Test adding a new model."""
        config = LLMModelsConfig()
        new_model = LLMModelConfig(
            model="custom-model",
            description="Custom model for testing"
        )
        
        config.add_model("custom", new_model)
        
        assert "custom" in config.models
        assert config.get_model("custom").model == "custom-model"
    
    def test_remove_model(self):
        """Test removing a model."""
        config = LLMModelsConfig()
        initial_count = len(config.models)
        
        config.remove_model("claude-3")
        
        assert len(config.models) == initial_count - 1
        assert "claude-3" not in config.models


class TestLoggingConfig:
    """Test cases for LoggingConfig."""
    
    def test_init_with_defaults(self):
        """Test LoggingConfig initialization with defaults."""
        config = LoggingConfig()
        
        assert config.level == "INFO"
        assert config.format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert config.file is None
        assert config.max_size == 10485760  # 10MB
        assert config.backup_count == 5
    
    def test_init_with_custom_values(self):
        """Test LoggingConfig initialization with custom values."""
        config = LoggingConfig(
            level="DEBUG",
            format="%(levelname)s: %(message)s",
            file="/tmp/test.log",
            max_size=5242880,  # 5MB
            backup_count=3
        )
        
        assert config.level == "DEBUG"
        assert config.format == "%(levelname)s: %(message)s"
        assert config.file == "/tmp/test.log"
        assert config.max_size == 5242880
        assert config.backup_count == 3


class TestTokenManagerConfig:
    """Test cases for TokenManagerConfig."""
    
    def test_init_with_defaults(self):
        """Test TokenManagerConfig initialization with defaults."""
        config = TokenManagerConfig()
        
        assert config.refresh_interval_minutes == 45
        assert config.max_failures_before_fallback == 1
        assert config.enable_periodic_refresh is True
        assert config.enable_fallback is True
    
    def test_init_with_custom_values(self):
        """Test TokenManagerConfig initialization with custom values."""
        config = TokenManagerConfig(
            refresh_interval_minutes=30,
            max_failures_before_fallback=3,
            enable_periodic_refresh=False,
            enable_fallback=False
        )
        
        assert config.refresh_interval_minutes == 30
        assert config.max_failures_before_fallback == 3
        assert config.enable_periodic_refresh is False
        assert config.enable_fallback is False


class TestRevoMainConfig:
    """Test cases for RevoMainConfig."""
    
    def test_init_with_defaults(self):
        """Test RevoMainConfig initialization with defaults."""
        with patch.dict(os.environ, {
            'REVO_CLIENT_ID': 'test-client-id',
            'REVO_CLIENT_SECRET': 'test-client-secret'
        }):
            config = RevoMainConfig()
            
            assert config.revo.client_id == "test-client-id"
            assert config.revo.client_secret == "test-client-secret"
            assert isinstance(config.llm, LLMConfig)
            assert isinstance(config.llm_models, LLMModelsConfig)
            assert isinstance(config.logging, LoggingConfig)
            assert isinstance(config.token_manager, TokenManagerConfig)
    
    def test_init_with_custom_values(self):
        """Test RevoMainConfig initialization with custom values."""
        config = RevoMainConfig(
            revo={
                "client_id": "custom-client-id",
                "client_secret": "custom-client-secret"
            },
            llm={
                "model": "gpt-4",
                "temperature": 0.8
            }
        )
        
        assert config.revo.client_id == "custom-client-id"
        assert config.revo.client_secret == "custom-client-secret"
        assert config.llm.model == "gpt-4"
        assert config.llm.temperature == 0.8


class TestConfigFactory:
    """Test cases for configuration factory functions."""
    
    def test_create_config_with_prefixes(self):
        """Test create_config_with_prefixes function."""
        config = create_config_with_prefixes(
            revo_prefix="CUSTOM_REVO_",
            llm_prefix="CUSTOM_LLM_",
            revo={
                "client_id": "test-client-id",
                "client_secret": "test-client-secret"
            }
        )
        
        assert isinstance(config, RevoMainConfig)
        # The function should work without errors
    
    def test_create_minimal_config(self):
        """Test create_minimal_config function."""
        config = create_minimal_config(
            client_id="minimal-client-id",
            client_secret="minimal-client-secret"
        )
        
        assert isinstance(config, RevoMainConfig)
        assert config.revo.client_id == "minimal-client-id"
        assert config.revo.client_secret == "minimal-client-secret"
    
    def test_create_development_config(self):
        """Test create_development_config function."""
        config = create_development_config(
            client_id="dev-client-id",
            client_secret="dev-client-secret"
        )
        
        assert isinstance(config, RevoMainConfig)
        assert config.revo.client_id == "dev-client-id"
        assert config.revo.client_secret == "dev-client-secret"
        assert config.logging.level == "DEBUG"
    
    def test_create_production_config(self):
        """Test create_production_config function."""
        config = create_production_config(
            client_id="prod-client-id",
            client_secret="prod-client-secret"
        )
        
        assert isinstance(config, RevoMainConfig)
        assert config.revo.client_id == "prod-client-id"
        assert config.revo.client_secret == "prod-client-secret"
        assert config.logging.level == "WARNING"


class TestConfigFileLoading:
    """Test cases for configuration file loading."""
    
    def test_load_yaml_config(self):
        """Test loading configuration from YAML file."""
        config_data = {
            "revo": {
                "client_id": "yaml-client-id",
                "client_secret": "yaml-client-secret"
            },
            "llm": {
                "model": "gpt-4",
                "temperature": 0.8
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_file = f.name
        
        try:
            config = RevoMainConfig.from_file(temp_file)
            
            assert config.revo.client_id == "yaml-client-id"
            assert config.revo.client_secret == "yaml-client-secret"
            assert config.llm.model == "gpt-4"
            assert config.llm.temperature == 0.8
        finally:
            os.unlink(temp_file)
    
    def test_load_json_config(self):
        """Test loading configuration from JSON file."""
        config_data = {
            "revo": {
                "client_id": "json-client-id",
                "client_secret": "json-client-secret"
            },
            "llm": {
                "model": "gpt-4",
                "temperature": 0.8
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name
        
        try:
            config = RevoMainConfig.from_file(temp_file)
            
            assert config.revo.client_id == "json-client-id"
            assert config.revo.client_secret == "json-client-secret"
            assert config.llm.model == "gpt-4"
            assert config.llm.temperature == 0.8
        finally:
            os.unlink(temp_file)
    
    def test_load_config_from_file_function(self):
        """Test load_config_from_file function."""
        config_data = {
            "revo": {
                "client_id": "function-client-id",
                "client_secret": "function-client-secret"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_file = f.name
        
        try:
            config = load_config_from_file(temp_file)
            
            assert isinstance(config, RevoMainConfig)
            assert config.revo.client_id == "function-client-id"
            assert config.revo.client_secret == "function-client-secret"
        finally:
            os.unlink(temp_file)


class TestSettings:
    """Test cases for global settings."""
    
    def test_get_settings(self):
        """Test get_settings function."""
        # Clear the global settings cache
        from revo.config.main import _settings
        import revo.config.main
        revo.config.main._settings = None
        
        with patch.dict(os.environ, {
            'REVO_CLIENT_ID': 'settings-client-id',
            'REVO_CLIENT_SECRET': 'settings-client-secret'
        }):
            settings = get_settings()
            
            assert isinstance(settings, RevoMainConfig)
            assert settings.revo.client_id == "settings-client-id"
            assert settings.revo.client_secret == "settings-client-secret"
    
    def test_get_settings_singleton(self):
        """Test that get_settings returns the same instance."""
        with patch.dict(os.environ, {
            'REVO_CLIENT_ID': 'singleton-client-id',
            'REVO_CLIENT_SECRET': 'singleton-client-secret'
        }):
            settings1 = get_settings()
            settings2 = get_settings()
            
            assert settings1 is settings2
