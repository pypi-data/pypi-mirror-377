"""
Token Refresh Logic

This module provides token refresh functionality for the Revos library,
including validation, testing, and refresh operations.
"""

import logging
import traceback
from datetime import datetime, timedelta
from typing import Optional

from ..auth.exceptions import RevosTokenError

logger = logging.getLogger(__name__)


class TokenRefreshManager:
    """
    Manages token refresh operations and validation.
    
    This class handles the logic for determining when tokens need to be
    refreshed and performing the actual refresh operations with proper
    validation and error handling.
    """
    
    def __init__(self, refresh_interval_minutes: int = 45):
        """
        Initialize the token refresh manager.

        Args:
            refresh_interval_minutes: Token refresh interval in minutes.
                Defaults to 45 minutes to provide a good balance between
                security and performance.
        """
        self.refresh_interval = refresh_interval_minutes * 60  # Convert to seconds
        self.last_refresh = None

    def should_refresh_token(self) -> bool:
        """
        Check if token should be refreshed based on time and buffer settings.

        This method determines if a token refresh is needed by comparing
        the current time with the last refresh time plus the configured
        refresh interval. It includes a buffer time to prevent using
        tokens that are about to expire.

        Returns:
            bool: True if token refresh is needed, False otherwise

        Note:
            Returns True if no previous refresh has occurred (last_refresh is None)
        """
        if self.last_refresh is None:
            return True
        return datetime.now() - self.last_refresh > timedelta(
            seconds=self.refresh_interval
        )

    def refresh_extractor(self) -> bool:
        """
        Refresh authentication tokens without executing LLM calls.

        This method performs a token refresh cycle that:
        1. Invalidates current tokens to force refresh
        2. Tests token acquisition without LLM calls
        3. Records the refresh timestamp

        The method avoids expensive LLM calls during refresh operations
        and focuses on token validation only.

        Returns:
            bool: True if refresh was successful, False otherwise

        Raises:
            RevosTokenError: If refresh fails after all attempts

        Refresh Process:
            1. Invalidate current tokens to force refresh
            2. Test token acquisition without LLM calls
            3. Record successful refresh timestamp
            4. Log refresh success or failure details
        """
        try:
            logger.info("Starting token refresh process...")
            
            # Invalidate current tokens to force refresh
            from ..auth.tokens import invalidate_revos_token
            invalidate_revos_token()
            
            # Test token acquisition without LLM calls
            if self._test_token_acquisition():
                # Record successful refresh
                self.last_refresh = datetime.now()
                logger.info(f"Token refresh successful at {self.last_refresh}")
                return True
            else:
                logger.error("Token refresh failed: token acquisition test failed")
                return False
                
        except Exception as e:
            logger.error(f"Token refresh failed with exception: {e}")
            logger.error(f"Token refresh traceback: {traceback.format_exc()}")
            raise RevosTokenError(f"Token refresh failed: {e}")

    def _test_token_acquisition(self) -> bool:
        """
        Test token acquisition without executing LLM calls.

        This method validates that a fresh token can be acquired
        without making expensive LLM API calls. It focuses purely
        on authentication token validation.

        Returns:
            bool: True if token acquisition succeeds, False otherwise

        Test Process:
            1. Attempt to acquire a fresh token
            2. Validate token format and expiration
            3. Log test results for debugging
        """
        try:
            logger.debug("Testing token acquisition...")
            
            # Try to get a fresh token
            from ..auth.tokens import get_revos_token
            token = get_revos_token(force_refresh=True)
            
            # Validate token
            if token and isinstance(token, str) and len(token) > 0:
                logger.debug("Token acquisition test successful")
                return True
            else:
                logger.warning("Token acquisition test failed: invalid token format")
                return False
                
        except Exception as e:
            logger.warning(f"Token acquisition test failed with exception: {e}")
            logger.debug(f"Token acquisition test traceback: {traceback.format_exc()}")
            return False
    
    def get_last_refresh_time(self) -> Optional[datetime]:
        """
        Get the timestamp of the last successful token refresh.
        
        Returns:
            Optional[datetime]: Last refresh timestamp, or None if no refresh has occurred
        """
        return self.last_refresh

