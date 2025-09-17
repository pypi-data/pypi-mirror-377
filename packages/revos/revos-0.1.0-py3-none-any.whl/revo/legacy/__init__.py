"""
Legacy Module

This module provides backward compatibility for the Revo library,
re-exporting functionality from the new modular structure.
"""

from .revo import (
    RevoTokenManager,
    get_revo_token,
    invalidate_revo_token,
    get_consecutive_failures,
    reset_token_manager,
    get_token_info,
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
