"""
Revos API Authentication Core

This module provides the core authentication logic for the Revos API,
including token acquisition, validation, and management.
"""

import requests
import time
import logging
import traceback
from datetime import datetime, timedelta
from typing import Optional

from ..config import get_settings
from .exceptions import RevosAuthenticationError, RevosAPIError

logger = logging.getLogger(__name__)


class RevosTokenManager:
    """
    Manages Revos API authentication tokens with dual authentication methods.

    This class provides robust token management for the Revos API service,
    implementing both primary and fallback authentication methods to ensure
    continuous service availability. It handles token lifecycle, automatic
    refresh, and intelligent fallback switching based on failure patterns.

    The manager supports two authentication flows:
    1. Original OAuth2 client credentials method
    2. Fallback httpx-based method for OpenShift compatibility

    Attributes:
        client_id: Revos API client identifier
        client_secret: Revos API client secret key
        token_url: OAuth token endpoint URL
        _token: Current access token (private)
        _token_expires_at: Token expiration timestamp (private)
        _buffer_minutes: Buffer time before token expiration
        consecutive_failures: Count of consecutive authentication failures
        max_failures_before_fallback: Threshold for switching to fallback method

    Authentication Strategy:
        - Always try original method first unless explicitly told to use fallback
        - Switch to fallback method after consecutive failures
        - Reset failure counters on successful authentication
        - Maintain token expiration tracking with buffer time
    """
    
    def __init__(self, settings_instance: Optional[object] = None):
        """
        Initialize the Revos token manager with configuration.

        Reads Revos API configuration from the provided settings or global settings
        and validates that all required configuration values are present. 
        Sets up the authentication parameters and initializes internal state.

        Args:
            settings_instance: Optional settings instance. If None, uses global settings.

        Raises:
            ValueError: If required Revos configuration is missing
        """
        self.settings = settings_instance or get_settings()
        self.revos_config = self.settings.revos
        
        self.client_id = self.revos_config.client_id
        self.client_secret = self.revos_config.client_secret
        self.token_url = self.revos_config.token_url
        self.base_url = self.revos_config.base_url
        self._token = None
        self._token_expires_at = None
        self._buffer_minutes = self.revos_config.token_buffer_minutes
        self.max_retries = self.revos_config.max_retries
        self.request_timeout = self.revos_config.request_timeout
        self.consecutive_failures = 0
        self.max_failures_before_fallback = self.settings.token_manager.max_failures_before_fallback

        if not all([self.client_id, self.client_secret, self.token_url]):
            raise ValueError("Missing required Revos configuration. Please set REVOS_CLIENT_ID and REVOS_CLIENT_SECRET environment variables.")

    def _fetch_new_token(self) -> dict:
        """
        Fetch a new token from Revos using the original OAuth2 method.

        This method implements the standard OAuth2 client credentials flow
        using the requests library. It includes retry logic with exponential
        backoff to handle transient network issues and service unavailability.

        The method sends a POST request to the token endpoint with client
        credentials and handles various response scenarios including network
        errors, HTTP status errors, and malformed responses.

        Returns:
            dict: Token response containing access_token and expires_in

        Raises:
            requests.exceptions.RequestException: For network and HTTP errors
            ValueError: If response doesn't contain access_token

        Retry Logic:
            - Maximum of 3 retry attempts
            - Exponential backoff: 2^attempt seconds delay
            - Logs warnings for failed attempts
            - Raises exception after all retries exhausted
        """
        token_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        max_retries = self.max_retries
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Attempting original token fetch (attempt {attempt + 1}/{max_retries})..."
                )
                response = requests.post(
                    self.token_url,
                    data=token_data,
                    timeout=self.request_timeout,
                )
                response.raise_for_status()

                token_response = response.json()
                if "access_token" not in token_response:
                    raise ValueError("Response missing access_token")

                logger.info("Successfully obtained token using original method")
                self.consecutive_failures = 0  # Reset failure counter on success
                return token_response

            except requests.exceptions.RequestException as e:
                logger.warning(f"Original token fetch attempt {attempt + 1} failed: {e}")
                logger.debug(f"Token fetch attempt {attempt + 1} traceback: {traceback.format_exc()}")
                if attempt < max_retries - 1:
                    delay = 2 ** attempt
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("All original token fetch attempts failed")
                    raise RevosAPIError(f"Failed to fetch token after {max_retries} attempts: {e}")

            except ValueError as e:
                logger.error(f"Invalid token response: {e}")
                raise RevosAuthenticationError(f"Invalid token response: {e}")

    def _fetch_new_token_fallback(self) -> dict:
        """
        Fetch a new token using the fallback httpx-based method.

        This method implements an alternative authentication approach using
        httpx with custom headers and authentication mechanisms. It's designed
        to work in environments where the standard OAuth2 flow may not be
        available or may be blocked by network policies.

        The fallback method uses httpx to make the authentication request
        with additional headers and potentially different authentication
        mechanisms that are compatible with OpenShift and similar platforms.

        Returns:
            dict: Token response containing access_token and expires_in

        Raises:
            httpx.RequestError: For network and HTTP errors
            ValueError: If response doesn't contain access_token

        Note:
            This method requires httpx to be installed. If httpx is not
            available, it will raise an ImportError.
        """
        try:
            import httpx
        except ImportError:
            raise ImportError(
                "httpx is required for fallback authentication. Install with: pip install httpx"
            )

        token_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Revos-Python-Client/1.0",
        }

        max_retries = self.max_retries
        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Attempting fallback token fetch (attempt {attempt + 1}/{max_retries})..."
                )
                
                with httpx.Client(timeout=self.request_timeout) as client:
                    response = client.post(
                        self.token_url,
                        data=token_data,
                        headers=headers,
                    )
                    response.raise_for_status()

                    token_response = response.json()
                    if "access_token" not in token_response:
                        raise ValueError("Response missing access_token")

                    logger.info("Successfully obtained token using fallback method")
                    self.consecutive_failures = 0  # Reset failure counter on success
                    return token_response

            except httpx.RequestError as e:
                logger.warning(f"Fallback token fetch attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    delay = 2 ** attempt
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("All fallback token fetch attempts failed")
                    raise RevosAPIError(f"Failed to fetch token using fallback method after {max_retries} attempts: {e}")

            except ValueError as e:
                logger.error(f"Invalid fallback token response: {e}")
                raise RevosAuthenticationError(f"Invalid fallback token response: {e}")

    def get_token(self, force_refresh: bool = False, use_fallback: bool = False) -> str:
        """
        Get a valid access token, refreshing if necessary.

        This method provides the main interface for obtaining valid access tokens.
        It handles token lifecycle management, including checking expiration,
        automatic refresh, and fallback method switching based on failure patterns.

        The method implements intelligent token management:
        - Checks if current token is still valid (with buffer time)
        - Automatically refreshes expired or missing tokens
        - Switches to fallback method after consecutive failures
        - Handles both forced refresh and automatic refresh scenarios

        Args:
            force_refresh: If True, forces a new token fetch regardless of current token status
            use_fallback: If True, uses fallback authentication method instead of original

        Returns:
            str: Valid access token for API operations

        Raises:
            RevosAuthenticationError: If authentication fails with both methods
            RevosAPIError: If API requests fail after all retries

        Token Management Logic:
            1. If force_refresh is True, immediately fetch new token
            2. If current token is None or expired, fetch new token
            3. If consecutive_failures >= max_failures_before_fallback, use fallback
            4. Otherwise, use original method
            5. Update token and expiration time on successful fetch
        """
        # Force refresh or no token available
        if force_refresh or self._token is None:
            logger.info("Fetching new token (force refresh or no token)")
            self._fetch_and_update_token(use_fallback)
            return self._token

        # Check if token is expired (with buffer time)
        if self._token_expires_at and datetime.now() >= self._token_expires_at:
            logger.info("Token expired, fetching new token")
            self._fetch_and_update_token(use_fallback)
            return self._token

        # Token is still valid
        logger.debug("Using existing valid token")
        return self._token

    def _fetch_and_update_token(self, use_fallback: bool = False) -> None:
        """
        Fetch a new token and update internal state.

        This method handles the actual token fetching logic and updates
        the internal token state. It implements the fallback switching
        logic based on consecutive failures and user preferences.

        Args:
            use_fallback: If True, uses fallback method; if False, uses intelligent switching

        Raises:
            RevosAuthenticationError: If both authentication methods fail
        """
        # Determine which method to use
        should_use_fallback = (
            use_fallback or 
            self.consecutive_failures >= self.max_failures_before_fallback
        )

        try:
            if should_use_fallback:
                logger.info("Using fallback authentication method")
                token_response = self._fetch_new_token_fallback()
            else:
                logger.info("Using original authentication method")
                token_response = self._fetch_new_token()

            # Update token state
            self._token = token_response["access_token"]
            
            # Calculate expiration time
            expires_in = token_response.get("expires_in", 3600)  # Default 1 hour
            buffer_seconds = self._buffer_minutes * 60
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - buffer_seconds)
            
            logger.info(f"Token updated, expires at {self._token_expires_at}")

        except Exception as e:
            self.consecutive_failures += 1
            logger.error(f"Token fetch failed (failure #{self.consecutive_failures}): {e}")
            logger.error(f"Token fetch failure traceback: {traceback.format_exc()}")
            
            # Try fallback if original method failed and we haven't tried it yet
            if not should_use_fallback and self.consecutive_failures >= self.max_failures_before_fallback:
                logger.info("Switching to fallback method due to consecutive failures")
                try:
                    token_response = self._fetch_new_token_fallback()
                    self._token = token_response["access_token"]
                    expires_in = token_response.get("expires_in", 3600)
                    buffer_seconds = self._buffer_minutes * 60
                    self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - buffer_seconds)
                    logger.info("Successfully obtained token using fallback method")
                    return
                except Exception as fallback_error:
                    logger.error(f"Fallback method also failed: {fallback_error}")
                    logger.error(f"Fallback method traceback: {traceback.format_exc()}")
            
            raise RevosAuthenticationError(f"Failed to obtain token: {e}")

    def invalidate_token(self) -> None:
        """
        Invalidate the current token to force refresh on next request.

        This method clears the current token and expiration time, forcing
        the system to fetch a new token on the next get_token() call.
        It's useful for handling token revocation or when you need to
        ensure a fresh token is obtained.

        The method also resets the consecutive failure counter, giving
        the system a fresh start for authentication attempts.
        """
        logger.info("Invalidating current Revos token")
        self._token = None
        self._token_expires_at = None
        self.consecutive_failures = 0
