"""Unit tests for utils module."""

import unittest
from src.utils import VideoInfo, PlaylistInfo, ExtractionOptions, sanitize_filename, create_safe_directory_name


class TestDataModels(unittest.TestCase):
    """Test cases for data model classes."""
    
    def test_video_info_creation(self):
        """Test VideoInfo data class creation and attributes."""
        video = VideoInfo(
            title="Test Video",
            uploader="Test Channel",
            duration=180,
            upload_date="20231201",
            url="https://youtube.com/watch?v=test123",
            id="test123"
        )
        
        self.assertEqual(video.title, "Test Video")
        self.assertEqual(video.uploader, "Test Channel")
        self.assertEqual(video.duration, 180)
        self.assertEqual(video.upload_date, "20231201")
        self.assertEqual(video.url, "https://youtube.com/watch?v=test123")
        self.assertEqual(video.id, "test123")
    
    def test_playlist_info_creation(self):
        """Test PlaylistInfo data class creation and attributes."""
        video1 = VideoInfo("Video 1", "Channel", 120, "20231201", "url1", "id1")
        video2 = VideoInfo("Video 2", "Channel", 150, "20231202", "url2", "id2")
        
        playlist = PlaylistInfo(
            title="Test Playlist",
            uploader="Test Channel",
            video_count=2,
            videos=[video1, video2]
        )
        
        self.assertEqual(playlist.title, "Test Playlist")
        self.assertEqual(playlist.uploader, "Test Channel")
        self.assertEqual(playlist.video_count, 2)
        self.assertEqual(len(playlist.videos), 2)
        self.assertEqual(playlist.videos[0].title, "Video 1")
        self.assertEqual(playlist.videos[1].title, "Video 2")
    
    def test_extraction_options_defaults(self):
        """Test ExtractionOptions default values."""
        options = ExtractionOptions()
        
        self.assertEqual(options.quality, "320")
        self.assertEqual(options.output_dir, "downloads")
        self.assertEqual(options.format_template, "%(title)s.%(ext)s")
        self.assertTrue(options.embed_metadata)
    
    def test_extraction_options_custom_values(self):
        """Test ExtractionOptions with custom values."""
        options = ExtractionOptions(
            quality="192",
            output_dir="/custom/path",
            format_template="%(uploader)s - %(title)s.%(ext)s",
            embed_metadata=False
        )
        
        self.assertEqual(options.quality, "192")
        self.assertEqual(options.output_dir, "/custom/path")
        self.assertEqual(options.format_template, "%(uploader)s - %(title)s.%(ext)s")
        self.assertFalse(options.embed_metadata)


class TestFilenameSanitization(unittest.TestCase):
    """Test cases for filename sanitization functions."""
    
    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        result = sanitize_filename("Normal Filename")
        self.assertEqual(result, "Normal Filename")
    
    def test_sanitize_filename_invalid_characters(self):
        """Test sanitization of invalid characters."""
        test_cases = [
            ("File<name>", "File_name"),
            ("File:name", "File_name"),
            ('File"name', "File_name"),
            ("File|name", "File_name"),
            ("File?name", "File_name"),
            ("File*name", "File_name"),
            ("File\\name", "File_name"),
            ("File/name", "File_name"),
            ("File<>:\"|?*\\/name", "File_name"),
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = sanitize_filename(input_name)
                self.assertEqual(result, expected)
    
    def test_sanitize_filename_whitespace_and_dots(self):
        """Test sanitization of leading/trailing whitespace and dots."""
        test_cases = [
            ("  filename  ", "filename"),
            ("..filename..", "filename"),
            ("  ..filename..  ", "filename"),
            ("   ", "untitled"),
            ("...", "untitled"),
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = sanitize_filename(input_name)
                self.assertEqual(result, expected)
    
    def test_sanitize_filename_multiple_underscores(self):
        """Test replacement of multiple consecutive underscores."""
        result = sanitize_filename("File___with____many_underscores")
        self.assertEqual(result, "File_with_many_underscores")
    
    def test_sanitize_filename_empty_input(self):
        """Test sanitization of empty or None input."""
        self.assertEqual(sanitize_filename(""), "untitled")
        self.assertEqual(sanitize_filename(None), "untitled")
    
    def test_sanitize_filename_long_filename(self):
        """Test sanitization of very long filenames."""
        long_name = "a" * 250
        result = sanitize_filename(long_name)
        self.assertEqual(len(result), 200)
        self.assertTrue(result.endswith("a"))  # Should not end with underscore
    
    def test_sanitize_filename_becomes_empty_after_sanitization(self):
        """Test handling of filenames that become empty after sanitization."""
        result = sanitize_filename("<<<>>>")
        self.assertEqual(result, "untitled")
    
    def test_create_safe_directory_name(self):
        """Test directory name creation."""
        test_cases = [
            ("My Playlist", "My Playlist"),
            ("Playlist<with>invalid:chars", "Playlist_with_invalid_chars"),
            ("", "untitled"),
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = create_safe_directory_name(input_name)
                self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()