"""Unit tests for audio converter module."""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock, call
from src.converter import AudioConverter


class TestAudioConverter(unittest.TestCase):
    """Test cases for AudioConverter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.converter.shutil.which')
    def test_validate_ffmpeg_success(self, mock_which):
        """Test ffmpeg validation when ffmpeg is available."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        
        converter = AudioConverter()
        result = converter.validate_ffmpeg()
        
        self.assertTrue(result)
        mock_which.assert_called_with('ffmpeg')
    
    @patch('src.converter.shutil.which')
    def test_validate_ffmpeg_failure(self, mock_which):
        """Test ffmpeg validation when ffmpeg is not available."""
        mock_which.return_value = None
        
        from src.errors import ConversionError
        with self.assertRaises(ConversionError) as context:
            AudioConverter()
        
        self.assertIn('ffmpeg not found', str(context.exception))
    
    @patch('src.converter.shutil.which')
    def test_get_supported_qualities(self, mock_which):
        """Test getting supported audio qualities."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        
        converter = AudioConverter()
        qualities = converter.get_supported_qualities()
        
        expected_qualities = ['128', '192', '320']
        self.assertEqual(sorted(qualities), sorted(expected_qualities))
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.ffmpeg')
    @patch('src.converter.os.path.exists')
    @patch('src.converter.os.makedirs')
    def test_convert_to_mp3_success(self, mock_makedirs, mock_exists, mock_ffmpeg, mock_which):
        """Test successful MP3 conversion."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = True
        
        # Mock ffmpeg chain
        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_ffmpeg.input.return_value = mock_input
        mock_ffmpeg.output.return_value = mock_output
        mock_ffmpeg.run.return_value = None
        
        converter = AudioConverter()
        result = converter.convert_to_mp3('input.wav', 'output.mp3', '320')
        
        self.assertTrue(result)
        mock_ffmpeg.input.assert_called_once_with('input.wav')
        mock_ffmpeg.output.assert_called_once_with(
            mock_input,
            'output.mp3',
            acodec='mp3',
            audio_bitrate='320k',
            format='mp3'
        )
        mock_ffmpeg.run.assert_called_once_with(mock_output, overwrite_output=True, quiet=True)
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.os.path.exists')
    def test_convert_to_mp3_invalid_quality(self, mock_exists, mock_which):
        """Test MP3 conversion with invalid quality."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = True
        
        converter = AudioConverter()
        
        from src.errors import ConversionError
        with self.assertRaises(ConversionError) as context:
            converter.convert_to_mp3('input.wav', 'output.mp3', '999')
        
        self.assertIn('Unsupported quality: 999', str(context.exception))
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.os.path.exists')
    def test_convert_to_mp3_file_not_found(self, mock_exists, mock_which):
        """Test MP3 conversion when input file doesn't exist."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = False
        
        converter = AudioConverter()
        
        from src.errors import ConversionError
        with self.assertRaises(ConversionError) as context:
            converter.convert_to_mp3('nonexistent.wav', 'output.mp3', '320')
        
        self.assertIn('Input file not found', str(context.exception))
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.ffmpeg')
    @patch('src.converter.os.path.exists')
    @patch('src.converter.os.makedirs')
    def test_convert_to_mp3_ffmpeg_error(self, mock_makedirs, mock_exists, mock_ffmpeg, mock_which):
        """Test MP3 conversion when ffmpeg fails."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.side_effect = lambda path: path == 'input.wav'  # Input exists, output doesn't
        
        # Mock ffmpeg to raise an error
        mock_ffmpeg.Error = Exception  # Define the exception class
        mock_ffmpeg.run.side_effect = mock_ffmpeg.Error("FFmpeg failed")
        
        converter = AudioConverter()
        
        from src.errors import ConversionError
        with self.assertRaises(ConversionError) as context:
            converter.convert_to_mp3('input.wav', 'output.mp3', '320')
        
        self.assertIn('Audio conversion failed', str(context.exception))
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.MP3')
    @patch('src.converter.os.path.exists')
    def test_embed_metadata_success(self, mock_exists, mock_mp3_class, mock_which):
        """Test successful metadata embedding."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = True
        
        # Mock MP3 file and tags
        mock_mp3_file = MagicMock()
        mock_mp3_file.tags = MagicMock()
        mock_mp3_class.return_value = mock_mp3_file
        
        converter = AudioConverter()
        metadata = {
            'title': 'Test Song',
            'artist': 'Test Artist',
            'album': 'Test Album',
            'date': '2023',
            'duration': 180.5
        }
        
        result = converter.embed_metadata('test.mp3', metadata)
        
        self.assertTrue(result)
        mock_mp3_file.tags.add.assert_called()
        mock_mp3_file.save.assert_called_once()
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.MP3')
    @patch('src.converter.os.path.exists')
    def test_embed_metadata_no_tags(self, mock_exists, mock_mp3_class, mock_which):
        """Test metadata embedding when file has no existing tags."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = True
        
        # Mock MP3 file without tags
        mock_mp3_file = MagicMock()
        mock_mp3_file.tags = None
        mock_tags = MagicMock()
        
        # Mock add_tags to set the tags attribute
        def add_tags_side_effect():
            mock_mp3_file.tags = mock_tags
        
        mock_mp3_file.add_tags.side_effect = add_tags_side_effect
        mock_mp3_class.return_value = mock_mp3_file
        
        converter = AudioConverter()
        metadata = {'title': 'Test Song'}
        
        result = converter.embed_metadata('test.mp3', metadata)
        
        self.assertTrue(result)
        mock_mp3_file.add_tags.assert_called_once()
        mock_tags.add.assert_called()
        mock_mp3_file.save.assert_called_once()
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.os.path.exists')
    def test_embed_metadata_file_not_found(self, mock_exists, mock_which):
        """Test metadata embedding when file doesn't exist."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = False
        
        converter = AudioConverter()
        
        # This test is now covered by test_embed_metadata_file_not_found_raises_error
        # The old behavior returned False, new behavior raises ConversionError
        from src.errors import ConversionError
        with self.assertRaises(ConversionError) as context:
            converter.embed_metadata('nonexistent.mp3', {'title': 'Test'})
        
        self.assertIn('File not found', str(context.exception))
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.MP3')
    @patch('src.converter.os.path.exists')
    def test_embed_metadata_exception(self, mock_exists, mock_mp3_class, mock_which):
        """Test metadata embedding when an exception occurs."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = True
        mock_mp3_class.side_effect = Exception("Mutagen error")
        
        converter = AudioConverter()
        
        from src.errors import ConversionError
        with self.assertRaises(ConversionError) as context:
            converter.embed_metadata('test.mp3', {'title': 'Test'})
        
        self.assertIn('Error embedding metadata', str(context.exception))
    
    @patch('src.converter.shutil.which')
    def test_convert_and_embed_success(self, mock_which):
        """Test combined convert and embed operation success."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        
        converter = AudioConverter()
        
        # Mock both methods to return True
        with patch.object(converter, 'convert_to_mp3', return_value=True) as mock_convert, \
             patch.object(converter, 'embed_metadata', return_value=True) as mock_embed:
            
            metadata = {'title': 'Test Song'}
            result = converter.convert_and_embed('input.wav', 'output.mp3', metadata, '192')
            
            self.assertTrue(result)
            mock_convert.assert_called_once_with('input.wav', 'output.mp3', '192')
            mock_embed.assert_called_once_with('output.mp3', metadata)
    
    @patch('src.converter.shutil.which')
    def test_convert_and_embed_conversion_fails(self, mock_which):
        """Test combined operation when conversion fails."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        
        converter = AudioConverter()
        
        # Mock conversion to fail
        with patch.object(converter, 'convert_to_mp3', return_value=False) as mock_convert, \
             patch.object(converter, 'embed_metadata') as mock_embed:
            
            metadata = {'title': 'Test Song'}
            result = converter.convert_and_embed('input.wav', 'output.mp3', metadata)
            
            self.assertFalse(result)
            mock_convert.assert_called_once()
            mock_embed.assert_not_called()  # Should not be called if conversion fails
    
    @patch('src.converter.shutil.which')
    def test_convert_and_embed_metadata_fails(self, mock_which):
        """Test combined operation when metadata embedding fails."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        
        converter = AudioConverter()
        
        # Mock conversion to succeed but metadata to fail
        with patch.object(converter, 'convert_to_mp3', return_value=True) as mock_convert, \
             patch.object(converter, 'embed_metadata', return_value=False) as mock_embed:
            
            metadata = {'title': 'Test Song'}
            result = converter.convert_and_embed('input.wav', 'output.mp3', metadata)
            
            self.assertFalse(result)
            mock_convert.assert_called_once()
            mock_embed.assert_called_once()
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.os.path.exists')
    @patch('src.converter.os.makedirs')
    def test_convert_to_mp3_output_directory_permission_error(self, mock_makedirs, mock_exists, mock_which):
        """Test MP3 conversion with output directory permission error."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = True
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        converter = AudioConverter()
        
        from src.errors import ConversionError
        with self.assertRaises(ConversionError) as context:
            converter.convert_to_mp3('input.wav', 'output/output.mp3', '320')
        
        self.assertIn('Permission denied', str(context.exception))
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.ffmpeg')
    @patch('src.converter.os.path.exists')
    @patch('src.converter.os.makedirs')
    def test_convert_to_mp3_output_file_not_created(self, mock_makedirs, mock_exists, mock_ffmpeg, mock_which):
        """Test MP3 conversion when output file is not created."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        # Mock exists to return True for input, False for output after conversion
        mock_exists.side_effect = lambda path: path == 'input.wav'
        
        # Mock successful ffmpeg run but no output file created
        mock_ffmpeg.run.return_value = None
        
        converter = AudioConverter()
        
        from src.errors import ConversionError
        with self.assertRaises(ConversionError) as context:
            converter.convert_to_mp3('input.wav', 'output.mp3', '320')
        
        self.assertIn('Output file was not created', str(context.exception))
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.ffmpeg')
    @patch('src.converter.os.path.exists')
    @patch('src.converter.os.makedirs')
    def test_convert_to_mp3_permission_error_during_conversion(self, mock_makedirs, mock_exists, mock_ffmpeg, mock_which):
        """Test MP3 conversion with permission error during conversion."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = True
        mock_ffmpeg.run.side_effect = PermissionError("Permission denied writing output file")
        
        converter = AudioConverter()
        
        from src.errors import ConversionError
        with self.assertRaises(ConversionError) as context:
            converter.convert_to_mp3('input.wav', 'output.mp3', '320')
        
        self.assertIn('Permission denied', str(context.exception))
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.os.path.exists')
    def test_embed_metadata_file_not_found_raises_error(self, mock_exists, mock_which):
        """Test metadata embedding when file doesn't exist raises error."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = False
        
        converter = AudioConverter()
        
        from src.errors import ConversionError
        with self.assertRaises(ConversionError) as context:
            converter.embed_metadata('nonexistent.mp3', {'title': 'Test'})
        
        self.assertIn('File not found', str(context.exception))
    
    @patch('src.converter.shutil.which')
    @patch('src.converter.MP3')
    @patch('src.converter.os.path.exists')
    def test_embed_metadata_permission_error(self, mock_exists, mock_mp3_class, mock_which):
        """Test metadata embedding with permission error."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = True
        
        # Mock MP3 file save to raise permission error
        mock_mp3_file = MagicMock()
        mock_mp3_file.tags = MagicMock()
        mock_mp3_file.save.side_effect = PermissionError("Permission denied")
        mock_mp3_class.return_value = mock_mp3_file
        
        converter = AudioConverter()
        
        from src.errors import ConversionError
        with self.assertRaises(ConversionError) as context:
            converter.embed_metadata('test.mp3', {'title': 'Test Song'})
        
        self.assertIn('Permission denied', str(context.exception))
    
    @patch('src.converter.shutil.which')
    def test_convert_and_embed_conversion_error_propagation(self, mock_which):
        """Test that conversion errors are properly propagated in convert_and_embed."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        
        converter = AudioConverter()
        
        # Mock convert_to_mp3 to raise ConversionError
        with patch.object(converter, 'convert_to_mp3') as mock_convert:
            from src.errors import ConversionError
            mock_convert.side_effect = ConversionError("Conversion failed", ["Try again"])
            
            with self.assertRaises(ConversionError) as context:
                converter.convert_and_embed('input.wav', 'output.mp3', {'title': 'Test'})
            
            self.assertIn('Conversion failed', str(context.exception))
    
    @patch('src.converter.shutil.which')
    def test_convert_and_embed_metadata_error_propagation(self, mock_which):
        """Test that metadata errors are properly propagated in convert_and_embed."""
        mock_which.return_value = '/usr/bin/ffmpeg'
        
        converter = AudioConverter()
        
        # Mock successful conversion but failed metadata embedding
        with patch.object(converter, 'convert_to_mp3', return_value=True) as mock_convert, \
             patch.object(converter, 'embed_metadata') as mock_embed:
            
            from src.errors import ConversionError
            mock_embed.side_effect = ConversionError("Metadata failed", ["Check file"])
            
            with self.assertRaises(ConversionError) as context:
                converter.convert_and_embed('input.wav', 'output.mp3', {'title': 'Test'})
            
            self.assertIn('Metadata failed', str(context.exception))


if __name__ == '__main__':
    unittest.main()