"""Unit tests for comprehensive error handling."""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
import shutil

import yt_dlp

from src.errors import (
    ErrorHandler, YouTubeExtractorError, NetworkError, FileSystemError, 
    ConversionError, URLValidationError
)


class TestYouTubeExtractorError(unittest.TestCase):
    """Test base exception class."""
    
    def test_error_with_message_only(self):
        """Test error creation with message only."""
        error = YouTubeExtractorError("Test error")
        
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.suggestions, [])
    
    def test_error_with_suggestions(self):
        """Test error creation with suggestions."""
        suggestions = ["Try this", "Or this"]
        error = YouTubeExtractorError("Test error", suggestions)
        
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.suggestions, suggestions)


class TestErrorHandler(unittest.TestCase):
    """Test ErrorHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.error_handler = ErrorHandler()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_url_empty(self):
        """Test URL validation with empty URL."""
        with self.assertRaises(URLValidationError) as context:
            self.error_handler.validate_url("")
        
        self.assertIn("URL cannot be empty", str(context.exception))
        self.assertIn("Provide a valid YouTube", context.exception.suggestions[0])
    
    def test_validate_url_none(self):
        """Test URL validation with None URL."""
        with self.assertRaises(URLValidationError) as context:
            self.error_handler.validate_url(None)
        
        self.assertIn("URL cannot be empty", str(context.exception))
    
    def test_validate_url_no_protocol(self):
        """Test URL validation without protocol."""
        with self.assertRaises(URLValidationError) as context:
            self.error_handler.validate_url("youtube.com/watch?v=test")
        
        self.assertIn("URL must start with http", str(context.exception))
        self.assertIn("includes the protocol", context.exception.suggestions[0])
    
    def test_validate_url_not_youtube(self):
        """Test URL validation with non-YouTube URL."""
        with self.assertRaises(URLValidationError) as context:
            self.error_handler.validate_url("https://example.com/video")
        
        self.assertIn("URL must be a YouTube URL", str(context.exception))
        self.assertIn("youtube.com or youtu.be", context.exception.suggestions[0])
    
    @patch('src.errors.yt_dlp.YoutubeDL')
    def test_validate_url_private_video(self, mock_ydl_class):
        """Test URL validation with private video."""
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = yt_dlp.DownloadError("Video is private")
        
        with self.assertRaises(URLValidationError) as context:
            self.error_handler.validate_url("https://youtube.com/watch?v=private")
        
        self.assertIn("not accessible", str(context.exception))
        self.assertIn("video/playlist is public", context.exception.suggestions[0])
    
    @patch('src.errors.yt_dlp.YoutubeDL')
    def test_validate_url_network_error(self, mock_ydl_class):
        """Test URL validation with network error."""
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = yt_dlp.DownloadError("Network connection failed")
        
        with self.assertRaises(NetworkError) as context:
            self.error_handler.validate_url("https://youtube.com/watch?v=test")
        
        self.assertIn("Network error", str(context.exception))
        self.assertIn("internet connection", context.exception.suggestions[0])
    
    @patch('src.errors.yt_dlp.YoutubeDL')
    def test_validate_url_success(self, mock_ydl_class):
        """Test successful URL validation."""
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {"title": "Test Video"}
        
        # Should not raise any exception
        self.error_handler.validate_url("https://youtube.com/watch?v=test")
    
    def test_validate_file_system_success(self):
        """Test successful file system validation."""
        # Should not raise any exception
        self.error_handler.validate_file_system(self.temp_dir)
    
    def test_validate_file_system_create_directory(self):
        """Test file system validation with directory creation."""
        new_dir = os.path.join(self.temp_dir, "new_folder")
        
        # Should not raise any exception and should create directory
        self.error_handler.validate_file_system(new_dir)
        self.assertTrue(os.path.exists(new_dir))
    
    @patch('src.errors.os.access')
    def test_validate_file_system_no_write_permission(self, mock_access):
        """Test file system validation without write permission."""
        mock_access.return_value = False
        
        with self.assertRaises(FileSystemError) as context:
            self.error_handler.validate_file_system(self.temp_dir)
        
        self.assertIn("No write permission", str(context.exception))
        self.assertIn("directory permissions", context.exception.suggestions[0])
    
    @patch('src.errors.shutil.disk_usage')
    def test_validate_file_system_insufficient_space(self, mock_disk_usage):
        """Test file system validation with insufficient disk space."""
        # Mock disk usage to return very little free space
        mock_usage = Mock()
        mock_usage.free = 10 * 1024 * 1024  # 10 MB
        mock_disk_usage.return_value = mock_usage
        
        with self.assertRaises(FileSystemError) as context:
            self.error_handler.validate_file_system(self.temp_dir, required_space_mb=50)
        
        self.assertIn("Insufficient disk space", str(context.exception))
        self.assertIn("Free up disk space", context.exception.suggestions[0])
    
    def test_validate_file_system_invalid_path(self):
        """Test file system validation with invalid path."""
        invalid_path = "/invalid/path/that/cannot/be/created"
        
        with self.assertRaises(FileSystemError) as context:
            self.error_handler.validate_file_system(invalid_path)
        
        self.assertIn("Cannot create output directory", str(context.exception))
    
    @patch('src.errors.shutil.which')
    def test_validate_ffmpeg_success(self, mock_which):
        """Test successful ffmpeg validation."""
        mock_which.return_value = "/usr/bin/ffmpeg"
        
        # Should not raise any exception
        self.error_handler.validate_ffmpeg()
    
    @patch('src.errors.shutil.which')
    def test_validate_ffmpeg_not_found(self, mock_which):
        """Test ffmpeg validation when not found."""
        mock_which.return_value = None
        
        with self.assertRaises(ConversionError) as context:
            self.error_handler.validate_ffmpeg()
        
        self.assertIn("ffmpeg not found", str(context.exception))
        self.assertIn("Install ffmpeg", context.exception.suggestions[0])
    
    def test_handle_network_error_timeout(self):
        """Test network error handling for timeout."""
        original_error = Exception("Connection timeout")
        
        network_error = self.error_handler.handle_network_error(
            original_error, "video download", max_retries=3
        )
        
        self.assertIsInstance(network_error, NetworkError)
        self.assertIn("Network error during video download", str(network_error))
        self.assertIn("connection is stable", network_error.suggestions[3])  # After base suggestions
        self.assertIn("retried 3 times", network_error.suggestions[-1])
    
    def test_handle_network_error_connection_refused(self):
        """Test network error handling for connection refused."""
        original_error = Exception("Connection refused")
        
        network_error = self.error_handler.handle_network_error(
            original_error, "playlist download"
        )
        
        self.assertIn("firewall settings", network_error.suggestions[3])  # After base suggestions
        self.assertIn("VPN", network_error.suggestions[4])
    
    def test_handle_network_error_dns(self):
        """Test network error handling for DNS issues."""
        original_error = Exception("DNS resolution failed")
        
        network_error = self.error_handler.handle_network_error(
            original_error, "URL validation"
        )
        
        self.assertIn("DNS settings", network_error.suggestions[3])  # After base suggestions
        self.assertIn("DNS server", network_error.suggestions[4])
    
    def test_handle_conversion_error_permission(self):
        """Test conversion error handling for permission issues."""
        original_error = Exception("Permission denied")
        
        conversion_error = self.error_handler.handle_conversion_error(
            original_error, "input.wav", "output.mp3"
        )
        
        self.assertIsInstance(conversion_error, ConversionError)
        self.assertIn("Audio conversion failed", str(conversion_error))
        self.assertIn("file permissions", conversion_error.suggestions[3])  # After base suggestions
    
    def test_handle_conversion_error_disk_space(self):
        """Test conversion error handling for disk space issues."""
        original_error = Exception("No space left on device")
        
        conversion_error = self.error_handler.handle_conversion_error(
            original_error, "input.wav", "output.mp3"
        )
        
        self.assertIn("Free up disk space", conversion_error.suggestions[3])  # After base suggestions
        self.assertIn("different output directory", conversion_error.suggestions[4])
    
    def test_handle_conversion_error_codec(self):
        """Test conversion error handling for codec issues."""
        original_error = Exception("Unsupported codec")
        
        conversion_error = self.error_handler.handle_conversion_error(
            original_error, "input.wav", "output.mp3"
        )
        
        self.assertIn("format may not be supported", conversion_error.suggestions[3])  # After base suggestions
        self.assertIn("original format", conversion_error.suggestions[4])
    
    def test_handle_file_system_error_permission(self):
        """Test file system error handling for permission issues."""
        original_error = PermissionError("Permission denied")
        
        fs_error = self.error_handler.handle_file_system_error(
            original_error, "creating directory", "/test/path"
        )
        
        self.assertIsInstance(fs_error, FileSystemError)
        self.assertIn("File system error during creating directory", str(fs_error))
        self.assertIn("file/directory permissions", fs_error.suggestions[0])
    
    def test_handle_file_system_error_not_found(self):
        """Test file system error handling for file not found."""
        original_error = FileNotFoundError("File not found")
        
        fs_error = self.error_handler.handle_file_system_error(
            original_error, "reading file", "/test/file.txt"
        )
        
        self.assertIn("path exists", fs_error.suggestions[0])
        self.assertIn("file/directory name", fs_error.suggestions[1])
    
    def test_handle_file_system_error_file_exists(self):
        """Test file system error handling for file exists."""
        original_error = FileExistsError("File already exists")
        
        fs_error = self.error_handler.handle_file_system_error(
            original_error, "creating file", "/test/file.txt"
        )
        
        self.assertIn("File already exists", fs_error.suggestions[0])
        self.assertIn("different filename", fs_error.suggestions[1])
    
    def test_get_retry_delay_exponential_backoff(self):
        """Test retry delay calculation with exponential backoff."""
        # Test exponential backoff
        delay_0 = self.error_handler.get_retry_delay(0)  # 1.0 * 2^0 = 1.0
        delay_1 = self.error_handler.get_retry_delay(1)  # 1.0 * 2^1 = 2.0
        delay_2 = self.error_handler.get_retry_delay(2)  # 1.0 * 2^2 = 4.0
        
        self.assertEqual(delay_0, 1.0)
        self.assertEqual(delay_1, 2.0)
        self.assertEqual(delay_2, 4.0)
    
    def test_get_retry_delay_max_limit(self):
        """Test retry delay with maximum limit."""
        # Test that delay doesn't exceed max_delay
        delay = self.error_handler.get_retry_delay(10, base_delay=1.0, max_delay=5.0)
        self.assertEqual(delay, 5.0)
    
    def test_get_retry_delay_custom_base(self):
        """Test retry delay with custom base delay."""
        delay = self.error_handler.get_retry_delay(1, base_delay=0.5)  # 0.5 * 2^1 = 1.0
        self.assertEqual(delay, 1.0)


class TestSpecificErrorTypes(unittest.TestCase):
    """Test specific error type behaviors."""
    
    def test_network_error_inheritance(self):
        """Test NetworkError inherits from YouTubeExtractorError."""
        error = NetworkError("Network issue", ["Check connection"])
        
        self.assertIsInstance(error, YouTubeExtractorError)
        self.assertEqual(str(error), "Network issue")
        self.assertEqual(error.suggestions, ["Check connection"])
    
    def test_file_system_error_inheritance(self):
        """Test FileSystemError inherits from YouTubeExtractorError."""
        error = FileSystemError("File issue", ["Check permissions"])
        
        self.assertIsInstance(error, YouTubeExtractorError)
        self.assertEqual(str(error), "File issue")
        self.assertEqual(error.suggestions, ["Check permissions"])
    
    def test_conversion_error_inheritance(self):
        """Test ConversionError inherits from YouTubeExtractorError."""
        error = ConversionError("Conversion issue", ["Check ffmpeg"])
        
        self.assertIsInstance(error, YouTubeExtractorError)
        self.assertEqual(str(error), "Conversion issue")
        self.assertEqual(error.suggestions, ["Check ffmpeg"])
    
    def test_url_validation_error_inheritance(self):
        """Test URLValidationError inherits from YouTubeExtractorError."""
        error = URLValidationError("URL issue", ["Check URL format"])
        
        self.assertIsInstance(error, YouTubeExtractorError)
        self.assertEqual(str(error), "URL issue")
        self.assertEqual(error.suggestions, ["Check URL format"])


if __name__ == "__main__":
    unittest.main()