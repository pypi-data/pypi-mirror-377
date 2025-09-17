"""
Revos API Authentication and Token Management

This module provides the main interface for Revos API authentication.
It re-exports the core authentication classes and functions from
the specialized modules for backward compatibility.

For detailed implementation, see:
- revo.auth: Core authentication logic
- revo.tokens: Token utilities and global functions
- revo.exceptions: Custom exceptions
"""

# Re-export everything for backward compatibility
from ..auth.core import RevosTokenManager
from ..auth.tokens import (
    get_revos_token,
    invalidate_revos_token,
    get_consecutive_failures,
    reset_token_manager,
    get_token_info
)
from ..auth.exceptions import (
    RevosError,
    RevosAuthenticationError,
    RevosConfigurationError,
    RevosTokenError,
    RevosAPIError,
    RevosValidationError
)