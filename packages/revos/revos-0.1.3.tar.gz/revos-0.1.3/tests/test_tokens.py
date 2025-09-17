"""
Tests for token management functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from revos.tokens.refresh import TokenRefreshManager
from revos.tokens.background import BackgroundTokenManager
from revos.tokens.manager import TokenManager
from revos.auth.exceptions import RevosTokenError


class TestTokenRefreshManager:
    """Test cases for TokenRefreshManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.refresh_manager = TokenRefreshManager(refresh_interval_minutes=30)
    
    def test_init(self):
        """Test TokenRefreshManager initialization."""
        assert self.refresh_manager.refresh_interval == 1800  # 30 minutes in seconds
        assert self.refresh_manager.last_refresh is None
    
    def test_should_refresh_token_no_previous_refresh(self):
        """Test should_refresh_token when no previous refresh occurred."""
        assert self.refresh_manager.should_refresh_token() is True
    
    def test_should_refresh_token_recent_refresh(self):
        """Test should_refresh_token when refresh was recent."""
        self.refresh_manager.last_refresh = datetime.now() - timedelta(minutes=10)
        
        assert self.refresh_manager.should_refresh_token() is False
    
    def test_should_refresh_token_old_refresh(self):
        """Test should_refresh_token when refresh was old."""
        self.refresh_manager.last_refresh = datetime.now() - timedelta(minutes=35)
        
        assert self.refresh_manager.should_refresh_token() is True
    
    @patch('revos.auth.tokens.invalidate_revos_token')
    @patch('revos.auth.tokens.get_revos_token')
    def test_refresh_extractor_success(self, mock_get_token, mock_invalidate):
        """Test successful token refresh."""
        mock_get_token.return_value = "new-test-token"
        
        result = self.refresh_manager.refresh_extractor()
        
        assert result is True
        assert self.refresh_manager.last_refresh is not None
        mock_invalidate.assert_called_once()
        mock_get_token.assert_called_once_with(force_refresh=True)
    
    @patch('revos.auth.tokens.invalidate_revos_token')
    @patch('revos.auth.tokens.get_revos_token')
    def test_refresh_extractor_failure(self, mock_get_token, mock_invalidate):
        """Test token refresh failure."""
        mock_get_token.side_effect = Exception("Token fetch failed")
        
        result = self.refresh_manager.refresh_extractor()
        
        assert result is False
        assert self.refresh_manager.last_refresh is None
        mock_invalidate.assert_called_once()
        mock_get_token.assert_called_once_with(force_refresh=True)
    
    @patch('revos.auth.tokens.invalidate_revos_token')
    def test_refresh_extractor_exception(self, mock_invalidate):
        """Test token refresh with exception."""
        mock_invalidate.side_effect = Exception("Invalidation failed")
        
        with pytest.raises(RevosTokenError, match="Token refresh failed"):
            self.refresh_manager.refresh_extractor()
    
    @patch('revos.auth.tokens.get_revos_token')
    def test_test_token_acquisition_success(self, mock_get_token):
        """Test successful token acquisition test."""
        mock_get_token.return_value = "valid-token"
        
        result = self.refresh_manager._test_token_acquisition()
        
        assert result is True
        mock_get_token.assert_called_once_with(force_refresh=True)
    
    @patch('revos.auth.tokens.get_revos_token')
    def test_test_token_acquisition_invalid_token(self, mock_get_token):
        """Test token acquisition test with invalid token."""
        mock_get_token.return_value = None
        
        result = self.refresh_manager._test_token_acquisition()
        
        assert result is False
    
    @patch('revos.auth.tokens.get_revos_token')
    def test_test_token_acquisition_empty_token(self, mock_get_token):
        """Test token acquisition test with empty token."""
        mock_get_token.return_value = ""
        
        result = self.refresh_manager._test_token_acquisition()
        
        assert result is False
    
    @patch('revos.auth.tokens.get_revos_token')
    def test_test_token_acquisition_exception(self, mock_get_token):
        """Test token acquisition test with exception."""
        mock_get_token.side_effect = Exception("Token fetch failed")
        
        result = self.refresh_manager._test_token_acquisition()
        
        assert result is False


class TestBackgroundTokenManager:
    """Test cases for BackgroundTokenManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.background_manager = BackgroundTokenManager(refresh_interval_minutes=30)
    
    def test_init(self):
        """Test BackgroundTokenManager initialization."""
        assert self.background_manager.refresh_manager is not None
        assert self.background_manager._background_task is None
        assert self.background_manager._running is False
    
    def test_is_running_initial_state(self):
        """Test is_running in initial state."""
        assert self.background_manager.is_running() is False
    
    def test_is_running_after_start(self):
        """Test is_running after starting service."""
        self.background_manager._running = True
        assert self.background_manager.is_running() is True
    
    def test_get_last_refresh_time(self):
        """Test get_last_refresh_time."""
        test_time = datetime.now()
        self.background_manager.refresh_manager.last_refresh = test_time
        
        result = self.background_manager.get_last_refresh_time()
        
        assert result == test_time
    
    def test_get_last_refresh_time_none(self):
        """Test get_last_refresh_time when no refresh occurred."""
        result = self.background_manager.get_last_refresh_time()
        
        assert result is None
    
    @patch.object(TokenRefreshManager, 'refresh_extractor')
    def test_force_refresh_success(self, mock_refresh):
        """Test successful force refresh."""
        mock_refresh.return_value = True
        
        result = self.background_manager.force_refresh()
        
        assert result is True
        mock_refresh.assert_called_once()
    
    @patch.object(TokenRefreshManager, 'refresh_extractor')
    def test_force_refresh_failure(self, mock_refresh):
        """Test force refresh failure."""
        mock_refresh.return_value = False
        
        result = self.background_manager.force_refresh()
        
        assert result is False
        mock_refresh.assert_called_once()
    
    @patch.object(TokenRefreshManager, 'refresh_extractor')
    def test_force_refresh_exception(self, mock_refresh):
        """Test force refresh with exception."""
        mock_refresh.side_effect = Exception("Refresh failed")
        
        result = self.background_manager.force_refresh()
        
        assert result is False
        mock_refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_background_refresh_success(self):
        """Test successful background refresh service start."""
        with patch.object(self.background_manager, '_background_refresh_loop') as mock_loop:
            mock_task = Mock()
            with patch('asyncio.create_task', return_value=mock_task):
                await self.background_manager.start_background_refresh()
                
                assert self.background_manager._running is True
                assert self.background_manager._background_task == mock_task
    
    @pytest.mark.asyncio
    async def test_start_background_refresh_already_running(self):
        """Test starting background refresh when already running."""
        self.background_manager._running = True
        
        await self.background_manager.start_background_refresh()
        
        # Should not raise an error, just log a warning
        assert self.background_manager._running is True
    
    @pytest.mark.asyncio
    async def test_start_background_refresh_failure(self):
        """Test background refresh service start failure."""
        with patch('asyncio.create_task', side_effect=Exception("Task creation failed")):
            with pytest.raises(RevosTokenError, match="Background service startup failed"):
                await self.background_manager.start_background_refresh()
            
            assert self.background_manager._running is False
    
    @pytest.mark.asyncio
    async def test_stop_background_refresh_success(self):
        """Test successful background refresh service stop."""
        mock_task = Mock()
        self.background_manager._background_task = mock_task
        self.background_manager._running = True
        
        await self.background_manager.stop_background_refresh()
        
        assert self.background_manager._running is False
        mock_task.cancel.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_background_refresh_not_running(self):
        """Test stopping background refresh when not running."""
        await self.background_manager.stop_background_refresh()
        
        # Should not raise an error, just log a warning
        assert self.background_manager._running is False
    
    @pytest.mark.asyncio
    async def test_background_refresh_loop(self):
        """Test background refresh loop."""
        self.background_manager._running = True
        
        with patch.object(self.background_manager.refresh_manager, 'should_refresh_token') as mock_should_refresh:
            with patch.object(self.background_manager.refresh_manager, 'refresh_extractor') as mock_refresh:
                mock_should_refresh.return_value = True
                mock_refresh.return_value = True
                
                # Mock sleep to prevent actual waiting and make it raise CancelledError
                with patch('asyncio.sleep') as mock_sleep:
                    # Make the loop run once and then raise CancelledError
                    mock_sleep.side_effect = asyncio.CancelledError()
                    
                    # The loop should handle CancelledError gracefully and not re-raise it
                    await self.background_manager._background_refresh_loop()
                    
                    mock_should_refresh.assert_called()
                    mock_refresh.assert_called()
    
    @pytest.mark.asyncio
    async def test_background_refresh_loop_error_handling(self):
        """Test background refresh loop error handling."""
        self.background_manager._running = True
        
        with patch.object(self.background_manager.refresh_manager, 'should_refresh_token') as mock_should_refresh:
            mock_should_refresh.side_effect = Exception("Check failed")
            
            # Mock sleep to prevent actual waiting and make it raise CancelledError
            with patch('asyncio.sleep') as mock_sleep:
                # Make the loop run once and then raise CancelledError
                mock_sleep.side_effect = asyncio.CancelledError()
                
                # The loop should handle both the exception and CancelledError gracefully
                await self.background_manager._background_refresh_loop()
                
                # Should handle the error gracefully and continue


class TestTokenManager:
    """Test cases for TokenManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.token_manager = TokenManager()
    
    def test_init(self):
        """Test TokenManager initialization."""
        assert self.token_manager.refresh_manager is not None
        assert self.token_manager.background_manager is not None
    
    @patch.object(BackgroundTokenManager, 'start_background_refresh')
    @pytest.mark.asyncio
    async def test_start_background_service(self, mock_start):
        """Test starting background service."""
        await self.token_manager.start_background_service()
        
        mock_start.assert_called_once()
    
    @patch.object(BackgroundTokenManager, 'stop_background_refresh')
    @pytest.mark.asyncio
    async def test_stop_background_service(self, mock_stop):
        """Test stopping background service."""
        await self.token_manager.stop_background_service()
        
        mock_stop.assert_called_once()
    
    @patch.object(BackgroundTokenManager, 'is_running')
    def test_is_background_service_running(self, mock_is_running):
        """Test checking if background service is running."""
        mock_is_running.return_value = True
        
        result = self.token_manager.is_background_service_running()
        
        assert result is True
        mock_is_running.assert_called_once()
    
    @patch.object(TokenRefreshManager, 'get_last_refresh_time')
    def test_get_last_refresh_time(self, mock_get_time):
        """Test getting last refresh time."""
        test_time = datetime.now()
        mock_get_time.return_value = test_time
        
        result = self.token_manager.get_last_refresh_time()
        
        assert result == test_time
        mock_get_time.assert_called_once()
    
    @patch.object(BackgroundTokenManager, 'force_refresh')
    def test_force_refresh(self, mock_force_refresh):
        """Test forcing refresh."""
        mock_force_refresh.return_value = True
        
        result = self.token_manager.force_refresh()
        
        assert result is True
        mock_force_refresh.assert_called_once()
    
    @patch.object(TokenRefreshManager, 'should_refresh_token')
    def test_should_refresh_token(self, mock_should_refresh):
        """Test checking if token should be refreshed."""
        mock_should_refresh.return_value = True
        
        result = self.token_manager.should_refresh_token()
        
        assert result is True
        mock_should_refresh.assert_called_once()


class TestTokenIntegration:
    """Integration tests for token management."""
    
    @patch('revos.auth.tokens.get_revos_token')
    @patch('revos.auth.tokens.invalidate_revos_token')
    def test_refresh_workflow(self, mock_invalidate, mock_get_token):
        """Test complete token refresh workflow."""
        mock_get_token.return_value = "refreshed-token"
        
        refresh_manager = TokenRefreshManager()
        result = refresh_manager.refresh_extractor()
        
        assert result is True
        assert refresh_manager.last_refresh is not None
        mock_invalidate.assert_called_once()
        mock_get_token.assert_called_once_with(force_refresh=True)
    
    @pytest.mark.asyncio
    async def test_background_service_workflow(self):
        """Test complete background service workflow."""
        background_manager = BackgroundTokenManager()
        
        # Start service
        with patch.object(background_manager, '_background_refresh_loop'):
            await background_manager.start_background_refresh()
            assert background_manager.is_running() is True
        
        # Stop service
        await background_manager.stop_background_refresh()
        assert background_manager.is_running() is False
    
    @patch.object(TokenRefreshManager, 'refresh_extractor')
    def test_token_manager_workflow(self, mock_refresh):
        """Test complete token manager workflow."""
        mock_refresh.return_value = True
        
        token_manager = TokenManager()
        
        # Test refresh
        result = token_manager.force_refresh()
        assert result is True
        
        # Test should refresh
        with patch.object(token_manager.refresh_manager, 'should_refresh_token', return_value=True):
            should_refresh = token_manager.should_refresh_token()
            assert should_refresh is True
