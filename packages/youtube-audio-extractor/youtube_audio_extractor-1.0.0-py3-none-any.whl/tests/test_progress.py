"""Tests for progress tracking and user feedback functionality."""

import pytest
from unittest.mock import Mock, patch, call
import time
from io import StringIO
import sys

from src.progress import ProgressTracker, PlaylistProgressTracker, ProgressInfo


class TestProgressInfo:
    """Test ProgressInfo dataclass."""
    
    def test_progress_info_creation(self):
        """Test creating ProgressInfo with default values."""
        info = ProgressInfo("test.mp3")
        
        assert info.filename == "test.mp3"
        assert info.total_bytes is None
        assert info.downloaded_bytes == 0
        assert info.speed is None
        assert info.eta is None
        assert info.status == "downloading"
    
    def test_progress_info_with_values(self):
        """Test creating ProgressInfo with specific values."""
        info = ProgressInfo(
            filename="test.mp3",
            total_bytes=1000000,
            downloaded_bytes=500000,
            speed=1024.5,
            eta=30,
            status="downloading"
        )
        
        assert info.filename == "test.mp3"
        assert info.total_bytes == 1000000
        assert info.downloaded_bytes == 500000
        assert info.speed == 1024.5
        assert info.eta == 30
        assert info.status == "downloading"


class TestProgressTracker:
    """Test ProgressTracker functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = ProgressTracker(verbose=False)
        self.verbose_tracker = ProgressTracker(verbose=True)
    
    @patch('click.echo')
    def test_show_stage_message_simple(self, mock_echo):
        """Test showing simple stage message."""
        self.tracker.show_stage_message("Downloading")
        
        mock_echo.assert_called_once_with("Downloading")
    
    @patch('click.echo')
    def test_show_stage_message_with_details(self, mock_echo):
        """Test showing stage message with details."""
        self.tracker.show_stage_message("Downloading", "video.mp3")
        
        mock_echo.assert_called_once_with("Downloading: video.mp3")
    
    @patch('click.echo')
    @patch('time.strftime')
    def test_show_stage_message_verbose(self, mock_strftime, mock_echo):
        """Test showing stage message in verbose mode."""
        mock_strftime.return_value = "12:34:56"
        
        self.verbose_tracker.show_stage_message("Downloading", "video.mp3")
        
        mock_echo.assert_called_once_with("[12:34:56] Downloading: video.mp3")
    
    @patch('click.echo')
    def test_show_video_info(self, mock_echo):
        """Test displaying video information."""
        self.tracker.show_video_info("Test Video", "Test Channel", 180)
        
        # Check that the calls were made (ignoring ANSI color codes)
        assert mock_echo.call_count == 3
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("Test Video" in call for call in calls)
        assert any("Test Channel" in call for call in calls)
        assert any("3:00" in call for call in calls)
    
    @patch('click.echo')
    def test_show_video_info_no_duration(self, mock_echo):
        """Test displaying video information without duration."""
        self.tracker.show_video_info("Test Video", "Test Channel")
        
        # Check that the calls were made (ignoring ANSI color codes)
        assert mock_echo.call_count == 2
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("Test Video" in call for call in calls)
        assert any("Test Channel" in call for call in calls)
    
    @patch('click.echo')
    def test_show_playlist_info(self, mock_echo):
        """Test displaying playlist information."""
        self.tracker.show_playlist_info("Test Playlist", "Test Channel", 5)
        
        # Check that the calls were made (ignoring ANSI color codes)
        assert mock_echo.call_count == 3
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("Test Playlist" in call for call in calls)
        assert any("Test Channel" in call for call in calls)
        assert any("5" in call for call in calls)
    
    @patch('click.echo')
    def test_show_error_with_suggestions(self, mock_echo):
        """Test displaying error with suggestions."""
        suggestions = ["Check internet", "Try again"]
        
        self.tracker.show_error_with_suggestions("Download failed", suggestions)
        
        # Check that the calls were made (ignoring ANSI color codes)
        assert mock_echo.call_count == 4
        calls = [str(call) for call in mock_echo.call_args_list]
        assert any("Download failed" in call and "err=True" in call for call in calls)
        assert any("Troubleshooting suggestions" in call for call in calls)
        assert any("Check internet" in call for call in calls)
        assert any("Try again" in call for call in calls)
    
    @patch('click.echo')
    def test_show_error_no_suggestions(self, mock_echo):
        """Test displaying error without suggestions."""
        self.tracker.show_error_with_suggestions("Download failed")
        
        # Check that error was displayed (ignoring ANSI color codes)
        assert mock_echo.call_count == 1
        call_str = str(mock_echo.call_args)
        assert "Download failed" in call_str and "err=True" in call_str
    
    @patch('click.confirm')
    def test_confirm_large_playlist_small(self, mock_confirm):
        """Test confirmation for small playlist (should not ask)."""
        result = self.tracker.confirm_large_playlist(5)
        
        assert result is True
        mock_confirm.assert_not_called()
    
    @patch('click.confirm')
    def test_confirm_large_playlist_large_accept(self, mock_confirm):
        """Test confirmation for large playlist (user accepts)."""
        mock_confirm.return_value = True
        
        result = self.tracker.confirm_large_playlist(15)
        
        assert result is True
        mock_confirm.assert_called_once_with(
            "This playlist contains 15 videos. Continue?",
            default=True
        )
    
    @patch('click.confirm')
    def test_confirm_large_playlist_large_decline(self, mock_confirm):
        """Test confirmation for large playlist (user declines)."""
        mock_confirm.return_value = False
        
        result = self.tracker.confirm_large_playlist(15)
        
        assert result is False
        mock_confirm.assert_called_once()
    
    def test_create_yt_dlp_hook(self):
        """Test creating yt-dlp progress hook."""
        hook = self.tracker.create_yt_dlp_hook()
        
        assert callable(hook)
    
    @patch('click.echo')
    @patch('sys.stdout.flush')
    def test_yt_dlp_hook_downloading(self, mock_flush, mock_echo):
        """Test yt-dlp hook during download."""
        hook = self.tracker.create_yt_dlp_hook()
        
        download_data = {
            'status': 'downloading',
            'filename': 'test.mp3',
            'total_bytes': 1000000,
            'downloaded_bytes': 500000,
            'speed': 1024,
            'eta': 30
        }
        
        hook(download_data)
        
        # Should show progress
        mock_echo.assert_called()
        mock_flush.assert_called_once()
    
    @patch('click.echo')
    def test_yt_dlp_hook_finished(self, mock_echo):
        """Test yt-dlp hook when download finishes."""
        hook = self.tracker.create_yt_dlp_hook()
        
        download_data = {
            'status': 'finished',
            'filename': 'test.mp3'
        }
        
        hook(download_data)
        
        # Should show completion message
        mock_echo.assert_called()
    
    @patch('click.echo')
    def test_yt_dlp_hook_error(self, mock_echo):
        """Test yt-dlp hook when download errors."""
        hook = self.tracker.create_yt_dlp_hook()
        
        download_data = {
            'status': 'error',
            'error': 'Network error'
        }
        
        hook(download_data)
        
        # Should show error message
        mock_echo.assert_called()
    
    @patch('click.echo')
    def test_show_processing_summary_single_video(self, mock_echo):
        """Test showing summary for single video processing."""
        results = {
            'title': 'Test Video',
            'output_path': '/path/to/test.mp3'
        }
        
        self.tracker.show_processing_summary(results)
        
        # Should show single video summary
        mock_echo.assert_called()
        calls = mock_echo.call_args_list
        assert any("PROCESSING COMPLETE" in str(call) for call in calls)
        assert any("Test Video" in str(call) for call in calls)
    
    @patch('click.echo')
    def test_show_processing_summary_playlist(self, mock_echo):
        """Test showing summary for playlist processing."""
        results = {
            'playlist_title': 'Test Playlist',
            'playlist_folder': '/path/to/playlist',
            'total_videos': 5,
            'success_count': 4,
            'failure_count': 1,
            'successful_downloads': [
                {'title': 'Video 1'},
                {'title': 'Video 2'}
            ],
            'failed_downloads': [
                {'title': 'Video 3', 'error': 'Network error'}
            ]
        }
        
        self.tracker.show_processing_summary(results)
        
        # Should show playlist summary
        mock_echo.assert_called()
        calls = mock_echo.call_args_list
        assert any("PROCESSING COMPLETE" in str(call) for call in calls)
        assert any("Test Playlist" in str(call) for call in calls)
        assert any("Total videos: 5" in str(call) for call in calls)


class TestPlaylistProgressTracker:
    """Test PlaylistProgressTracker functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = PlaylistProgressTracker(5, verbose=False)
        self.verbose_tracker = PlaylistProgressTracker(5, verbose=True)
    
    @patch('click.echo')
    @patch('time.time')
    def test_start_video(self, mock_time, mock_echo):
        """Test starting video processing."""
        mock_time.return_value = 1000.0
        
        self.tracker.start_video(1, "Test Video")
        
        assert self.tracker.current_video == 1
        mock_echo.assert_called()
    
    @patch('click.echo')
    @patch('time.time')
    def test_start_video_with_eta(self, mock_time, mock_echo):
        """Test starting video with ETA calculation."""
        # Set up time progression
        self.verbose_tracker.start_time = 1000.0
        mock_time.return_value = 1060.0  # 60 seconds later
        
        self.verbose_tracker.start_video(2, "Test Video 2")
        
        # Should show ETA
        mock_echo.assert_called()
        calls = mock_echo.call_args_list
        assert any("ETA:" in str(call) for call in calls)
    
    @patch('click.echo')
    def test_video_success(self, mock_echo):
        """Test marking video as successful."""
        self.tracker.video_success("Test Video", "/path/to/test.mp3")
        
        assert self.tracker.successful == 1
        call_str = str(mock_echo.call_args)
        assert "Success" in call_str and "/path/to/test.mp3" in call_str
    
    @patch('click.echo')
    def test_video_failed(self, mock_echo):
        """Test marking video as failed."""
        self.tracker.video_failed("Test Video", "Network error")
        
        assert self.tracker.failed == 1
        call_str = str(mock_echo.call_args)
        assert "Failed" in call_str
    
    @patch('click.echo')
    def test_video_failed_verbose(self, mock_echo):
        """Test marking video as failed in verbose mode."""
        self.verbose_tracker.video_failed("Test Video", "Network error")
        
        assert self.verbose_tracker.failed == 1
        call_str = str(mock_echo.call_args)
        assert "Failed" in call_str and "Network error" in call_str
    
    @patch('time.time')
    def test_get_summary(self, mock_time):
        """Test getting processing summary."""
        # Set up initial state
        self.tracker.start_time = 1000.0
        self.tracker.successful = 3
        self.tracker.failed = 2
        mock_time.return_value = 1120.0  # 120 seconds later
        
        summary = self.tracker.get_summary()
        
        assert summary['total_videos'] == 5
        assert summary['successful'] == 3
        assert summary['failed'] == 2
        assert summary['elapsed_time'] == 120.0
        assert summary['success_rate'] == 60.0


class TestProgressTrackerIntegration:
    """Integration tests for progress tracking."""
    
    @patch('click.echo')
    @patch('sys.stdout.flush')
    def test_download_progress_display(self, mock_flush, mock_echo):
        """Test complete download progress display."""
        tracker = ProgressTracker(verbose=False)
        hook = tracker.create_yt_dlp_hook()
        
        # Simulate download progress
        download_data = {
            'status': 'downloading',
            'filename': 'test.mp3',
            'total_bytes': 1000000,
            'downloaded_bytes': 250000,
            'speed': 1024,
            'eta': 45
        }
        hook(download_data)
        
        # Update progress
        download_data['downloaded_bytes'] = 500000
        download_data['eta'] = 30
        hook(download_data)
        
        # Finish download
        download_data['status'] = 'finished'
        hook(download_data)
        
        # Should have called echo multiple times for progress updates
        assert mock_echo.call_count >= 2
        mock_flush.assert_called()
    
    @patch('click.echo')
    def test_verbose_progress_display(self, mock_echo):
        """Test verbose progress display."""
        tracker = ProgressTracker(verbose=True)
        hook = tracker.create_yt_dlp_hook()
        
        download_data = {
            'status': 'downloading',
            'filename': 'test.mp3',
            'total_bytes': 1000000,
            'downloaded_bytes': 500000,
            'speed': 2048,  # 2 KB/s
            'eta': 30
        }
        
        hook(download_data)
        
        # Should show detailed progress with speed and ETA
        mock_echo.assert_called()
        call_args = str(mock_echo.call_args)
        assert "50.0%" in call_args
        assert "KB/s" in call_args
        assert "ETA:" in call_args
    
    def test_speed_formatting(self):
        """Test different speed formatting scenarios."""
        tracker = ProgressTracker(verbose=True)
        hook = tracker.create_yt_dlp_hook()
        
        # Test MB/s
        with patch('click.echo') as mock_echo:
            download_data = {
                'status': 'downloading',
                'filename': 'test.mp3',
                'total_bytes': 1000000,
                'downloaded_bytes': 500000,
                'speed': 2 * 1024 * 1024,  # 2 MB/s
                'eta': 30
            }
            hook(download_data)
            
            call_args = str(mock_echo.call_args)
            assert "MB/s" in call_args
        
        # Test KB/s
        with patch('click.echo') as mock_echo:
            download_data['speed'] = 1024  # 1 KB/s
            hook(download_data)
            
            call_args = str(mock_echo.call_args)
            assert "KB/s" in call_args
        
        # Test B/s
        with patch('click.echo') as mock_echo:
            download_data['speed'] = 512  # 512 B/s
            hook(download_data)
            
            call_args = str(mock_echo.call_args)
            assert "B/s" in call_args


if __name__ == '__main__':
    pytest.main([__file__])