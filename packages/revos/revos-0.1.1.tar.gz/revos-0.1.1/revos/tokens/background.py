"""
Background Services and Periodic Tasks

This module provides background services for the Revos library,
including periodic token refresh and background task management.
"""

import asyncio
import logging
import threading
import traceback
from datetime import datetime, timedelta
from typing import Optional

from .refresh import TokenRefreshManager
from ..auth.exceptions import RevosTokenError

logger = logging.getLogger(__name__)


class BackgroundTokenManager:
    """
    Manages background token refresh operations and periodic tasks.
    
    This class provides background services for automatic token refresh,
    including periodic refresh operations and background task management.
    It ensures that tokens are refreshed automatically without blocking
    the main application flow.
    """
    
    def __init__(self, refresh_interval_minutes: int = 45):
        """
        Initialize the background token manager.

        Args:
            refresh_interval_minutes: Token refresh interval in minutes.
                Defaults to 45 minutes to provide a good balance between
                security and performance.
        """
        self.refresh_manager = TokenRefreshManager(refresh_interval_minutes)
        self.lock = threading.Lock()
        self._background_task: Optional[asyncio.Task] = None
        self._running = False

    async def start_background_refresh(self) -> None:
        """
        Start the background token refresh service.

        This method starts an asynchronous background task that periodically
        refreshes authentication tokens. The task runs continuously until
        stopped, ensuring that tokens are always fresh and valid.

        The background service:
        1. Checks if token refresh is needed at regular intervals
        2. Performs refresh operations when needed
        3. Handles errors gracefully without stopping the service
        4. Logs all operations for monitoring and debugging

        Raises:
            RevosTokenError: If background service fails to start
        """
        if self._running:
            logger.warning("Background refresh service is already running")
            return

        try:
            self._running = True
            logger.info("Starting background token refresh service...")
            
            # Start the background task
            self._background_task = asyncio.create_task(self._background_refresh_loop())
            
            logger.info("Background token refresh service started successfully")
            
        except Exception as e:
            self._running = False
            logger.error(f"Failed to start background refresh service: {e}")
            logger.error(f"Background service startup traceback: {traceback.format_exc()}")
            raise RevosTokenError(f"Background service startup failed: {e}")

    async def stop_background_refresh(self) -> None:
        """
        Stop the background token refresh service.

        This method gracefully stops the background refresh service,
        ensuring that any ongoing operations are completed before
        shutting down. It's important to call this method when
        the application is shutting down to prevent resource leaks.

        The method:
        1. Sets the running flag to False
        2. Cancels the background task
        3. Waits for the task to complete
        4. Logs the shutdown process
        """
        if not self._running:
            logger.warning("Background refresh service is not running")
            return

        try:
            logger.info("Stopping background token refresh service...")
            self._running = False
            
            if self._background_task:
                self._background_task.cancel()
                try:
                    await self._background_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Background token refresh service stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping background refresh service: {e}")
            logger.error(f"Background service stop traceback: {traceback.format_exc()}")

    async def _background_refresh_loop(self) -> None:
        """
        Background refresh loop that runs continuously.

        This method implements the main background refresh loop that
        periodically checks if token refresh is needed and performs
        refresh operations when necessary. It runs continuously until
        the service is stopped.

        The loop:
        1. Checks if refresh is needed every minute
        2. Performs refresh operations when needed
        3. Handles errors gracefully
        4. Logs all operations for monitoring
        """
        logger.info("Background refresh loop started")
        
        try:
            while self._running:
                try:
                    # Check if refresh is needed
                    if self.refresh_manager.should_refresh_token():
                        logger.info("Background refresh needed, performing refresh...")
                        
                        # Perform refresh in a thread to avoid blocking
                        loop = asyncio.get_event_loop()
                        success = await loop.run_in_executor(
                            None, self.refresh_manager.refresh_extractor
                        )
                        
                        if success:
                            logger.info("Background refresh completed successfully")
                        else:
                            logger.warning("Background refresh failed")
                    
                    # Wait for 1 minute before next check
                    await asyncio.sleep(60)
                    
                except Exception as e:
                    logger.error(f"Error in background refresh loop: {e}")
                    logger.error(f"Background refresh loop traceback: {traceback.format_exc()}")
                    # Wait a bit before retrying
                    await asyncio.sleep(30)
                    
        except asyncio.CancelledError:
            logger.info("Background refresh loop cancelled")
        except Exception as e:
            logger.error(f"Fatal error in background refresh loop: {e}")
            logger.error(f"Fatal background refresh loop traceback: {traceback.format_exc()}")
        finally:
            logger.info("Background refresh loop ended")

    def is_running(self) -> bool:
        """
        Check if the background refresh service is running.

        Returns:
            bool: True if the service is running, False otherwise
        """
        return self._running

    def get_last_refresh_time(self) -> Optional[datetime]:
        """
        Get the timestamp of the last successful token refresh.

        Returns:
            Optional[datetime]: Last refresh timestamp, or None if no refresh has occurred
        """
        return self.refresh_manager.last_refresh

    def force_refresh(self) -> bool:
        """
        Force an immediate token refresh.

        This method performs an immediate token refresh, bypassing
        the normal timing checks. It's useful for testing or when
        you need to ensure a fresh token is obtained immediately.

        Returns:
            bool: True if refresh was successful, False otherwise
        """
        try:
            logger.info("Forcing immediate token refresh...")
            success = self.refresh_manager.refresh_extractor()
            if success:
                logger.info("Forced refresh completed successfully")
            else:
                logger.warning("Forced refresh failed")
            return success
        except Exception as e:
            logger.error(f"Forced refresh failed with exception: {e}")
            logger.error(f"Forced refresh traceback: {traceback.format_exc()}")
            return False
