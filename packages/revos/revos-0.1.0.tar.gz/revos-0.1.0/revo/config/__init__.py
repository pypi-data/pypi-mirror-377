"""
Configuration package for the Revo library.

This package provides a modular configuration system with separate
modules for different configuration aspects:

- api: Revo API authentication and connection settings
- llm: LLM model and generation parameters
- logging: Logging configuration and file rotation
- token: Token management and refresh settings
- main: Main configuration class that combines all sections

Usage:
    from revo.config import get_settings, RevoMainConfig
    from revo.config.api import RevoConfig
    from revo.config.llm import LLMConfig
"""

# Main configuration classes and functions
from .main import (
    RevoMainConfig,
    get_settings,
    reload_settings,
    load_config_from_file,
    settings,
)

# Factory functions
from .factory import (
    create_config_with_prefixes,
    create_minimal_config,
    create_development_config,
    create_production_config,
)

# Individual configuration classes
from .api import RevoConfig
from .llm import LLMConfig
from .llm_models import LLMModelsConfig, LLMModelConfig
from .logging import LoggingConfig
from .token import TokenManagerConfig


__all__ = [
    # Main configuration
    "RevoMainConfig",
    "get_settings",
    "reload_settings", 
    "load_config_from_file",
    "settings",
    
    # Factory functions
    "create_config_with_prefixes",
    "create_minimal_config",
    "create_development_config",
    "create_production_config",
    
    # Individual configuration classes
    "RevoConfig",
    "LLMConfig",
    "LLMModelsConfig",
    "LLMModelConfig",
    "LoggingConfig",
    "TokenManagerConfig",
    
]
