"""
Configuration Factory Functions

This module provides factory functions for creating configurations
with custom settings, prefixes, and other options.
"""

from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from .api import RevosConfig
from .llm import LLMConfig
from .logging import LoggingConfig
from .token import TokenManagerConfig
from .main import RevosMainConfig


def create_config_with_prefixes(
    revo_prefix: str = "REVOS_",
    llm_prefix: str = "LLM_", 
    logging_prefix: str = "LOG_",
    token_prefix: str = "TOKEN_",
    **kwargs
) -> RevosMainConfig:
    """
    Create a RevosMainConfig with custom environment variable prefixes.
    
    Args:
        revo_prefix: Prefix for Revos API environment variables (default: "REVOS_")
        llm_prefix: Prefix for LLM environment variables (default: "LLM_")
        logging_prefix: Prefix for logging environment variables (default: "LOG_")
        token_prefix: Prefix for token management environment variables (default: "TOKEN_")
        **kwargs: Additional arguments passed to RevosMainConfig
        
    Returns:
        RevosMainConfig instance with custom prefixes
        
    Example:
        # Use custom prefixes
        config = create_config_with_prefixes(
            revo_prefix="MY_API_",
            llm_prefix="AI_",
            logging_prefix="LOG_"
        )
        
        # This will look for environment variables like:
        # MY_API_CLIENT_ID, MY_API_CLIENT_SECRET
        # AI_MODEL, AI_TEMPERATURE
        # LOG_LEVEL, LOG_FORMAT
    """
    # Create custom config classes with modified prefixes
    class CustomRevosConfig(RevosConfig):
        model_config = SettingsConfigDict(
            env_prefix=revo_prefix,
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
        )
    
    class CustomLLMConfig(LLMConfig):
        model_config = SettingsConfigDict(
            env_prefix=llm_prefix,
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
        )
    
    class CustomLoggingConfig(LoggingConfig):
        model_config = SettingsConfigDict(
            env_prefix=logging_prefix,
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
        )
    
    class CustomTokenManagerConfig(TokenManagerConfig):
        model_config = SettingsConfigDict(
            env_prefix=token_prefix,
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
        )
    
    # Create the main config with custom nested configs
    class CustomRevosMainConfig(RevosMainConfig):
        revo: CustomRevosConfig = Field(default_factory=CustomRevosConfig)
        llm: CustomLLMConfig = Field(default_factory=CustomLLMConfig)
        logging: CustomLoggingConfig = Field(default_factory=CustomLoggingConfig)
        token_manager: CustomTokenManagerConfig = Field(default_factory=CustomTokenManagerConfig)
        
        def __init__(self, **kwargs):
            # Extract _env_file if provided
            env_file = kwargs.pop('_env_file', None)
            
            # If _env_file is provided, pass it to nested configurations
            if env_file:
                if 'revo' not in kwargs:
                    kwargs['revo'] = CustomRevosConfig(_env_file=env_file)
                if 'llm' not in kwargs:
                    kwargs['llm'] = CustomLLMConfig(_env_file=env_file)
                if 'logging' not in kwargs:
                    kwargs['logging'] = CustomLoggingConfig(_env_file=env_file)
                if 'token_manager' not in kwargs:
                    kwargs['token_manager'] = CustomTokenManagerConfig(_env_file=env_file)
            
            super().__init__(**kwargs)
    
    return CustomRevosMainConfig(**kwargs)


def create_minimal_config(**kwargs) -> RevosMainConfig:
    """
    Create a minimal configuration with only essential settings.
    
    Args:
        **kwargs: Additional arguments passed to RevosMainConfig
        
    Returns:
        RevosMainConfig instance with minimal settings
    """
    return RevosMainConfig(
        revo=RevosConfig(
            client_id=kwargs.get('client_id', ''),
            client_secret=kwargs.get('client_secret', ''),
            token_url=kwargs.get('token_url', 'https://your-site.com/revo/oauth/token'),
            base_url=kwargs.get('base_url', 'https://your-site.com/revo/llm-api')
        ),
        llm=LLMConfig(
            model=kwargs.get('model', 'gpt-3.5-turbo'),
            temperature=kwargs.get('temperature', 0.7)
        ),
        logging=LoggingConfig(
            level=kwargs.get('log_level', 'INFO')
        ),
        debug=kwargs.get('debug', False)
    )


def create_development_config(**kwargs) -> RevosMainConfig:
    """
    Create a configuration optimized for development.
    
    Args:
        **kwargs: Additional arguments passed to RevosMainConfig
        
    Returns:
        RevosMainConfig instance with development-optimized settings
    """
    return RevosMainConfig(
        revo=RevosConfig(
            client_id=kwargs.get('client_id', 'dev-client-id'),
            client_secret=kwargs.get('client_secret', 'dev-client-secret'),
            token_url=kwargs.get('token_url', 'https://dev-api.example.com/oauth/token'),
            base_url=kwargs.get('base_url', 'https://dev-api.example.com/llm-api'),
            token_buffer_minutes=10,  # Longer buffer for dev
            max_retries=5,  # More retries for dev
            request_timeout=60  # Longer timeout for dev
        ),
        llm=LLMConfig(
            model=kwargs.get('model', 'gpt-4'),
            temperature=kwargs.get('temperature', 0.8),
            max_tokens=kwargs.get('max_tokens', 2000)
        ),
        logging=LoggingConfig(
            level='DEBUG',
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            file=kwargs.get('log_file', '/tmp/revo-dev.log')
        ),
        token_manager=TokenManagerConfig(
            refresh_interval_minutes=30,  # More frequent refresh for dev
            enable_periodic_refresh=True,
            enable_fallback=True
        ),
        debug=True
    )


def create_production_config(**kwargs) -> RevosMainConfig:
    """
    Create a configuration optimized for production.
    
    Args:
        **kwargs: Additional arguments passed to RevosMainConfig
        
    Returns:
        RevosMainConfig instance with production-optimized settings
    """
    return RevosMainConfig(
        revo=RevosConfig(
            client_id=kwargs.get('client_id', ''),
            client_secret=kwargs.get('client_secret', ''),
            token_url=kwargs.get('token_url', 'https://api.example.com/oauth/token'),
            base_url=kwargs.get('base_url', 'https://api.example.com/llm-api'),
            token_buffer_minutes=5,  # Shorter buffer for prod
            max_retries=3,  # Standard retries for prod
            request_timeout=30  # Standard timeout for prod
        ),
        llm=LLMConfig(
            model=kwargs.get('model', 'gpt-3.5-turbo'),
            temperature=kwargs.get('temperature', 0.1),  # Lower temperature for prod
            max_tokens=kwargs.get('max_tokens', 1000)
        ),
        logging=LoggingConfig(
            level='WARNING',
            format='%(asctime)s - %(levelname)s - %(message)s',
            file=kwargs.get('log_file', '/var/log/revo/revo.log'),
            max_size=50 * 1024 * 1024,  # 50MB
            backup_count=10
        ),
        token_manager=TokenManagerConfig(
            refresh_interval_minutes=45,  # Standard refresh for prod
            enable_periodic_refresh=True,
            enable_fallback=True
        ),
        debug=False
    )
