"""
Revo API Authentication and Token Management

This module provides the main interface for Revo API authentication.
It re-exports the core authentication classes and functions from
the specialized modules for backward compatibility.

For detailed implementation, see:
- revo.auth: Core authentication logic
- revo.tokens: Token utilities and global functions
- revo.exceptions: Custom exceptions
"""

# Re-export everything for backward compatibility
from ..auth.core import RevoTokenManager
from ..auth.tokens import (
    get_revo_token,
    invalidate_revo_token,
    get_consecutive_failures,
    reset_token_manager,
    get_token_info
)
from ..auth.exceptions import (
    RevoError,
    RevoAuthenticationError,
    RevoConfigurationError,
    RevoTokenError,
    RevoAPIError,
    RevoValidationError
)