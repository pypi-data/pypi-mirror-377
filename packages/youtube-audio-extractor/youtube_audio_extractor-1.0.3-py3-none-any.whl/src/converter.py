"""Audio conversion utilities."""

import os
import subprocess
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import ffmpeg
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TLEN

from .errors import ErrorHandler, ConversionError, FileSystemError


class AudioConverter:
    """
    Handles audio conversion and MP3 processing.
    
    This class provides functionality for converting audio files to MP3 format
    and embedding metadata using ID3 tags. It uses ffmpeg for audio conversion
    and mutagen for metadata manipulation. The converter includes comprehensive
    error handling and validation for all operations.
    
    Attributes:
        QUALITY_BITRATES (dict): Mapping of quality strings to ffmpeg bitrate values
        logger (logging.Logger): Logger instance for this class
        error_handler (ErrorHandler): Error handler for consistent error management
        
    Example:
        >>> converter = AudioConverter()
        >>> success = converter.convert_to_mp3("input.webm", "output.mp3", "320")
        >>> if success:
        ...     metadata = {"title": "Song Title", "artist": "Artist Name"}
        ...     converter.embed_metadata("output.mp3", metadata)
    """
    
    QUALITY_BITRATES = {
        "128": "128k",
        "192": "192k", 
        "320": "320k"
    }
    
    def __init__(self):
        """
        Initialize the audio converter.
        
        Sets up the audio converter with necessary components and validates that
        ffmpeg is available on the system. This validation ensures that audio
        conversion operations will work properly.
        
        Raises:
            ConversionError: If ffmpeg is not found in the system PATH or is not
                           properly installed.
                           
        Example:
            >>> try:
            ...     converter = AudioConverter()
            ...     print("Audio converter initialized successfully")
            ... except ConversionError as e:
            ...     print(f"Failed to initialize converter: {e}")
        """
        self.logger = logging.getLogger(__name__)
        self.error_handler = ErrorHandler()
        self.validate_ffmpeg()
    
    def validate_ffmpeg(self) -> bool:
        """
        Check if ffmpeg is available in the system PATH.
        
        Validates that ffmpeg is properly installed and accessible from the command
        line. This is essential for audio conversion operations to work correctly.
        
        Returns:
            bool: True if ffmpeg is available and working properly
            
        Raises:
            ConversionError: If ffmpeg is not found in PATH, not properly installed,
                           or not executable. The error includes suggestions for
                           installing ffmpeg on different operating systems.
                           
        Example:
            >>> converter = AudioConverter()
            >>> try:
            ...     if converter.validate_ffmpeg():
            ...         print("ffmpeg is available")
            ... except ConversionError as e:
            ...     print(f"ffmpeg validation failed: {e}")
            ...     for suggestion in e.suggestions:
            ...         print(f"  - {suggestion}")
        """
        try:
            self.error_handler.validate_ffmpeg()
            return True
        except ConversionError:
            raise  # Re-raise as ConversionError for consistency
    
    def convert_to_mp3(self, input_file: str, output_file: str, quality: str = "320") -> bool:
        """
        Convert audio file to MP3 format with specified quality.
        
        Converts an audio file from any supported format to MP3 using ffmpeg.
        Supports multiple quality levels and includes comprehensive validation
        of input files, output directories, and conversion parameters.
        
        Args:
            input_file (str): Path to the input audio file to convert
            output_file (str): Path where the MP3 file should be saved
            quality (str, optional): Audio quality in kbps. Supported values are
                                   "128", "192", or "320". Defaults to "320".
            
        Returns:
            bool: True if conversion completed successfully and output file was created
            
        Raises:
            ConversionError: If conversion fails due to:
                - Unsupported quality setting
                - Input file not found or not readable
                - Output directory not writable or insufficient disk space
                - ffmpeg conversion errors
                - File system permission issues
                
        Example:
            >>> converter = AudioConverter()
            >>> success = converter.convert_to_mp3(
            ...     "downloaded_audio.webm", 
            ...     "output/song.mp3", 
            ...     quality="192"
            ... )
            >>> if success:
            ...     print("Conversion completed successfully")
        """
        # Validate quality
        if quality not in self.QUALITY_BITRATES:
            raise ConversionError(
                f"Unsupported quality: {quality}. Supported: {list(self.QUALITY_BITRATES.keys())}",
                ["Use one of the supported quality values: 128, 192, 320"]
            )
        
        # Validate input file
        if not os.path.exists(input_file):
            raise ConversionError(
                f"Input file not found: {input_file}",
                [
                    "Check if the file path is correct",
                    "Verify the file was downloaded successfully",
                    "Ensure the file hasn't been moved or deleted"
                ]
            )
        
        # Validate and create output directory
        output_dir = os.path.dirname(output_file)
        if output_dir:
            try:
                self.error_handler.validate_file_system(output_dir, required_space_mb=10)
                os.makedirs(output_dir, exist_ok=True)
            except (FileSystemError, OSError, PermissionError) as e:
                fs_error = self.error_handler.handle_file_system_error(e, "creating output directory", output_dir)
                raise ConversionError(str(fs_error), fs_error.suggestions)
        
        try:
            # Use ffmpeg-python for conversion
            stream = ffmpeg.input(input_file)
            stream = ffmpeg.output(
                stream,
                output_file,
                acodec='mp3',
                audio_bitrate=self.QUALITY_BITRATES[quality],
                format='mp3'
            )
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            # Verify output file was created
            if not os.path.exists(output_file):
                raise ConversionError(
                    "Output file was not created after conversion",
                    [
                        "Check available disk space",
                        "Verify write permissions",
                        "Try a different output directory"
                    ]
                )
            
            self.logger.info(f"Successfully converted {input_file} to {output_file}")
            return True
            
        except (OSError, PermissionError) as e:
            fs_error = self.error_handler.handle_file_system_error(e, "audio conversion", output_file)
            raise ConversionError(str(fs_error), fs_error.suggestions)
        except Exception as e:
            conversion_error = self.error_handler.handle_conversion_error(e, input_file, output_file)
            self.logger.error(str(conversion_error))
            raise conversion_error
    
    def embed_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Embed metadata into MP3 file using ID3 tags.
        
        Adds or updates ID3v2 metadata tags in an MP3 file using the mutagen library.
        Supports standard metadata fields like title, artist, album, date, and duration.
        Creates ID3 tags if they don't exist and handles encoding properly for
        international characters.
        
        Args:
            file_path (str): Path to the MP3 file to modify
            metadata (Dict[str, Any]): Dictionary containing metadata fields.
                                     Supported keys:
                                     - title: Song/video title
                                     - artist: Artist/channel name
                                     - album: Album/playlist name
                                     - date: Release/upload date
                                     - duration: Track duration in seconds
                     
        Returns:
            bool: True if metadata was successfully embedded and saved
            
        Raises:
            ConversionError: If metadata embedding fails due to:
                - File not found or not accessible
                - Invalid MP3 file format
                - File permission issues
                - Corrupted audio file
                - File being used by another program
                
        Example:
            >>> converter = AudioConverter()
            >>> metadata = {
            ...     "title": "Never Gonna Give You Up",
            ...     "artist": "Rick Astley",
            ...     "album": "Whenever You Need Somebody",
            ...     "date": "1987",
            ...     "duration": 213
            ... }
            >>> success = converter.embed_metadata("song.mp3", metadata)
            >>> if success:
            ...     print("Metadata embedded successfully")
        """
        if not os.path.exists(file_path):
            raise ConversionError(
                f"File not found: {file_path}",
                [
                    "Check if the file path is correct",
                    "Verify the file exists and wasn't moved",
                    "Ensure the conversion completed successfully"
                ]
            )
        
        try:
            # Load the MP3 file
            audio_file = MP3(file_path, ID3=ID3)
            
            # Add ID3 tag if it doesn't exist
            if audio_file.tags is None:
                audio_file.add_tags()
            
            # Embed metadata
            if metadata.get('title'):
                audio_file.tags.add(TIT2(encoding=3, text=str(metadata['title'])))
            
            if metadata.get('artist'):
                audio_file.tags.add(TPE1(encoding=3, text=str(metadata['artist'])))
            
            if metadata.get('album'):
                audio_file.tags.add(TALB(encoding=3, text=str(metadata['album'])))
            
            if metadata.get('date'):
                audio_file.tags.add(TDRC(encoding=3, text=str(metadata['date'])))
            
            if metadata.get('duration'):
                # Duration should be in milliseconds for TLEN
                duration_ms = int(metadata['duration'] * 1000) if isinstance(metadata['duration'], (int, float)) else None
                if duration_ms:
                    audio_file.tags.add(TLEN(encoding=3, text=str(duration_ms)))
            
            # Save the changes
            audio_file.save()
            self.logger.info(f"Successfully embedded metadata in {file_path}")
            return True
            
        except (OSError, PermissionError) as e:
            fs_error = self.error_handler.handle_file_system_error(e, "embedding metadata", file_path)
            raise ConversionError(str(fs_error), fs_error.suggestions)
        except Exception as e:
            raise ConversionError(
                f"Error embedding metadata: {e}",
                [
                    "Check if the MP3 file is valid",
                    "Verify the file is not corrupted",
                    "Ensure the file is not being used by another program",
                    "Try converting the file again"
                ]
            )
    
    def get_supported_qualities(self) -> list:
        """
        Get list of supported audio qualities.
        
        Returns the list of audio quality options that can be used with the
        convert_to_mp3 method. These correspond to different MP3 bitrates.
        
        Returns:
            list: List of supported quality strings ("128", "192", "320")
                  representing bitrates in kbps
                  
        Example:
            >>> converter = AudioConverter()
            >>> qualities = converter.get_supported_qualities()
            >>> print(f"Supported qualities: {', '.join(qualities)}")
            >>> # Output: Supported qualities: 128, 192, 320
        """
        return list(self.QUALITY_BITRATES.keys())
    
    def convert_and_embed(self, input_file: str, output_file: str, 
                         metadata: Dict[str, Any], quality: str = "320") -> bool:
        """
        Convert audio to MP3 and embed metadata in one operation.
        
        Convenience method that combines audio conversion and metadata embedding
        into a single operation. This is more efficient than calling the methods
        separately and ensures consistency between the two operations.
        
        Args:
            input_file (str): Path to the input audio file to convert
            output_file (str): Path where the MP3 file should be saved
            metadata (Dict[str, Any]): Dictionary containing metadata to embed
            quality (str, optional): Audio quality in kbps. Defaults to "320".
            
        Returns:
            bool: True if both conversion and metadata embedding completed successfully
            
        Raises:
            ConversionError: If either conversion or metadata embedding fails.
                           The error will indicate which operation failed.
                           
        Example:
            >>> converter = AudioConverter()
            >>> metadata = {"title": "Song Title", "artist": "Artist Name"}
            >>> success = converter.convert_and_embed(
            ...     "input.webm", "output.mp3", metadata, quality="192"
            ... )
            >>> if success:
            ...     print("Conversion and metadata embedding completed")
        """
        try:
            # First convert to MP3
            success = self.convert_to_mp3(input_file, output_file, quality)
            if not success:
                return False
            
            # Then embed metadata
            return self.embed_metadata(output_file, metadata)
            
        except ConversionError:
            raise  # Re-raise ConversionError as-is
        except Exception as e:
            conversion_error = self.error_handler.handle_conversion_error(e, input_file, output_file)
            raise conversion_error