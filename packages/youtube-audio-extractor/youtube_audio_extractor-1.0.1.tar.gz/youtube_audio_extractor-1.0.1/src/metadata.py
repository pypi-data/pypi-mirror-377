"""Metadata handling for MP3 files."""

import re
from dataclasses import dataclass
from typing import Dict, Optional, Any
from datetime import datetime


@dataclass
class VideoMetadata:
    """
    Structured metadata for a video.
    
    Data class that holds metadata information extracted from YouTube videos
    for use in MP3 ID3 tags. Provides a clean interface for handling video
    metadata with proper type hints and optional fields.
    
    Attributes:
        title (str): Video title, used as the song title in ID3 tags
        artist (str): Channel/uploader name, used as the artist in ID3 tags
        album (Optional[str]): Playlist name if video is part of a playlist,
                              used as album name in ID3 tags
        date (Optional[str]): Upload date in YYYY format for ID3 tags
        duration (Optional[int]): Video duration in seconds
        track_number (Optional[int]): Position in playlist for track numbering
        
    Example:
        >>> metadata = VideoMetadata(
        ...     title="Never Gonna Give You Up",
        ...     artist="Rick Astley",
        ...     album="Whenever You Need Somebody",
        ...     date="1987",
        ...     duration=213,
        ...     track_number=1
        ... )
    """
    title: str
    artist: str
    album: Optional[str] = None
    date: Optional[str] = None
    duration: Optional[int] = None
    track_number: Optional[int] = None


def extract_metadata(video_info: Dict[str, Any], playlist_info: Optional[Dict[str, Any]] = None) -> VideoMetadata:
    """
    Extract metadata from yt-dlp video information.
    
    Processes raw video information from yt-dlp and converts it into a structured
    VideoMetadata object suitable for ID3 tag embedding. Handles data cleaning,
    format conversion, and extraction of relevant fields.
    
    Args:
        video_info (Dict[str, Any]): Video information dictionary from yt-dlp
                                   containing fields like title, uploader, 
                                   upload_date, duration, etc.
        playlist_info (Optional[Dict[str, Any]]): Optional playlist information
                                                for album metadata extraction
        
    Returns:
        VideoMetadata: Structured metadata object with cleaned and formatted
                      information ready for ID3 tag embedding
        
    Requirements: 3.1, 3.2, 3.3
    
    Example:
        >>> video_info = {
        ...     'title': 'Never Gonna Give You Up',
        ...     'uploader': 'Rick Astley',
        ...     'upload_date': '20091025',
        ...     'duration': 213
        ... }
        >>> playlist_info = {'title': 'Best of Rick Astley'}
        >>> metadata = extract_metadata(video_info, playlist_info)
        >>> print(f"Title: {metadata.title}, Artist: {metadata.artist}")
    """
    # Extract basic metadata
    title = clean_metadata_text(video_info.get('title', 'Unknown Title'))
    artist = clean_metadata_text(video_info.get('uploader', 'Unknown Artist'))
    
    # Extract album from playlist if available
    album = None
    if playlist_info:
        album = clean_metadata_text(playlist_info.get('title', ''))
    
    # Extract and format date
    date = None
    upload_date = video_info.get('upload_date')
    if upload_date:
        try:
            # yt-dlp provides date in YYYYMMDD format
            date_obj = datetime.strptime(upload_date, '%Y%m%d')
            date = date_obj.strftime('%Y')
        except (ValueError, TypeError):
            date = None
    
    # Extract duration
    duration = video_info.get('duration')
    
    # Extract track number from playlist index
    track_number = None
    if playlist_info and 'playlist_index' in video_info:
        track_number = video_info.get('playlist_index')
    
    return VideoMetadata(
        title=title,
        artist=artist,
        album=album,
        date=date,
        duration=duration,
        track_number=track_number
    )


def format_metadata_for_id3(metadata: VideoMetadata) -> Dict[str, Any]:
    """
    Format metadata for ID3 tag embedding.
    
    Converts a VideoMetadata object into a dictionary format suitable for
    ID3 tag libraries like mutagen. Maps metadata fields to their corresponding
    ID3v2 tag identifiers and handles optional fields appropriately.
    
    Args:
        metadata (VideoMetadata): VideoMetadata object containing the metadata
                                to format for ID3 tags
        
    Returns:
        Dict[str, Any]: Dictionary with ID3 tag identifiers as keys:
                       - TIT2: Title/song name
                       - TPE1: Artist/performer
                       - TALB: Album name (if available)
                       - TDRC: Recording date (if available)
                       - TRCK: Track number (if available)
        
    Requirements: 3.1, 3.2, 3.3, 3.4
    
    Example:
        >>> metadata = VideoMetadata(
        ...     title="Never Gonna Give You Up",
        ...     artist="Rick Astley",
        ...     album="Whenever You Need Somebody"
        ... )
        >>> id3_tags = format_metadata_for_id3(metadata)
        >>> print(id3_tags['TIT2'])  # "Never Gonna Give You Up"
    """
    id3_tags = {}
    
    # Required tags
    if metadata.title:
        id3_tags['TIT2'] = metadata.title  # Title
    
    if metadata.artist:
        id3_tags['TPE1'] = metadata.artist  # Artist
    
    # Optional tags
    if metadata.album:
        id3_tags['TALB'] = metadata.album  # Album
    
    if metadata.date:
        id3_tags['TDRC'] = metadata.date  # Recording date
    
    if metadata.track_number:
        id3_tags['TRCK'] = str(metadata.track_number)  # Track number
    
    return id3_tags


def clean_metadata_text(text: str) -> str:
    """
    Clean and validate metadata text for safe use in ID3 tags.
    
    Sanitizes text by removing control characters, normalizing whitespace,
    and ensuring the text is within reasonable length limits for ID3 tags.
    This prevents issues with metadata that contains problematic characters.
    
    Args:
        text (str): Raw text to clean and validate
        
    Returns:
        str: Cleaned text safe for use in ID3 metadata tags, with control
             characters removed, whitespace normalized, and length limited
             to 255 characters
        
    Requirements: 3.4
    
    Example:
        >>> dirty_text = "Song Title\x00\x01  with   extra\tspaces"
        >>> clean_text = clean_metadata_text(dirty_text)
        >>> print(clean_text)  # "Song Title with extra spaces"
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove or replace problematic characters
    # Remove control characters and non-printable characters
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Replace multiple whitespace with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Limit length to reasonable size for metadata (255 chars is common limit)
    if len(cleaned) > 255:
        cleaned = cleaned[:252] + "..."
    
    return cleaned


def validate_metadata(metadata: VideoMetadata) -> bool:
    """
    Validate that metadata contains minimum required information.
    
    Checks that the metadata object contains the essential fields required
    for proper ID3 tag creation. At minimum, both title and artist must be
    present and non-empty for valid MP3 metadata.
    
    Args:
        metadata (VideoMetadata): VideoMetadata object to validate
        
    Returns:
        bool: True if metadata contains valid title and artist information,
              False if essential fields are missing or empty
        
    Requirements: 3.4
    
    Example:
        >>> valid_metadata = VideoMetadata(title="Song", artist="Artist")
        >>> invalid_metadata = VideoMetadata(title="", artist="Artist")
        >>> print(validate_metadata(valid_metadata))    # True
        >>> print(validate_metadata(invalid_metadata))  # False
    """
    # At minimum, we need a title
    if not metadata.title or not metadata.title.strip():
        return False
    
    # Artist is also required for proper ID3 tags
    if not metadata.artist or not metadata.artist.strip():
        return False
    
    return True


def get_safe_filename_from_metadata(metadata: VideoMetadata) -> str:
    """
    Generate a safe filename from metadata.
    
    Creates a filesystem-safe filename from the video title in the metadata.
    Removes or replaces characters that are problematic in filenames across
    different operating systems and ensures the filename length is reasonable.
    
    Args:
        metadata (VideoMetadata): VideoMetadata object containing the title
                                to use for filename generation
        
    Returns:
        str: Safe filename string with problematic characters replaced,
             length limited to 200 characters, and fallback to "unknown_title"
             if the title is empty
        
    Requirements: 3.4
    
    Example:
        >>> metadata = VideoMetadata(
        ...     title='Song: "The Best" | Part 1',
        ...     artist="Artist"
        ... )
        >>> filename = get_safe_filename_from_metadata(metadata)
        >>> print(filename)  # "Song_ _The Best_ _ Part 1"
    """
    # Use title as base filename
    filename = metadata.title
    
    # Remove or replace characters that are problematic in filenames
    # Replace with underscore: < > : " | ? * \ /
    filename = re.sub(r'[<>:"|?*\\/]', '_', filename)
    
    # Remove any remaining control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Replace multiple underscores/spaces with single underscore
    filename = re.sub(r'[_\s]+', '_', filename)
    
    # Remove leading/trailing underscores and spaces
    filename = filename.strip('_ ')
    
    # Ensure filename isn't empty
    if not filename:
        filename = "unknown_title"
    
    # Limit filename length (most filesystems support 255 chars)
    if len(filename) > 200:  # Leave room for extension and numbering
        filename = filename[:200]
    
    return filename