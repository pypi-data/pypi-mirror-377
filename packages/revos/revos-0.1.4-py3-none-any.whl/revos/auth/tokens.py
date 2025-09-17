"""
Token Utilities and Global Functions

This module provides utility functions for token management and global
token operations that can be used throughout the application.
"""

import logging
from typing import Optional

from .core import RevosTokenManager
from .exceptions import RevosAuthenticationError

logger = logging.getLogger(__name__)

# Global token manager instance
_token_manager: Optional[RevosTokenManager] = None


def _get_token_manager() -> RevosTokenManager:
    """
    Get or create the global token manager instance.
    
    This function implements lazy initialization of the global token manager.
    The manager is created only when first needed, ensuring that configuration
    is properly loaded before initialization.
    
    Returns:
        RevosTokenManager: Global token manager instance
        
    Raises:
        RevosAuthenticationError: If token manager initialization fails
    """
    global _token_manager
    if _token_manager is None:
        try:
            _token_manager = RevosTokenManager()
        except Exception as e:
            logger.error(f"Failed to initialize token manager: {e}")
            raise RevosAuthenticationError(f"Token manager initialization failed: {e}")
    return _token_manager


def get_revos_token(force_refresh: bool = False, use_fallback: bool = False) -> str:
    """
    Get Revos access token with automatic refresh and fallback support.

    This is the main public interface for obtaining Revos API access tokens.
    It delegates to the global RevosTokenManager instance and provides
    a simple interface for token operations.

    The function handles all token lifecycle management automatically,
    including expiration checking, refresh operations, and fallback
    method switching based on failure patterns.

    Args:
        force_refresh: If True, forces a new token fetch regardless of current token status
        use_fallback: If True, uses fallback authentication method instead of original

    Returns:
        str: Valid access token for Revos API operations

    Raises:
        RevosAuthenticationError: If authentication fails with both methods
        RevosAPIError: If API requests fail after all retries

    Examples:
        # Get current token (refresh if needed)
        token = get_revos_token()
        
        # Force refresh token
        token = get_revos_token(force_refresh=True)
        
        # Use fallback authentication method
        token = get_revos_token(use_fallback=True)
    """
    try:
        token_manager = _get_token_manager()
        return token_manager.get_token(force_refresh=force_refresh, use_fallback=use_fallback)
    except Exception as e:
        logger.error(f"Failed to get Revos token: {e}")
        raise


def invalidate_revos_token():
    """
    Invalidate current Revos token to force refresh.

    This function clears the current token in the global token manager,
    forcing the system to fetch a new token on the next get_revos_token()
    call. It's useful for handling token revocation or when you need to
    ensure a fresh token is obtained.

    The function also resets the consecutive failure counter, giving
    the system a fresh start for authentication attempts.

    Examples:
        # Invalidate current token
        invalidate_revos_token()
        
        # Next call will fetch a new token
        token = get_revos_token()
    """
    try:
        token_manager = _get_token_manager()
        token_manager.invalidate_token()
        logger.info("Revos token invalidated successfully")
    except Exception as e:
        logger.error(f"Failed to invalidate Revos token: {e}")
        raise


def get_consecutive_failures() -> int:
    """
    Get the number of consecutive authentication failures.

    This function returns the current count of consecutive authentication
    failures from the global token manager. It's useful for monitoring
    authentication health and implementing custom retry logic.

    Returns:
        int: Number of consecutive authentication failures
        
    Examples:
        # Check authentication health
        failures = get_consecutive_failures()
        if failures > 5:
            print("Authentication is having issues")
    """
    try:
        token_manager = _get_token_manager()
        return token_manager.consecutive_failures
    except Exception as e:
        logger.error(f"Failed to get consecutive failures count: {e}")
        return 0


def reset_token_manager():
    """
    Reset the global token manager instance.
    
    This function clears the global token manager instance, forcing
    a new one to be created on the next token operation. It's useful
    for testing or when you need to reinitialize the token manager
    with new configuration.
    
    Examples:
        # Reset token manager (useful for testing)
        reset_token_manager()
        
        # Next token operation will create a new manager
        token = get_revos_token()
    """
    global _token_manager
    _token_manager = None
    logger.info("Token manager reset")


def get_token_info() -> dict:
    """
    Get information about the current token state.
    
    This function returns a dictionary with information about the
    current token state, including expiration time and failure count.
    It's useful for debugging and monitoring token health.
    
    Returns:
        dict: Token information including:
            - has_token: Whether a token is currently available
            - expires_at: Token expiration time (if available)
            - consecutive_failures: Number of consecutive failures
            - time_until_expiry: Seconds until token expires (if available)
    """
    try:
        token_manager = _get_token_manager()
        info = {
            "has_token": token_manager._token is not None,
            "consecutive_failures": token_manager.consecutive_failures,
        }
        
        if token_manager._token_expires_at:
            from datetime import datetime
            now = datetime.now()
            if token_manager._token_expires_at > now:
                info["expires_at"] = token_manager._token_expires_at.isoformat()
                info["time_until_expiry"] = (token_manager._token_expires_at - now).total_seconds()
            else:
                info["expired"] = True
                
        return info
    except Exception as e:
        logger.error(f"Failed to get token info: {e}")
        return {"error": str(e)}
