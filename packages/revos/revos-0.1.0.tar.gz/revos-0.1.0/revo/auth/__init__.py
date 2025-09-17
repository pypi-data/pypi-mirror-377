"""
Authentication Module

This module provides authentication functionality for the Revo library,
including token management, authentication flows, and error handling.
"""

from .core import RevoTokenManager
from .tokens import (
    get_revo_token,
    invalidate_revo_token,
    get_consecutive_failures,
    reset_token_manager,
    get_token_info
)
from .exceptions import (
    RevoError,
    RevoAuthenticationError,
    RevoConfigurationError,
    RevoTokenError,
    RevoAPIError,
    RevoValidationError
)

__all__ = [
    # Core authentication
    "RevoTokenManager",
    
    # Token utilities
    "get_revo_token",
    "invalidate_revo_token",
    "get_consecutive_failures",
    "reset_token_manager",
    "get_token_info",
    
    # Exceptions
    "RevoError",
    "RevoAuthenticationError",
    "RevoConfigurationError",
    "RevoTokenError",
    "RevoAPIError",
    "RevoValidationError",
]
