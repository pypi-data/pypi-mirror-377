"""Unit tests for metadata handling functionality."""

import unittest
from datetime import datetime
from src.metadata import (
    VideoMetadata,
    extract_metadata,
    format_metadata_for_id3,
    clean_metadata_text,
    validate_metadata,
    get_safe_filename_from_metadata
)


class TestVideoMetadata(unittest.TestCase):
    """Test VideoMetadata dataclass."""
    
    def test_video_metadata_creation(self):
        """Test creating VideoMetadata object."""
        metadata = VideoMetadata(
            title="Test Title",
            artist="Test Artist",
            album="Test Album",
            date="2023",
            duration=180,
            track_number=1
        )
        
        self.assertEqual(metadata.title, "Test Title")
        self.assertEqual(metadata.artist, "Test Artist")
        self.assertEqual(metadata.album, "Test Album")
        self.assertEqual(metadata.date, "2023")
        self.assertEqual(metadata.duration, 180)
        self.assertEqual(metadata.track_number, 1)
    
    def test_video_metadata_minimal(self):
        """Test creating VideoMetadata with minimal required fields."""
        metadata = VideoMetadata(title="Title", artist="Artist")
        
        self.assertEqual(metadata.title, "Title")
        self.assertEqual(metadata.artist, "Artist")
        self.assertIsNone(metadata.album)
        self.assertIsNone(metadata.date)
        self.assertIsNone(metadata.duration)
        self.assertIsNone(metadata.track_number)


class TestExtractMetadata(unittest.TestCase):
    """Test metadata extraction from yt-dlp video info."""
    
    def setUp(self):
        """Set up test data."""
        self.video_info = {
            'title': 'Amazing Song Title',
            'uploader': 'Great Artist',
            'upload_date': '20231215',
            'duration': 240,
            'playlist_index': 3
        }
        
        self.playlist_info = {
            'title': 'Best Playlist Ever'
        }
    
    def test_extract_basic_metadata(self):
        """Test extracting basic metadata without playlist."""
        metadata = extract_metadata(self.video_info)
        
        self.assertEqual(metadata.title, 'Amazing Song Title')
        self.assertEqual(metadata.artist, 'Great Artist')
        self.assertEqual(metadata.date, '2023')
        self.assertEqual(metadata.duration, 240)
        self.assertIsNone(metadata.album)
        self.assertIsNone(metadata.track_number)
    
    def test_extract_metadata_with_playlist(self):
        """Test extracting metadata with playlist information."""
        metadata = extract_metadata(self.video_info, self.playlist_info)
        
        self.assertEqual(metadata.title, 'Amazing Song Title')
        self.assertEqual(metadata.artist, 'Great Artist')
        self.assertEqual(metadata.album, 'Best Playlist Ever')
        self.assertEqual(metadata.date, '2023')
        self.assertEqual(metadata.duration, 240)
        self.assertEqual(metadata.track_number, 3)
    
    def test_extract_metadata_missing_fields(self):
        """Test extracting metadata with missing fields."""
        minimal_info = {'title': 'Title Only'}
        metadata = extract_metadata(minimal_info)
        
        self.assertEqual(metadata.title, 'Title Only')
        self.assertEqual(metadata.artist, 'Unknown Artist')
        self.assertIsNone(metadata.date)
        self.assertIsNone(metadata.duration)
    
    def test_extract_metadata_invalid_date(self):
        """Test handling invalid upload date."""
        invalid_date_info = {
            'title': 'Test',
            'uploader': 'Test',
            'upload_date': 'invalid_date'
        }
        metadata = extract_metadata(invalid_date_info)
        
        self.assertIsNone(metadata.date)
    
    def test_extract_metadata_empty_title(self):
        """Test handling empty or missing title."""
        empty_title_info = {'uploader': 'Artist'}
        metadata = extract_metadata(empty_title_info)
        
        self.assertEqual(metadata.title, 'Unknown Title')
        self.assertEqual(metadata.artist, 'Artist')


class TestFormatMetadataForId3(unittest.TestCase):
    """Test formatting metadata for ID3 tags."""
    
    def test_format_complete_metadata(self):
        """Test formatting complete metadata."""
        metadata = VideoMetadata(
            title="Song Title",
            artist="Artist Name",
            album="Album Name",
            date="2023",
            track_number=5
        )
        
        id3_tags = format_metadata_for_id3(metadata)
        
        self.assertEqual(id3_tags['TIT2'], 'Song Title')
        self.assertEqual(id3_tags['TPE1'], 'Artist Name')
        self.assertEqual(id3_tags['TALB'], 'Album Name')
        self.assertEqual(id3_tags['TDRC'], '2023')
        self.assertEqual(id3_tags['TRCK'], '5')
    
    def test_format_minimal_metadata(self):
        """Test formatting minimal metadata."""
        metadata = VideoMetadata(title="Title", artist="Artist")
        
        id3_tags = format_metadata_for_id3(metadata)
        
        self.assertEqual(id3_tags['TIT2'], 'Title')
        self.assertEqual(id3_tags['TPE1'], 'Artist')
        self.assertNotIn('TALB', id3_tags)
        self.assertNotIn('TDRC', id3_tags)
        self.assertNotIn('TRCK', id3_tags)
    
    def test_format_metadata_with_none_values(self):
        """Test formatting metadata with None values."""
        metadata = VideoMetadata(
            title="Title",
            artist="Artist",
            album=None,
            date=None,
            track_number=None
        )
        
        id3_tags = format_metadata_for_id3(metadata)
        
        self.assertEqual(len(id3_tags), 2)  # Only title and artist
        self.assertIn('TIT2', id3_tags)
        self.assertIn('TPE1', id3_tags)


class TestCleanMetadataText(unittest.TestCase):
    """Test metadata text cleaning functionality."""
    
    def test_clean_normal_text(self):
        """Test cleaning normal text."""
        result = clean_metadata_text("Normal Song Title")
        self.assertEqual(result, "Normal Song Title")
    
    def test_clean_text_with_control_characters(self):
        """Test removing control characters."""
        result = clean_metadata_text("Title\x00with\x1fcontrol\x7fchars")
        self.assertEqual(result, "Titlewithcontrolchars")
    
    def test_clean_text_with_multiple_spaces(self):
        """Test normalizing whitespace."""
        result = clean_metadata_text("Title   with    multiple   spaces")
        self.assertEqual(result, "Title with multiple spaces")
    
    def test_clean_text_with_leading_trailing_spaces(self):
        """Test trimming whitespace."""
        result = clean_metadata_text("  Title with spaces  ")
        self.assertEqual(result, "Title with spaces")
    
    def test_clean_empty_text(self):
        """Test handling empty text."""
        self.assertEqual(clean_metadata_text(""), "")
        self.assertEqual(clean_metadata_text(None), "")
        self.assertEqual(clean_metadata_text("   "), "")
    
    def test_clean_long_text(self):
        """Test truncating long text."""
        long_text = "A" * 300
        result = clean_metadata_text(long_text)
        self.assertEqual(len(result), 255)
        self.assertTrue(result.endswith("..."))
    
    def test_clean_non_string_input(self):
        """Test handling non-string input."""
        self.assertEqual(clean_metadata_text(123), "")
        self.assertEqual(clean_metadata_text([]), "")


class TestValidateMetadata(unittest.TestCase):
    """Test metadata validation."""
    
    def test_validate_complete_metadata(self):
        """Test validating complete metadata."""
        metadata = VideoMetadata(
            title="Valid Title",
            artist="Valid Artist",
            album="Album"
        )
        self.assertTrue(validate_metadata(metadata))
    
    def test_validate_minimal_metadata(self):
        """Test validating minimal valid metadata."""
        metadata = VideoMetadata(title="Title", artist="Artist")
        self.assertTrue(validate_metadata(metadata))
    
    def test_validate_missing_title(self):
        """Test validation fails with missing title."""
        metadata = VideoMetadata(title="", artist="Artist")
        self.assertFalse(validate_metadata(metadata))
        
        metadata = VideoMetadata(title="   ", artist="Artist")
        self.assertFalse(validate_metadata(metadata))
    
    def test_validate_missing_artist(self):
        """Test validation fails with missing artist."""
        metadata = VideoMetadata(title="Title", artist="")
        self.assertFalse(validate_metadata(metadata))
        
        metadata = VideoMetadata(title="Title", artist="   ")
        self.assertFalse(validate_metadata(metadata))


class TestGetSafeFilenameFromMetadata(unittest.TestCase):
    """Test safe filename generation from metadata."""
    
    def test_safe_filename_normal_title(self):
        """Test generating filename from normal title."""
        metadata = VideoMetadata(title="Normal Song Title", artist="Artist")
        filename = get_safe_filename_from_metadata(metadata)
        self.assertEqual(filename, "Normal_Song_Title")
    
    def test_safe_filename_with_problematic_chars(self):
        """Test handling problematic filename characters."""
        metadata = VideoMetadata(
            title='Song<>:"|?*\\/Title',
            artist="Artist"
        )
        filename = get_safe_filename_from_metadata(metadata)
        self.assertEqual(filename, "Song_Title")
    
    def test_safe_filename_with_control_chars(self):
        """Test removing control characters."""
        metadata = VideoMetadata(
            title="Title\x00with\x1fcontrol",
            artist="Artist"
        )
        filename = get_safe_filename_from_metadata(metadata)
        self.assertEqual(filename, "Titlewithcontrol")
    
    def test_safe_filename_empty_title(self):
        """Test handling empty title."""
        metadata = VideoMetadata(title="", artist="Artist")
        filename = get_safe_filename_from_metadata(metadata)
        self.assertEqual(filename, "unknown_title")
    
    def test_safe_filename_long_title(self):
        """Test truncating long titles."""
        long_title = "A" * 250
        metadata = VideoMetadata(title=long_title, artist="Artist")
        filename = get_safe_filename_from_metadata(metadata)
        self.assertEqual(len(filename), 200)
    
    def test_safe_filename_multiple_spaces_underscores(self):
        """Test normalizing spaces and underscores."""
        metadata = VideoMetadata(
            title="Title___with   multiple___spaces",
            artist="Artist"
        )
        filename = get_safe_filename_from_metadata(metadata)
        self.assertEqual(filename, "Title_with_multiple_spaces")


if __name__ == '__main__':
    unittest.main()