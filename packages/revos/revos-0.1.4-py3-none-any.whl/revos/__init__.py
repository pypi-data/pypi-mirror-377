"""
Revoss: A Python library for Revoss API authentication and LangChain-based LLM tools.

This library provides comprehensive tools for:
- Revoss API authentication with dual authentication methods
- LangChain-based structured data extraction
- Token management with automatic refresh and fallback mechanisms
- LLM interaction through OpenAI-compatible APIs

Main Components:
- RevossTokenManager: Handles Revoss API authentication
- LangChainExtractor: Extracts structured data using LLMs
- TokenManager: Manages token lifecycle and refresh operations
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Core classes and functions
from .auth import (
    RevosTokenManager,
    get_revos_token,
    invalidate_revos_token,
    get_consecutive_failures,
    reset_token_manager,
    get_token_info,
    RevosError,
    RevosAuthenticationError,
    RevosConfigurationError,
    RevosTokenError,
    RevosAPIError,
    RevosValidationError,
)

from .config import (
    RevosMainConfig,
    RevosConfig,
    LLMConfig,
    LLMModelsConfig,
    LLMModelConfig,
    LoggingConfig,
    TokenManagerConfig,
    get_settings,
    reload_settings,
    load_config_from_file,
    create_config_with_prefixes,
    create_minimal_config,
    create_development_config,
    create_production_config,
    settings,
)

from .llm import (
    LangChainExtractor,
    get_langchain_extractor,
    create_all_extractors,
    list_available_extractors,
)

from .tokens import (
    TokenManager,
)

# Public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Configuration
    "RevosMainConfig",
    "RevosConfig", 
    "LLMConfig",
    "LLMModelsConfig",
    "LLMModelConfig",
    "LoggingConfig",
    "TokenManagerConfig",
    "get_settings",
    "reload_settings",
    "load_config_from_file",
    "create_config_with_prefixes",
    "create_minimal_config",
    "create_development_config",
    "create_production_config",
    "settings",
    
    # Revos authentication
    "RevosTokenManager",
    "get_revos_token",
    "invalidate_revos_token", 
    "get_consecutive_failures",
    "reset_token_manager",
    "get_token_info",
    
    # Exceptions
    "RevosError",
    "RevosAuthenticationError",
    "RevosConfigurationError",
    "RevosTokenError",
    "RevosAPIError",
    "RevosValidationError",
    
    # LangChain tools
    "LangChainExtractor",
    "get_langchain_extractor",
    "create_all_extractors",
    "list_available_extractors",
    
    # Token management
    "TokenManager",
]
