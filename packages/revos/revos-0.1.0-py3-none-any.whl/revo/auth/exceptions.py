"""
Custom exceptions for the Revo library.

This module defines all custom exceptions used throughout the Revo library,
providing clear error handling and better debugging capabilities.
"""


class RevoError(Exception):
    """Base exception for all Revo library errors."""
    pass


class RevoAuthenticationError(RevoError):
    """Raised when authentication fails."""
    pass


class RevoConfigurationError(RevoError):
    """Raised when configuration is invalid or missing."""
    pass


class RevoTokenError(RevoError):
    """Raised when token operations fail."""
    pass


class RevoAPIError(RevoError):
    """Raised when API requests fail."""
    pass


class RevoValidationError(RevoError):
    """Raised when data validation fails."""
    pass
