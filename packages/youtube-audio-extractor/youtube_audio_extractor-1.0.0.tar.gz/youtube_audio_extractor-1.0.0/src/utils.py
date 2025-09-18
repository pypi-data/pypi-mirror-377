"""Helper functions and utilities."""

import re
import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class VideoInfo:
    """
    Data class representing information about a YouTube video.
    
    Contains essential metadata about a YouTube video extracted from yt-dlp.
    Used throughout the application for passing video information between
    components and organizing extraction results.
    
    Attributes:
        title (str): Video title as displayed on YouTube
        uploader (str): Channel name or uploader username
        duration (int): Video duration in seconds
        upload_date (str): Upload date in YYYYMMDD format from yt-dlp
        url (str): Full YouTube URL for the video
        id (str): YouTube video ID (the part after 'v=' in URLs)
        
    Example:
        >>> video = VideoInfo(
        ...     title="Never Gonna Give You Up",
        ...     uploader="Rick Astley",
        ...     duration=213,
        ...     upload_date="20091025",
        ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        ...     id="dQw4w9WgXcQ"
        ... )
    """
    title: str
    uploader: str
    duration: int
    upload_date: str
    url: str
    id: str


@dataclass
class PlaylistInfo:
    """
    Data class representing information about a YouTube playlist.
    
    Contains comprehensive information about a YouTube playlist including
    metadata and a list of all videos contained within it. Used for
    organizing playlist extraction operations and providing user feedback.
    
    Attributes:
        title (str): Playlist title as displayed on YouTube
        uploader (str): Channel name or playlist creator username
        video_count (int): Total number of videos in the playlist
        videos (List[VideoInfo]): List of VideoInfo objects for each video
                                 in the playlist
        
    Example:
        >>> videos = [
        ...     VideoInfo("Video 1", "Channel", 180, "20230101", "url1", "id1"),
        ...     VideoInfo("Video 2", "Channel", 240, "20230102", "url2", "id2")
        ... ]
        >>> playlist = PlaylistInfo(
        ...     title="My Favorite Songs",
        ...     uploader="Music Channel",
        ...     video_count=2,
        ...     videos=videos
        ... )
    """
    title: str
    uploader: str
    video_count: int
    videos: List[VideoInfo]


@dataclass
class ExtractionOptions:
    """
    Data class representing options for audio extraction.
    
    Configuration object that holds all user preferences and settings for
    the audio extraction process. Used to pass configuration between
    different components of the application consistently.
    
    Attributes:
        quality (str): Audio quality in kbps. Supported values: "128", "192", "320".
                      Defaults to "320" for highest quality.
        output_dir (str): Directory path where extracted files should be saved.
                         Defaults to "downloads" in current directory.
        format_template (str): yt-dlp format template for output filenames.
                              Defaults to "%(title)s.%(ext)s".
        embed_metadata (bool): Whether to embed ID3 metadata in MP3 files.
                              Defaults to True.
        
    Example:
        >>> options = ExtractionOptions(
        ...     quality="192",
        ...     output_dir="~/Music/Downloads",
        ...     embed_metadata=True
        ... )
        >>> print(f"Quality: {options.quality}kbps")
        >>> print(f"Output: {options.output_dir}")
    """
    quality: str = "320"  # kbps
    output_dir: str = "downloads"
    format_template: str = "%(title)s.%(ext)s"
    embed_metadata: bool = True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing invalid characters.
    
    Ensures filenames are safe for use across different operating systems by
    removing or replacing characters that are invalid in Windows, macOS, or
    Linux filesystems. Also handles length limitations and edge cases.
    
    Args:
        filename (str): The original filename to sanitize
        
    Returns:
        str: A sanitized filename safe for filesystem use across platforms,
             with invalid characters replaced by underscores, length limited
             to 200 characters, and fallback to "untitled" if empty
        
    Example:
        >>> unsafe_name = 'Song: "Title" | Part 1 <HD>'
        >>> safe_name = sanitize_filename(unsafe_name)
        >>> print(safe_name)  # "Song_ _Title_ _ Part 1 _HD_"
        
        >>> empty_name = sanitize_filename("")
        >>> print(empty_name)  # "untitled"
    """
    if not filename:
        return "untitled"
    
    # Remove or replace invalid characters for cross-platform compatibility
    # Invalid characters: < > : " | ? * \ /
    invalid_chars = r'[<>:"|?*\\\/]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    
    # Replace multiple consecutive underscores with single underscore
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Ensure filename isn't empty after sanitization
    if not sanitized:
        return "untitled"
    
    # Limit filename length to 200 characters to avoid filesystem issues
    if len(sanitized) > 200:
        sanitized = sanitized[:200].rstrip('_')
    
    return sanitized


def create_safe_directory_name(name: str) -> str:
    """
    Create a safe directory name from a playlist or channel name.
    
    Convenience function that applies filename sanitization rules to create
    safe directory names. Uses the same sanitization logic as sanitize_filename
    to ensure consistency across the application.
    
    Args:
        name (str): The original name to convert to a directory name
        
    Returns:
        str: A sanitized directory name safe for filesystem use across platforms
        
    Example:
        >>> playlist_name = "My Playlist: Best Songs (2023)"
        >>> dir_name = create_safe_directory_name(playlist_name)
        >>> print(dir_name)  # "My Playlist_ Best Songs _2023_"
    """
    return sanitize_filename(name)