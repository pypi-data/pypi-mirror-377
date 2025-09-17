"""
Main configuration class for the Revos library.

This module provides the main configuration class that combines
all configuration sections and provides utility methods for
loading and saving configurations.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .api import RevosConfig
from .llm import LLMConfig
from .llm_models import LLMModelsConfig
from .logging import LoggingConfig
from .token import TokenManagerConfig


class RevosMainConfig(BaseSettings):
    """Main configuration class for the Revos library."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Nested configuration sections
    revos: RevosConfig = Field(default_factory=RevosConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    llm_models: LLMModelsConfig = Field(default_factory=LLMModelsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    token_manager: TokenManagerConfig = Field(default_factory=TokenManagerConfig)
    
    def __init__(self, **kwargs):
        # Extract _env_file if provided
        env_file = kwargs.pop('_env_file', None)
        
        # If _env_file is provided, pass it to nested configurations
        if env_file:
            # Create nested configs with the same env file
            if 'revos' not in kwargs:
                kwargs['revos'] = RevosConfig(_env_file=env_file)
            if 'llm' not in kwargs:
                kwargs['llm'] = LLMConfig(_env_file=env_file)
            if 'llm_models' not in kwargs:
                kwargs['llm_models'] = LLMModelsConfig(_env_file=env_file)
            if 'logging' not in kwargs:
                kwargs['logging'] = LoggingConfig(_env_file=env_file)
            if 'token_manager' not in kwargs:
                kwargs['token_manager'] = TokenManagerConfig(_env_file=env_file)
        
        super().__init__(**kwargs)
    
    # Global settings
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    config_file: Optional[str] = Field(
        default=None,
        description="Path to configuration file"
    )
    
    @model_validator(mode='after')
    def validate_config(self):
        """Validate the entire configuration."""
        # Check if we're in debug mode and adjust logging level
        if self.debug:
            self.logging.level = 'DEBUG'
        
        return self
    
    @classmethod
    def from_file(cls, config_path: str) -> 'RevosMainConfig':
        """Load configuration from a file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # Determine file type and load accordingly
        if config_file.suffix.lower() in ['.yaml', '.yml']:
            import yaml
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f)
            return cls(**data)
        elif config_file.suffix.lower() == '.json':
            import json
            with open(config_file, 'r') as f:
                data = json.load(f)
            return cls(**data)
        elif config_file.suffix.lower() in ['.env', '']:
            # Load .env file using pydantic-settings
            return cls(_env_file=str(config_file))
        else:
            raise ValueError(f"Unsupported configuration file format: {config_file.suffix}")
    
    def save_to_file(self, config_path: str, format: str = 'yaml') -> None:
        """Save configuration to a file."""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = self.model_dump()
        
        if format.lower() in ['yaml', 'yml']:
            import yaml
            with open(config_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, indent=2)
        elif format.lower() == 'json':
            import json
            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    


# Global configuration instance (lazy initialization)
_settings: Optional[RevosMainConfig] = None


def get_settings() -> RevosMainConfig:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = RevosMainConfig()
    return _settings


def reload_settings() -> RevosMainConfig:
    """Reload settings from environment and config files."""
    global _settings
    _settings = RevosMainConfig()
    return _settings


def load_config_from_file(config_path: str) -> RevosMainConfig:
    """Load configuration from a file and set as global settings."""
    global _settings
    _settings = RevosMainConfig.from_file(config_path)
    return _settings


# Import factory functions from separate module
from .factory import create_config_with_prefixes


# For backward compatibility, create a function that returns the settings
def settings() -> RevosMainConfig:
    """Get the global settings instance (function for backward compatibility)."""
    return get_settings()
