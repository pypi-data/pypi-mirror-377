"""
Legacy Module

This module provides backward compatibility for the Revos library,
re-exporting functionality from the new modular structure.
"""

from .revo import (
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
