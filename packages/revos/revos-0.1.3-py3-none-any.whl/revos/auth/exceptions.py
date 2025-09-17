"""
Custom exceptions for the Revos library.

This module defines all custom exceptions used throughout the Revos library,
providing clear error handling and better debugging capabilities.
"""


class RevosError(Exception):
    """Base exception for all Revos library errors."""
    pass


class RevosAuthenticationError(RevosError):
    """Raised when authentication fails."""
    pass


class RevosConfigurationError(RevosError):
    """Raised when configuration is invalid or missing."""
    pass


class RevosTokenError(RevosError):
    """Raised when token operations fail."""
    pass


class RevosAPIError(RevosError):
    """Raised when API requests fail."""
    pass


class RevosValidationError(RevosError):
    """Raised when data validation fails."""
    pass
