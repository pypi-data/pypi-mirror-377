"""
Authentication Module

This module provides authentication functionality for the Revos library,
including token management, authentication flows, and error handling.
"""

from .core import RevosTokenManager
from .tokens import (
    get_revos_token,
    invalidate_revos_token,
    get_consecutive_failures,
    reset_token_manager,
    get_token_info
)
from .exceptions import (
    RevosError,
    RevosAuthenticationError,
    RevosConfigurationError,
    RevosTokenError,
    RevosAPIError,
    RevosValidationError
)

__all__ = [
    # Core authentication
    "RevosTokenManager",
    
    # Token utilities
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
]
