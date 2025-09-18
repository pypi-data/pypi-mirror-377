"""Unit tests for the YouTube extractor module."""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.extractor import YouTubeExtractor
from src.utils import VideoInfo, PlaylistInfo, ExtractionOptions


class TestYouTubeExtractor(unittest.TestCase):
    """Test cases for YouTubeExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.options = ExtractionOptions(
            quality="320",
            output_dir=self.temp_dir,
            format_template="%(title)s.%(ext)s",
            embed_metadata=True,
        )
        self.extractor = YouTubeExtractor(self.options)

        # Mock video info data
        self.mock_video_info = {
            "title": "Test Video Title",
            "uploader": "Test Channel",
            "duration": 180,
            "upload_date": "20231201",
            "id": "test_video_id",
        }
        
        # Mock playlist info data
        self.mock_playlist_info = {
            "title": "Test Playlist",
            "uploader": "Test Channel",
            "entries": [
                {
                    "title": "Video 1",
                    "uploader": "Test Channel",
                    "duration": 180,
                    "upload_date": "20231201",
                    "id": "video1_id",
                    "webpage_url": "https://www.youtube.com/watch?v=video1",
                },
                {
                    "title": "Video 2",
                    "uploader": "Test Channel",
                    "duration": 240,
                    "upload_date": "20231202",
                    "id": "video2_id",
                    "webpage_url": "https://www.youtube.com/watch?v=video2",
                },
            ]
        }

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_get_video_info_success(self, mock_ydl_class):
        """Test successful video info extraction."""
        # Setup mock
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = self.mock_video_info

        # Test
        url = "https://www.youtube.com/watch?v=test123"
        result = self.extractor.get_video_info(url)

        # Assertions
        self.assertIsInstance(result, VideoInfo)
        self.assertEqual(result.title, "Test Video Title")
        self.assertEqual(result.uploader, "Test Channel")
        self.assertEqual(result.duration, 180)
        self.assertEqual(result.upload_date, "20231201")
        self.assertEqual(result.url, url)
        self.assertEqual(result.id, "test_video_id")

        # Verify yt-dlp was called correctly
        mock_ydl.extract_info.assert_called_once_with(url, download=False)

    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_get_video_info_download_error(self, mock_ydl_class):
        """Test video info extraction with DownloadError."""
        # Setup mock to raise DownloadError
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = Exception("Network error")

        # Test
        url = "https://www.youtube.com/watch?v=invalid"
        result = self.extractor.get_video_info(url)

        # Assertions
        self.assertIsNone(result)

    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_get_video_info_missing_fields(self, mock_ydl_class):
        """Test video info extraction with missing fields."""
        # Setup mock with incomplete data
        incomplete_info = {"title": "Test Video"}
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = incomplete_info

        # Test
        url = "https://www.youtube.com/watch?v=test123"
        result = self.extractor.get_video_info(url)

        # Assertions
        self.assertIsInstance(result, VideoInfo)
        self.assertEqual(result.title, "Test Video")
        self.assertEqual(result.uploader, "Unknown Uploader")
        self.assertEqual(result.duration, 0)
        self.assertEqual(result.upload_date, "")
        self.assertEqual(result.id, "")

    @patch("src.extractor.yt_dlp.YoutubeDL")
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_extract_video_audio_success(self, mock_makedirs, mock_exists, mock_ydl_class):
        """Test successful audio extraction."""
        # Setup mocks
        mock_ydl_info = Mock()
        mock_ydl_download = Mock()

        # Mock the context manager calls
        mock_ydl_class.return_value.__enter__.side_effect = [
            mock_ydl_info,
            mock_ydl_download,
        ]

        mock_ydl_info.extract_info.return_value = self.mock_video_info
        mock_ydl_download.download.return_value = None
        mock_exists.return_value = True

        # Test
        url = "https://www.youtube.com/watch?v=test123"
        result = self.extractor.extract_video_audio(url)

        # Assertions
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith("Test Video Title.mp3"))
        mock_ydl_download.download.assert_called_once_with([url])
        mock_makedirs.assert_called_once()

    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_extract_video_audio_no_info(self, mock_ydl_class):
        """Test audio extraction when video info cannot be retrieved."""
        # Setup mock to return None for extract_info
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = None

        # Test
        url = "https://www.youtube.com/watch?v=invalid"
        result = self.extractor.extract_video_audio(url)

        # Assertions
        self.assertIsNone(result)

    @patch("src.extractor.yt_dlp.YoutubeDL")
    @patch("os.path.exists")
    @patch("time.sleep")
    def test_extract_video_audio_retry_logic(
        self, mock_sleep, mock_exists, mock_ydl_class
    ):
        """Test retry logic on download failure."""
        # Setup mocks
        mock_ydl_info = Mock()
        mock_ydl_download1 = Mock()
        mock_ydl_download2 = Mock()

        # Mock the context manager calls - info call, then download calls
        mock_ydl_class.return_value.__enter__.side_effect = [
            mock_ydl_info,
            mock_ydl_download1,
            mock_ydl_download2,
        ]

        mock_ydl_info.extract_info.return_value = self.mock_video_info
        mock_ydl_download1.download.side_effect = Exception(
            "Network error"
        )  # First attempt fails
        mock_ydl_download2.download.return_value = None  # Second attempt succeeds
        mock_exists.return_value = True

        # Test
        url = "https://www.youtube.com/watch?v=test123"
        result = self.extractor.extract_video_audio(url, max_retries=2)

        # Assertions
        self.assertIsNotNone(result)
        mock_ydl_download1.download.assert_called_once_with([url])
        mock_ydl_download2.download.assert_called_once_with([url])
        mock_sleep.assert_called_once_with(1)  # First retry delay

    @patch("src.extractor.yt_dlp.YoutubeDL")
    @patch("time.sleep")
    def test_extract_video_audio_max_retries_exceeded(self, mock_sleep, mock_ydl_class):
        """Test behavior when max retries are exceeded."""
        # Setup mocks
        mock_ydl_info = Mock()
        mock_ydl_download1 = Mock()
        mock_ydl_download2 = Mock()
        mock_ydl_download3 = Mock()

        # Mock the context manager calls - info call, then 3 download attempts
        mock_ydl_class.return_value.__enter__.side_effect = [
            mock_ydl_info,
            mock_ydl_download1,
            mock_ydl_download2,
            mock_ydl_download3,
        ]

        mock_ydl_info.extract_info.return_value = self.mock_video_info
        mock_ydl_download1.download.side_effect = Exception("Persistent network error")
        mock_ydl_download2.download.side_effect = Exception("Persistent network error")
        mock_ydl_download3.download.side_effect = Exception("Persistent network error")

        # Test
        url = "https://www.youtube.com/watch?v=test123"
        result = self.extractor.extract_video_audio(url, max_retries=2)

        # Assertions
        self.assertIsNone(result)
        mock_ydl_download1.download.assert_called_once_with([url])
        mock_ydl_download2.download.assert_called_once_with([url])
        mock_ydl_download3.download.assert_called_once_with([url])
        self.assertEqual(mock_sleep.call_count, 2)  # 2 retry delays

    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_validate_url_valid(self, mock_ydl_class):
        """Test URL validation with valid URL."""
        # Setup mock
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = self.mock_video_info

        # Test
        url = "https://www.youtube.com/watch?v=test123"
        result = self.extractor.validate_url(url)

        # Assertions
        self.assertTrue(result)
        mock_ydl.extract_info.assert_called_once_with(url, download=False)

    def test_validate_url_invalid_format(self):
        """Test URL validation with invalid format."""
        # Test various invalid URL formats
        invalid_urls = [
            "",
            None,
            "not-a-url",
            "youtube.com/watch?v=test",  # Missing protocol
            "https://example.com/video",  # Not YouTube
        ]
        
        for url in invalid_urls:
            with self.subTest(url=url):
                result = self.extractor.validate_url(url)
                self.assertFalse(result)
    
    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_validate_url_network_error(self, mock_ydl_class):
        """Test URL validation with network error."""
        # Setup mock to raise network-related exception
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = Exception("Network connection failed")

        # Test
        url = "https://youtube.com/watch?v=test"
        result = self.extractor.validate_url(url)

        # Assertions
        self.assertFalse(result)

    def test_extractor_initialization(self):
        """Test extractor initialization with options."""
        # Test
        extractor = YouTubeExtractor(self.options)

        # Assertions
        self.assertEqual(extractor.options, self.options)
        self.assertIn("format", extractor.ydl_opts)
        self.assertIn("extractaudio", extractor.ydl_opts)
        self.assertIn("audioformat", extractor.ydl_opts)
        self.assertEqual(extractor.ydl_opts["audioquality"], "320")
        self.assertTrue(extractor.ydl_opts["noplaylist"])

    # Playlist processing tests
    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_is_playlist_url_true(self, mock_ydl_class):
        """Test playlist URL detection for valid playlist."""
        # Setup mock
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = self.mock_playlist_info

        # Test
        url = "https://www.youtube.com/playlist?list=test123"
        result = self.extractor.is_playlist_url(url)

        # Assertions
        self.assertTrue(result)
        mock_ydl.extract_info.assert_called_once_with(url, download=False)

    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_is_playlist_url_false_single_video(self, mock_ydl_class):
        """Test playlist URL detection for single video."""
        # Setup mock
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = self.mock_video_info  # No entries field

        # Test
        url = "https://www.youtube.com/watch?v=test123"
        result = self.extractor.is_playlist_url(url)

        # Assertions
        self.assertFalse(result)

    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_is_playlist_url_false_error(self, mock_ydl_class):
        """Test playlist URL detection with error."""
        # Setup mock to raise exception
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = Exception("Network error")

        # Test
        url = "https://invalid-url.com"
        result = self.extractor.is_playlist_url(url)

        # Assertions
        self.assertFalse(result)

    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_get_playlist_info_success(self, mock_ydl_class):
        """Test successful playlist info extraction."""
        # Setup mock
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = self.mock_playlist_info

        # Test
        url = "https://www.youtube.com/playlist?list=test123"
        result = self.extractor.get_playlist_info(url)

        # Assertions
        self.assertIsInstance(result, PlaylistInfo)
        self.assertEqual(result.title, "Test Playlist")
        self.assertEqual(result.uploader, "Test Channel")
        self.assertEqual(result.video_count, 2)
        self.assertEqual(len(result.videos), 2)
        
        # Check first video
        self.assertEqual(result.videos[0].title, "Video 1")
        self.assertEqual(result.videos[0].url, "https://www.youtube.com/watch?v=video1")
        
        # Check second video
        self.assertEqual(result.videos[1].title, "Video 2")
        self.assertEqual(result.videos[1].url, "https://www.youtube.com/watch?v=video2")

    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_get_playlist_info_no_entries(self, mock_ydl_class):
        """Test playlist info extraction with no entries."""
        # Setup mock
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {"title": "Empty Playlist"}  # No entries

        # Test
        url = "https://www.youtube.com/playlist?list=empty"
        result = self.extractor.get_playlist_info(url)

        # Assertions
        self.assertIsNone(result)

    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_get_playlist_info_with_none_entries(self, mock_ydl_class):
        """Test playlist info extraction with None entries (unavailable videos)."""
        # Setup mock with None entries
        playlist_with_none = {
            "title": "Playlist with Unavailable Videos",
            "uploader": "Test Channel",
            "entries": [
                {
                    "title": "Available Video",
                    "uploader": "Test Channel",
                    "duration": 180,
                    "upload_date": "20231201",
                    "id": "available_id",
                    "webpage_url": "https://www.youtube.com/watch?v=available",
                },
                None,  # Unavailable video
                {
                    "title": "Another Available Video",
                    "uploader": "Test Channel",
                    "duration": 240,
                    "upload_date": "20231202",
                    "id": "available2_id",
                    "webpage_url": "https://www.youtube.com/watch?v=available2",
                },
            ]
        }
        
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = playlist_with_none

        # Test
        url = "https://www.youtube.com/playlist?list=test123"
        result = self.extractor.get_playlist_info(url)

        # Assertions
        self.assertIsInstance(result, PlaylistInfo)
        self.assertEqual(result.video_count, 2)  # Should skip None entries
        self.assertEqual(len(result.videos), 2)
        self.assertEqual(result.videos[0].title, "Available Video")
        self.assertEqual(result.videos[1].title, "Another Available Video")

    @patch("src.extractor.yt_dlp.YoutubeDL")
    def test_get_playlist_info_error(self, mock_ydl_class):
        """Test playlist info extraction with error."""
        # Setup mock to raise exception
        mock_ydl = Mock()
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = Exception("Network error")

        # Test
        url = "https://www.youtube.com/playlist?list=invalid"
        result = self.extractor.get_playlist_info(url)

        # Assertions
        self.assertIsNone(result)

    @patch("src.extractor.YouTubeExtractor.extract_video_audio")
    @patch("src.extractor.YouTubeExtractor.get_playlist_info")
    @patch("os.makedirs")
    def test_extract_playlist_audio_success(self, mock_makedirs, mock_get_playlist_info, mock_extract_video):
        """Test successful playlist audio extraction."""
        # Setup mocks
        playlist_info = PlaylistInfo(
            title="Test Playlist",
            uploader="Test Channel",
            video_count=2,
            videos=[
                VideoInfo("Video 1", "Test Channel", 180, "20231201", "https://www.youtube.com/watch?v=video1", "video1_id"),
                VideoInfo("Video 2", "Test Channel", 240, "20231202", "https://www.youtube.com/watch?v=video2", "video2_id"),
            ]
        )
        
        mock_get_playlist_info.return_value = playlist_info
        mock_extract_video.side_effect = [
            os.path.join(self.temp_dir, "Test Playlist", "Video 1.mp3"),
            os.path.join(self.temp_dir, "Test Playlist", "Video 2.mp3"),
        ]

        # Test
        url = "https://www.youtube.com/playlist?list=test123"
        result = self.extractor.extract_playlist_audio(url)

        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['playlist_title'], "Test Playlist")
        self.assertEqual(result['total_videos'], 2)
        self.assertEqual(result['success_count'], 2)
        self.assertEqual(result['failure_count'], 0)
        self.assertEqual(len(result['successful_downloads']), 2)
        self.assertEqual(len(result['failed_downloads']), 0)
        
        # Verify extract_video_audio was called for each video
        self.assertEqual(mock_extract_video.call_count, 2)
        mock_makedirs.assert_called_once()

    @patch("src.extractor.YouTubeExtractor.extract_video_audio")
    @patch("src.extractor.YouTubeExtractor.get_playlist_info")
    @patch("os.makedirs")
    def test_extract_playlist_audio_partial_failure(self, mock_makedirs, mock_get_playlist_info, mock_extract_video):
        """Test playlist audio extraction with some failures."""
        # Setup mocks
        playlist_info = PlaylistInfo(
            title="Test Playlist",
            uploader="Test Channel",
            video_count=3,
            videos=[
                VideoInfo("Video 1", "Test Channel", 180, "20231201", "https://www.youtube.com/watch?v=video1", "video1_id"),
                VideoInfo("Video 2", "Test Channel", 240, "20231202", "https://www.youtube.com/watch?v=video2", "video2_id"),
                VideoInfo("Video 3", "Test Channel", 200, "20231203", "https://www.youtube.com/watch?v=video3", "video3_id"),
            ]
        )
        
        mock_get_playlist_info.return_value = playlist_info
        mock_extract_video.side_effect = [
            os.path.join(self.temp_dir, "Test Playlist", "Video 1.mp3"),  # Success
            None,  # Failure
            os.path.join(self.temp_dir, "Test Playlist", "Video 3.mp3"),  # Success
        ]

        # Test
        url = "https://www.youtube.com/playlist?list=test123"
        result = self.extractor.extract_playlist_audio(url)

        # Assertions
        self.assertTrue(result['success'])  # Should be True if at least one succeeds
        self.assertEqual(result['total_videos'], 3)
        self.assertEqual(result['success_count'], 2)
        self.assertEqual(result['failure_count'], 1)
        self.assertEqual(len(result['successful_downloads']), 2)
        self.assertEqual(len(result['failed_downloads']), 1)
        
        # Check failed download details
        self.assertEqual(result['failed_downloads'][0]['title'], "Video 2")
        self.assertEqual(result['failed_downloads'][0]['error'], "Download failed after retries")

    @patch("src.extractor.YouTubeExtractor.extract_video_audio")
    @patch("src.extractor.YouTubeExtractor.get_playlist_info")
    @patch("os.makedirs")
    def test_extract_playlist_audio_with_exception(self, mock_makedirs, mock_get_playlist_info, mock_extract_video):
        """Test playlist audio extraction with exception during processing."""
        # Setup mocks
        playlist_info = PlaylistInfo(
            title="Test Playlist",
            uploader="Test Channel",
            video_count=2,
            videos=[
                VideoInfo("Video 1", "Test Channel", 180, "20231201", "https://www.youtube.com/watch?v=video1", "video1_id"),
                VideoInfo("Video 2", "Test Channel", 240, "20231202", "https://www.youtube.com/watch?v=video2", "video2_id"),
            ]
        )
        
        mock_get_playlist_info.return_value = playlist_info
        mock_extract_video.side_effect = [
            os.path.join(self.temp_dir, "Test Playlist", "Video 1.mp3"),  # Success
            Exception("Unexpected error"),  # Exception
        ]

        # Test
        url = "https://www.youtube.com/playlist?list=test123"
        result = self.extractor.extract_playlist_audio(url)

        # Assertions
        self.assertTrue(result['success'])  # Should be True if at least one succeeds
        self.assertEqual(result['success_count'], 1)
        self.assertEqual(result['failure_count'], 1)
        self.assertEqual(result['failed_downloads'][0]['error'], "Unexpected error")
    
    @patch("src.extractor.yt_dlp.YoutubeDL")
    @patch("os.makedirs")
    def test_extract_video_audio_file_system_error(self, mock_makedirs, mock_ydl_class):
        """Test audio extraction with file system error."""
        # Setup mock to raise permission error on directory creation
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        # Test
        url = "https://www.youtube.com/watch?v=test123"
        result = self.extractor.extract_video_audio(url)
        
        # Assertions
        self.assertIsNone(result)
    
    @patch("src.extractor.yt_dlp.YoutubeDL")
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_extract_video_audio_file_not_created(self, mock_makedirs, mock_exists, mock_ydl_class):
        """Test audio extraction when output file is not created."""
        # Setup mocks
        mock_ydl_info = Mock()
        mock_ydl_download = Mock()
        
        mock_ydl_class.return_value.__enter__.side_effect = [
            mock_ydl_info,
            mock_ydl_download,
        ]
        
        mock_ydl_info.extract_info.return_value = self.mock_video_info
        mock_ydl_download.download.return_value = None
        mock_exists.return_value = False  # File not created
        
        # Test
        url = "https://www.youtube.com/watch?v=test123"
        result = self.extractor.extract_video_audio(url)
        
        # Assertions
        self.assertIsNone(result)
    
    @patch("src.extractor.yt_dlp.YoutubeDL")
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_extract_video_audio_download_permission_error(self, mock_makedirs, mock_exists, mock_ydl_class):
        """Test audio extraction with permission error during download."""
        # Setup mocks
        mock_ydl_info = Mock()
        mock_ydl_download = Mock()
        
        mock_ydl_class.return_value.__enter__.side_effect = [
            mock_ydl_info,
            mock_ydl_download,
        ]
        
        mock_ydl_info.extract_info.return_value = self.mock_video_info
        mock_ydl_download.download.side_effect = PermissionError("Permission denied writing file")
        
        # Test
        url = "https://www.youtube.com/watch?v=test123"
        result = self.extractor.extract_video_audio(url)
        
        # Assertions
        self.assertIsNone(result)
    
    @patch("src.extractor.YouTubeExtractor.get_playlist_info")
    @patch("os.makedirs")
    def test_extract_playlist_audio_folder_creation_error(self, mock_makedirs, mock_get_playlist_info):
        """Test playlist extraction with folder creation error."""
        # Setup mocks
        playlist_info = PlaylistInfo(
            title="Test Playlist",
            uploader="Test Channel",
            video_count=1,
            videos=[VideoInfo("Video 1", "Test Channel", 180, "20231201", "https://www.youtube.com/watch?v=video1", "video1_id")]
        )
        
        mock_get_playlist_info.return_value = playlist_info
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        # Test
        url = "https://www.youtube.com/playlist?list=test123"
        result = self.extractor.extract_playlist_audio(url)
        
        # Assertions
        self.assertFalse(result['success'])
        self.assertIn("Permission denied", result['error'])
        self.assertEqual(result['successful_downloads'], [])
        self.assertEqual(result['failed_downloads'], [])
        self.assertIsNone(result['playlist_folder'])

    @patch("src.extractor.YouTubeExtractor.get_playlist_info")
    def test_extract_playlist_audio_no_playlist_info(self, mock_get_playlist_info):
        """Test playlist audio extraction when playlist info cannot be retrieved."""
        # Setup mock to return None
        mock_get_playlist_info.return_value = None

        # Test
        url = "https://www.youtube.com/playlist?list=invalid"
        result = self.extractor.extract_playlist_audio(url)

        # Assertions
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Failed to retrieve playlist information')
        self.assertEqual(result['successful_downloads'], [])
        self.assertEqual(result['failed_downloads'], [])
        self.assertIsNone(result['playlist_folder'])


if __name__ == "__main__":
    unittest.main()
