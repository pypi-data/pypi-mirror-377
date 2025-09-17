"""
Token Management and Refresh Service

This module provides the main interface for token management in the
Revos library. It combines refresh logic and background services
for comprehensive token lifecycle management.

For detailed implementation, see:
- revo.refresh: Token refresh logic and validation
- revo.background: Background services and periodic tasks
"""

import threading
from datetime import datetime
from typing import Optional

from .refresh import TokenRefreshManager
from .background import BackgroundTokenManager
from ..auth.exceptions import RevosTokenError

# Re-export for backward compatibility
TokenRefreshManager = TokenRefreshManager
BackgroundTokenManager = BackgroundTokenManager


class TokenManager:
    """
    Main token manager that combines refresh logic and background services.

    This class provides a unified interface for token management, combining
    the refresh logic and background services into a single, easy-to-use
    interface. It maintains backward compatibility while providing access
    to the new modular functionality.

    The manager operates in two modes:
    1. On-demand refresh when tokens are needed
    2. Background periodic refresh to maintain token validity
    """

    def __init__(self, refresh_interval_minutes: int = 45):
        """
        Initialize the token manager with refresh interval configuration.

        Args:
            refresh_interval_minutes: Token refresh interval in minutes.
                Defaults to 45 minutes to provide a good balance between
                security and performance.
        """
        self.refresh_manager = TokenRefreshManager(refresh_interval_minutes)
        self.background_manager = BackgroundTokenManager(refresh_interval_minutes)
        self.lock = threading.Lock()

    def should_refresh_token(self) -> bool:
        """
        Check if token should be refreshed based on time and buffer settings.

        Returns:
            bool: True if token refresh is needed, False otherwise
        """
        return self.refresh_manager.should_refresh_token()

    def refresh_extractor(self) -> bool:
        """
        Refresh the LLM extractor with a new authentication token.

        Returns:
            bool: True if refresh was successful, False otherwise
        """
        return self.refresh_manager.refresh_extractor()

    async def start_background_refresh(self) -> None:
        """
        Start the background token refresh service.

        Raises:
            RevosTokenError: If background service fails to start
        """
        await self.background_manager.start_background_refresh()
    
    async def start_background_service(self) -> None:
        """
        Start the background token refresh service.
        Alias for start_background_refresh for backward compatibility.
        """
        await self.start_background_refresh()
    
    async def stop_background_service(self) -> None:
        """
        Stop the background token refresh service.
        Alias for stop_background_refresh for backward compatibility.
        """
        await self.background_manager.stop_background_refresh()
    
    def is_background_service_running(self) -> bool:
        """
        Check if the background service is currently running.
        
        Returns:
            bool: True if background service is running, False otherwise
        """
        return self.background_manager.is_running()

    async def stop_background_refresh(self) -> None:
        """
        Stop the background token refresh service.
        """
        await self.background_manager.stop_background_refresh()

    def is_background_running(self) -> bool:
        """
        Check if the background refresh service is running.

        Returns:
            bool: True if the service is running, False otherwise
        """
        return self.background_manager.is_running()

    def get_last_refresh_time(self) -> Optional[datetime]:
        """
        Get the timestamp of the last successful token refresh.

        Returns:
            Optional[datetime]: Last refresh timestamp, or None if no refresh has occurred
        """
        return self.refresh_manager.get_last_refresh_time()

    def force_refresh(self) -> bool:
        """
        Force an immediate token refresh.

        Returns:
            bool: True if refresh was successful, False otherwise
        """
        return self.background_manager.force_refresh()