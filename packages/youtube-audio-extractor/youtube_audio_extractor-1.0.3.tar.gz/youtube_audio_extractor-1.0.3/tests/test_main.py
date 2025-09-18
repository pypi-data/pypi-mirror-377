"""Integration tests for CLI functionality."""

import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import pytest
from click.testing import CliRunner

from src.main import main, setup_logging, validate_quality, validate_output_dir, validate_dependencies
from src.utils import VideoInfo, PlaylistInfo, ExtractionOptions


class TestCLIValidation:
    """Test CLI parameter validation functions."""
    
    def test_validate_quality_valid(self):
        """Test quality validation with valid values."""
        ctx = Mock()
        param = Mock()
        
        assert validate_quality(ctx, param, "128") == "128"
        assert validate_quality(ctx, param, "192") == "192"
        assert validate_quality(ctx, param, "320") == "320"
    
    def test_validate_quality_invalid(self):
        """Test quality validation with invalid values."""
        from click import BadParameter
        
        ctx = Mock()
        param = Mock()
        
        with pytest.raises(BadParameter):
            validate_quality(ctx, param, "256")
        
        with pytest.raises(BadParameter):
            validate_quality(ctx, param, "invalid")
    
    def test_validate_output_dir_valid(self):
        """Test output directory validation with valid paths."""
        ctx = Mock()
        param = Mock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Existing directory
            result = validate_output_dir(ctx, param, temp_dir)
            assert result == temp_dir
            
            # New directory that can be created
            new_dir = os.path.join(temp_dir, "new_folder")
            result = validate_output_dir(ctx, param, new_dir)
            assert result == new_dir
            assert os.path.exists(new_dir)
    
    def test_validate_output_dir_invalid(self):
        """Test output directory validation with invalid paths."""
        from click import BadParameter
        
        ctx = Mock()
        param = Mock()
        
        # Try to create directory in non-existent parent (should fail on most systems)
        with pytest.raises(BadParameter):
            validate_output_dir(ctx, param, "/non/existent/path/that/cannot/be/created")


class TestCLILogging:
    """Test CLI logging setup."""
    
    def test_setup_logging_verbose(self):
        """Test logging setup with verbose mode."""
        import logging
        
        setup_logging(verbose=True)
        logger = logging.getLogger()
        
        assert logger.level == logging.DEBUG
    
    def test_setup_logging_normal(self):
        """Test logging setup with normal mode."""
        import logging
        
        setup_logging(verbose=False)
        logger = logging.getLogger()
        
        assert logger.level == logging.INFO


class TestDependencyValidation:
    """Test dependency validation functionality."""
    
    @patch('src.main.AudioConverter')
    def test_validate_dependencies_success(self, mock_converter_class):
        """Test successful dependency validation."""
        # Setup mock
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        
        # Should not raise any exception
        validate_dependencies()
        
        # Verify AudioConverter was instantiated (ffmpeg check)
        mock_converter_class.assert_called_once()
    
    @patch('src.main.AudioConverter')
    def test_validate_dependencies_ffmpeg_missing(self, mock_converter_class):
        """Test dependency validation when ffmpeg is missing."""
        from src.errors import ConversionError
        
        # Setup mock to raise ConversionError
        mock_converter_class.side_effect = ConversionError(
            "ffmpeg not found in PATH",
            ["Install ffmpeg using your package manager"]
        )
        
        with pytest.raises(ConversionError):
            validate_dependencies()
    
    @patch('builtins.__import__')
    def test_validate_dependencies_python_package_missing(self, mock_import):
        """Test dependency validation when Python packages are missing."""
        # Setup mock to raise ImportError for yt_dlp
        def side_effect(name, *args, **kwargs):
            if name == 'yt_dlp':
                raise ImportError("No module named 'yt_dlp'")
            return Mock()
        
        mock_import.side_effect = side_effect
        
        with pytest.raises(ImportError) as exc_info:
            validate_dependencies()
        
        assert "Missing required Python packages" in str(exc_info.value)
        assert "yt_dlp" in str(exc_info.value)


class TestCLIIntegration:
    """Integration tests for the CLI interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock video info
        self.mock_video_info = VideoInfo(
            title="Test Video",
            uploader="Test Channel",
            duration=180,
            upload_date="20231201",
            url="https://www.youtube.com/watch?v=test123",
            id="test123"
        )
        
        # Mock playlist info
        self.mock_playlist_info = PlaylistInfo(
            title="Test Playlist",
            uploader="Test Channel",
            video_count=2,
            videos=[self.mock_video_info, self.mock_video_info]
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cli_help(self):
        """Test CLI help output."""
        result = self.runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert "Extract audio from YouTube videos and playlists" in result.output
        assert "--quality" in result.output
        assert "--output" in result.output
        assert "--verbose" in result.output
    
    def test_cli_version(self):
        """Test CLI version output."""
        result = self.runner.invoke(main, ['--version'])
        
        assert result.exit_code == 0
        assert "1.0.0" in result.output
    
    def test_cli_missing_url(self):
        """Test CLI with missing URL argument."""
        result = self.runner.invoke(main, [])
        
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Usage:" in result.output
    
    def test_cli_invalid_quality(self):
        """Test CLI with invalid quality parameter."""
        result = self.runner.invoke(main, ['--quality', '256', 'https://youtube.com/watch?v=test'])
        
        assert result.exit_code != 0
        assert "Quality must be one of" in result.output
    
    @patch('src.main.AudioConverter')
    @patch('src.main.ErrorHandler')
    def test_cli_invalid_url(self, mock_error_handler_class, mock_converter_class):
        """Test CLI with invalid YouTube URL."""
        # Setup mocks
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        
        from src.errors import URLValidationError
        mock_error_handler = Mock()
        mock_error_handler.validate_url.side_effect = URLValidationError(
            "URL must be a YouTube URL",
            ["Ensure the URL is from youtube.com or youtu.be"]
        )
        mock_error_handler_class.return_value = mock_error_handler
        
        result = self.runner.invoke(main, ['https://invalid-url.com'])
        
        assert result.exit_code == 1
        assert "URL must be a YouTube URL" in result.output
    
    @patch('src.main.validate_dependencies')
    @patch('src.main.ErrorHandler')
    @patch('src.main.AudioConverter')
    @patch('src.main.YouTubeExtractor')
    def test_cli_single_video_success(self, mock_extractor_class, mock_converter_class, mock_error_handler_class, mock_validate_deps):
        """Test successful single video extraction."""
        # Setup mocks
        mock_validate_deps.return_value = None
        
        mock_error_handler = Mock()
        mock_error_handler.validate_url.return_value = True
        mock_error_handler_class.return_value = mock_error_handler
        
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        
        mock_extractor = Mock()
        mock_extractor.is_playlist_url.return_value = False
        mock_extractor.get_video_info.return_value = self.mock_video_info
        mock_extractor.extract_video_audio.return_value = os.path.join(self.temp_dir, "test.mp3")
        mock_extractor_class.return_value = mock_extractor
        
        result = self.runner.invoke(main, [
            '--output', self.temp_dir,
            '--quality', '192',
            'https://youtube.com/watch?v=test'
        ])
        
        assert result.exit_code == 0
        assert "PROCESSING COMPLETE" in result.output
        assert "Successfully processed" in result.output
    
    @patch('src.main.validate_dependencies')
    @patch('src.main.ErrorHandler')
    @patch('src.main.AudioConverter')
    @patch('src.main.YouTubeExtractor')
    def test_cli_single_video_with_metadata(self, mock_extractor_class, mock_converter_class, mock_error_handler_class, mock_validate_deps):
        """Test single video extraction with metadata embedding."""
        # Setup mocks
        mock_validate_deps.return_value = None
        
        mock_error_handler = Mock()
        mock_error_handler.validate_url.return_value = True
        mock_error_handler_class.return_value = mock_error_handler
        
        mock_converter = Mock()
        mock_converter.embed_metadata.return_value = True
        mock_converter_class.return_value = mock_converter
        
        mock_extractor = Mock()
        mock_extractor.is_playlist_url.return_value = False
        mock_extractor.get_video_info.return_value = self.mock_video_info
        mock_extractor.extract_video_audio.return_value = os.path.join(self.temp_dir, "test.mp3")
        mock_extractor_class.return_value = mock_extractor
        
        with patch('src.main.extract_metadata') as mock_extract_metadata, \
             patch('src.main.format_metadata_for_id3') as mock_format_metadata:
            
            # Setup metadata mocks
            mock_metadata_obj = Mock()
            mock_metadata_obj.title = "Test Video"
            mock_metadata_obj.artist = "Test Channel"
            mock_metadata_obj.album = None
            mock_metadata_obj.date = "2023"
            mock_metadata_obj.duration = 180
            
            mock_extract_metadata.return_value = mock_metadata_obj
            mock_format_metadata.return_value = {}
            
            result = self.runner.invoke(main, [
                '--output', self.temp_dir,
                '--metadata',
                'https://youtube.com/watch?v=test'
            ])
            
            assert result.exit_code == 0
            assert "Embedding metadata" in result.output
            mock_converter.embed_metadata.assert_called_once()
    
    @patch('src.main.validate_dependencies')
    @patch('src.main.ErrorHandler')
    @patch('src.main.AudioConverter')
    @patch('src.main.YouTubeExtractor')
    def test_cli_playlist_success(self, mock_extractor_class, mock_converter_class, mock_error_handler_class, mock_validate_deps):
        """Test successful playlist extraction."""
        # Setup mocks
        mock_validate_deps.return_value = None
        
        mock_error_handler = Mock()
        mock_error_handler.validate_url.return_value = True
        mock_error_handler_class.return_value = mock_error_handler
        
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        
        mock_extractor = Mock()
        mock_extractor.is_playlist_url.return_value = True
        mock_extractor.get_playlist_info.return_value = self.mock_playlist_info
        mock_extractor.extract_playlist_audio.return_value = {
            'success': True,
            'playlist_title': 'Test Playlist',
            'playlist_folder': os.path.join(self.temp_dir, 'Test_Playlist'),
            'total_videos': 2,
            'successful_downloads': [
                {'title': 'Video 1', 'url': 'url1', 'output_path': 'path1.mp3'},
                {'title': 'Video 2', 'url': 'url2', 'output_path': 'path2.mp3'}
            ],
            'failed_downloads': [],
            'success_count': 2,
            'failure_count': 0
        }
        mock_extractor_class.return_value = mock_extractor
        
        result = self.runner.invoke(main, [
            '--output', self.temp_dir,
            'https://youtube.com/playlist?list=test'
        ])
        
        assert result.exit_code == 0
        assert "PROCESSING COMPLETE" in result.output
        assert "Test Playlist" in result.output
        assert "✓ Successful: 2" in result.output
        assert "Test Playlist" in result.output
    
    @patch('src.main.validate_dependencies')
    @patch('src.main.ErrorHandler')
    @patch('src.main.AudioConverter')
    @patch('src.main.YouTubeExtractor')
    def test_cli_playlist_with_failures(self, mock_extractor_class, mock_converter_class, mock_error_handler_class, mock_validate_deps):
        """Test playlist extraction with some failures."""
        # Setup mocks
        mock_validate_deps.return_value = None
        
        mock_error_handler = Mock()
        mock_error_handler.validate_url.return_value = True
        mock_error_handler_class.return_value = mock_error_handler
        
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        
        mock_extractor = Mock()
        mock_extractor.is_playlist_url.return_value = True
        mock_extractor.get_playlist_info.return_value = self.mock_playlist_info
        mock_extractor.extract_playlist_audio.return_value = {
            'success': True,
            'playlist_title': 'Test Playlist',
            'playlist_folder': os.path.join(self.temp_dir, 'Test_Playlist'),
            'total_videos': 2,
            'successful_downloads': [
                {'title': 'Video 1', 'url': 'url1', 'output_path': 'path1.mp3'}
            ],
            'failed_downloads': [
                {'title': 'Video 2', 'url': 'url2', 'error': 'Download failed'}
            ],
            'success_count': 1,
            'failure_count': 1
        }
        mock_extractor_class.return_value = mock_extractor
        
        result = self.runner.invoke(main, [
            '--output', self.temp_dir,
            '--verbose',
            'https://youtube.com/playlist?list=test'
        ])
        
        assert result.exit_code == 0
        assert "✓ Successful: 1" in result.output
        assert "✗ Failed: 1" in result.output
        assert "Video 2: Download failed" in result.output
    
    @patch('src.main.validate_dependencies')
    def test_cli_ffmpeg_not_found(self, mock_validate_deps):
        """Test CLI behavior when ffmpeg is not found."""
        from src.errors import ConversionError
        
        # Setup mock to raise ConversionError
        mock_validate_deps.side_effect = ConversionError(
            "ffmpeg not found in PATH",
            ["Install ffmpeg using your package manager", "Please install ffmpeg"]
        )
        
        result = self.runner.invoke(main, ['https://youtube.com/watch?v=test'])
        
        assert result.exit_code == 1
        assert "ffmpeg not found" in result.output
        assert "Please install ffmpeg" in result.output
    
    @patch('src.main.validate_dependencies')
    @patch('src.main.ErrorHandler')
    @patch('src.main.AudioConverter')
    @patch('src.main.YouTubeExtractor')
    def test_cli_keyboard_interrupt(self, mock_extractor_class, mock_converter_class, mock_error_handler_class, mock_validate_deps):
        """Test CLI behavior on keyboard interrupt."""
        # Setup mocks
        mock_validate_deps.return_value = None
        
        mock_error_handler = Mock()
        mock_error_handler.validate_url.side_effect = KeyboardInterrupt()
        mock_error_handler_class.return_value = mock_error_handler
        
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        
        result = self.runner.invoke(main, ['https://youtube.com/watch?v=test'])
        
        assert result.exit_code == 1
        assert "Operation cancelled by user" in result.output
    
    def test_cli_verbose_flag(self):
        """Test that verbose flag is properly handled."""
        with patch('src.main.setup_logging') as mock_setup_logging, \
             patch('src.main.AudioConverter'), \
             patch('src.main.YouTubeExtractor') as mock_extractor_class:
            
            # Setup basic mocks to avoid errors
            mock_extractor = Mock()
            mock_extractor.validate_url.return_value = False  # Will cause early exit
            mock_extractor_class.return_value = mock_extractor
            
            result = self.runner.invoke(main, ['--verbose', 'https://youtube.com/watch?v=test'])
            
            # Verify setup_logging was called with verbose=True
            mock_setup_logging.assert_called_once_with(True)
    
    def test_cli_quality_options(self):
        """Test all quality options are accepted."""
        for quality in ['128', '192', '320']:
            with patch('src.main.AudioConverter'), \
                 patch('src.main.YouTubeExtractor') as mock_extractor_class:
                
                # Setup basic mocks to avoid errors
                mock_extractor = Mock()
                mock_extractor.validate_url.return_value = False  # Will cause early exit
                mock_extractor_class.return_value = mock_extractor
                
                result = self.runner.invoke(main, ['--quality', quality, 'https://youtube.com/watch?v=test'])
                
                # Should not fail due to quality validation
                assert "Quality must be one of" not in result.output


class TestEndToEndIntegration:
    """End-to-end integration tests for complete workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock video info
        self.mock_video_info = VideoInfo(
            title="Integration Test Video",
            uploader="Test Channel",
            duration=180,
            upload_date="20231201",
            url="https://www.youtube.com/watch?v=integration_test",
            id="integration_test"
        )
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.main.validate_dependencies')
    @patch('src.main.AudioConverter')
    @patch('src.main.YouTubeExtractor')
    @patch('src.main.ProgressTracker')
    @patch('src.main.ErrorHandler')
    def test_complete_single_video_workflow(self, mock_error_handler_class, mock_progress_class, 
                                          mock_extractor_class, mock_converter_class, mock_validate_deps):
        """Test complete workflow for single video extraction with all components."""
        # Setup mocks
        mock_validate_deps.return_value = None
        
        mock_error_handler = Mock()
        mock_error_handler.validate_url.return_value = True
        mock_error_handler_class.return_value = mock_error_handler
        
        mock_progress = Mock()
        mock_progress_class.return_value = mock_progress
        
        mock_converter = Mock()
        mock_converter.embed_metadata.return_value = True
        mock_converter_class.return_value = mock_converter
        
        output_file = os.path.join(self.temp_dir, "integration_test.mp3")
        mock_extractor = Mock()
        mock_extractor.is_playlist_url.return_value = False
        mock_extractor.get_video_info.return_value = self.mock_video_info
        mock_extractor.extract_video_audio.return_value = output_file
        mock_extractor_class.return_value = mock_extractor
        
        # Mock metadata functions
        with patch('src.main.extract_metadata') as mock_extract_metadata:
            mock_metadata_obj = Mock()
            mock_metadata_obj.title = "Integration Test Video"
            mock_metadata_obj.artist = "Test Channel"
            mock_metadata_obj.album = None
            mock_metadata_obj.date = "2023"
            mock_metadata_obj.duration = 180
            mock_extract_metadata.return_value = mock_metadata_obj
            
            # Run the complete workflow
            result = self.runner.invoke(main, [
                '--output', self.temp_dir,
                '--quality', '192',
                '--metadata',
                '--verbose',
                'https://youtube.com/watch?v=integration_test'
            ])
            
            # Verify successful execution
            assert result.exit_code == 0
            
            # Verify all components were called in correct order
            mock_validate_deps.assert_called_once()
            mock_error_handler.validate_url.assert_called_once()
            mock_extractor.is_playlist_url.assert_called_once()
            mock_extractor.extract_video_audio.assert_called_once()
            mock_extractor.get_video_info.assert_called_once()
            mock_converter.embed_metadata.assert_called_once()
            
            # Verify output contains expected information
            assert "Detected video URL" in result.output
            assert "Metadata embedded successfully" in result.output
    
    @patch('src.main.validate_dependencies')
    @patch('src.main.AudioConverter')
    @patch('src.main.YouTubeExtractor')
    def test_dependency_validation_failure(self, mock_extractor_class, mock_converter_class, mock_validate_deps):
        """Test behavior when dependency validation fails."""
        # Setup mock to raise ImportError
        mock_validate_deps.side_effect = ImportError("Missing required Python packages: yt_dlp")
        
        result = self.runner.invoke(main, ['https://youtube.com/watch?v=test'])
        
        assert result.exit_code == 1
        assert "Missing required Python packages" in result.output
        
        # Verify other components weren't called
        mock_extractor_class.assert_not_called()
    
    @patch('src.main.validate_dependencies')
    @patch('src.main.AudioConverter')
    @patch('src.main.YouTubeExtractor')
    def test_configuration_integration(self, mock_extractor_class, mock_converter_class, mock_validate_deps):
        """Test that configuration is properly integrated throughout the application."""
        # Setup mocks
        mock_validate_deps.return_value = None
        
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        
        mock_extractor = Mock()
        mock_extractor.is_playlist_url.return_value = False
        mock_extractor.extract_video_audio.return_value = None  # Will cause early exit
        mock_extractor_class.return_value = mock_extractor
        
        # Test with default configuration values
        result = self.runner.invoke(main, ['https://youtube.com/watch?v=test'])
        
        # Verify configuration values are used
        assert "320kbps" in result.output  # Default quality
        assert "downloads" in result.output  # Default output directory
        
        # Verify ExtractionOptions was created with config values
        args, kwargs = mock_extractor_class.call_args
        options = args[0]  # First argument should be ExtractionOptions
        assert options.quality == "320"  # Default from config
        assert options.output_dir == "downloads"  # Default from config


class TestCLIEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('src.main.validate_dependencies')
    @patch('src.main.ErrorHandler')
    @patch('src.main.AudioConverter')
    @patch('src.main.YouTubeExtractor')
    def test_cli_extraction_failure(self, mock_extractor_class, mock_converter_class, mock_error_handler_class, mock_validate_deps):
        """Test CLI behavior when extraction fails."""
        # Setup mocks
        mock_validate_deps.return_value = None
        
        mock_error_handler = Mock()
        mock_error_handler.validate_url.return_value = True
        mock_error_handler_class.return_value = mock_error_handler
        
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        
        mock_extractor = Mock()
        mock_extractor.is_playlist_url.return_value = False
        mock_extractor.extract_video_audio.return_value = None  # Simulate failure
        mock_extractor_class.return_value = mock_extractor
        
        result = self.runner.invoke(main, ['https://youtube.com/watch?v=test'])
        
        assert result.exit_code == 1
        assert "Failed to extract audio" in result.output
    
    @patch('src.main.validate_dependencies')
    @patch('src.main.ErrorHandler')
    @patch('src.main.AudioConverter')
    @patch('src.main.YouTubeExtractor')
    def test_cli_large_playlist_confirmation(self, mock_extractor_class, mock_converter_class, mock_error_handler_class, mock_validate_deps):
        """Test confirmation prompt for large playlists."""
        # Setup mocks
        mock_validate_deps.return_value = None
        
        mock_error_handler = Mock()
        mock_error_handler.validate_url.return_value = True
        mock_error_handler_class.return_value = mock_error_handler
        
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        
        # Create large playlist
        large_playlist = PlaylistInfo(
            title="Large Playlist",
            uploader="Test Channel",
            video_count=15,  # > 10 triggers confirmation
            videos=[]
        )
        
        mock_extractor = Mock()
        mock_extractor.is_playlist_url.return_value = True
        mock_extractor.get_playlist_info.return_value = large_playlist
        # Mock the extract_playlist_audio to return cancellation
        mock_extractor.extract_playlist_audio.return_value = {
            'success': False,
            'error': 'Operation cancelled by user',
            'successful_downloads': [],
            'failed_downloads': [],
            'playlist_folder': None
        }
        mock_extractor_class.return_value = mock_extractor
        
        # Test declining the confirmation (the confirmation is now handled inside extract_playlist_audio)
        result = self.runner.invoke(main, ['https://youtube.com/playlist?list=test'])
        
        assert result.exit_code == 0
        assert "Operation cancelled" in result.output