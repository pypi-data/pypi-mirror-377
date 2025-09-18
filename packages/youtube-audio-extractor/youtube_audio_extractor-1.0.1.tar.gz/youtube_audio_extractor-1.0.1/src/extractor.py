"""Core extraction logic for YouTube content."""

import os
import time
import logging
from typing import Optional, Dict, Any, Callable
from pathlib import Path

import yt_dlp

from .utils import VideoInfo, PlaylistInfo, ExtractionOptions, sanitize_filename, create_safe_directory_name
from .progress import ProgressTracker, PlaylistProgressTracker
from .errors import ErrorHandler, NetworkError, FileSystemError, URLValidationError


class YouTubeExtractor:
    """
    Handles YouTube content extraction using yt-dlp.
    
    This class provides a high-level interface for downloading audio from YouTube
    videos and playlists. It handles URL validation, progress tracking, error recovery,
    and file organization. The extractor uses yt-dlp for downloading and provides
    comprehensive error handling with user-friendly feedback.
    
    Attributes:
        options (ExtractionOptions): Configuration options for extraction
        progress_tracker (ProgressTracker): Optional progress tracker for user feedback
        logger (logging.Logger): Logger instance for this class
        error_handler (ErrorHandler): Error handler for consistent error management
        ydl_opts (dict): Configuration options for yt-dlp
        
    Example:
        >>> options = ExtractionOptions(quality="320", output_dir="downloads")
        >>> tracker = ProgressTracker(verbose=True)
        >>> extractor = YouTubeExtractor(options, tracker)
        >>> output_path = extractor.extract_video_audio("https://youtube.com/watch?v=...")
    """
    
    def __init__(self, options: ExtractionOptions, progress_tracker: Optional[ProgressTracker] = None):
        """
        Initialize the extractor with extraction options.
        
        Sets up the YouTube extractor with the specified configuration options and
        optional progress tracking. Configures yt-dlp with appropriate settings for
        audio extraction and quality selection.
        
        Args:
            options (ExtractionOptions): Configuration options including quality,
                                       output directory, and metadata preferences
            progress_tracker (ProgressTracker, optional): Progress tracker for user
                                                         feedback during downloads
                                                         
        Example:
            >>> options = ExtractionOptions(quality="192", output_dir="~/Music")
            >>> tracker = ProgressTracker(verbose=False)
            >>> extractor = YouTubeExtractor(options, tracker)
        """
        self.options = options
        self.logger = logging.getLogger(__name__)
        self.progress_tracker = progress_tracker
        self.error_handler = ErrorHandler()
        
        # Configure yt-dlp options
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.options.output_dir, self.options.format_template),
            'noplaylist': True,  # Will be overridden for playlist extraction
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.options.quality,
            }],
        }
        
        # Add progress hook if tracker is provided
        if self.progress_tracker:
            self.ydl_opts['progress_hooks'] = [self.progress_tracker.create_yt_dlp_hook()]
    
    def get_video_info(self, url: str) -> Optional[VideoInfo]:
        """
        Retrieve video information without downloading.
        
        Extracts metadata from a YouTube video URL without downloading the actual
        content. This is useful for getting video details, validating URLs, and
        preparing for download operations.
        
        Args:
            url (str): YouTube video URL to extract information from
            
        Returns:
            VideoInfo: Object containing video metadata (title, uploader, duration,
                      upload_date, url, id) if successful
            None: If extraction fails due to network issues, invalid URL, or
                  other errors
                  
        Example:
            >>> extractor = YouTubeExtractor(options)
            >>> info = extractor.get_video_info("https://youtube.com/watch?v=dQw4w9WgXcQ")
            >>> if info:
            ...     print(f"Title: {info.title}")
            ...     print(f"Duration: {info.duration} seconds")
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return VideoInfo(
                    title=info.get('title', 'Unknown Title'),
                    uploader=info.get('uploader', 'Unknown Uploader'),
                    duration=info.get('duration', 0),
                    upload_date=info.get('upload_date', ''),
                    url=url,
                    id=info.get('id', '')
                )
                
        except yt_dlp.DownloadError as e:
            self.logger.error(f"Failed to extract video info for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error extracting video info for {url}: {e}")
            return None
    
    def extract_video_audio(self, url: str, max_retries: int = 3) -> Optional[str]:
        """
        Extract audio from a single YouTube video with retry logic.
        
        Downloads and extracts audio from a YouTube video, converting it to the
        specified format and quality. Includes comprehensive error handling with
        automatic retry logic for network issues and detailed user feedback.
        
        Args:
            url (str): YouTube video URL to extract audio from
            max_retries (int, optional): Maximum number of retry attempts for
                                       failed downloads. Defaults to 3.
            
        Returns:
            str: Path to the extracted audio file if successful
            None: If extraction fails after all retry attempts or encounters
                  unrecoverable errors
                  
        Raises:
            The method handles exceptions internally and returns None on failure,
            but may log errors through the progress tracker.
            
        Example:
            >>> extractor = YouTubeExtractor(options, progress_tracker)
            >>> output_path = extractor.extract_video_audio(
            ...     "https://youtube.com/watch?v=dQw4w9WgXcQ", max_retries=5
            ... )
            >>> if output_path:
            ...     print(f"Audio saved to: {output_path}")
        """
        # Validate file system before starting
        try:
            self.error_handler.validate_file_system(self.options.output_dir, required_space_mb=50)
        except FileSystemError as e:
            self.logger.error(f"File system validation failed: {e}")
            if self.progress_tracker:
                self.progress_tracker.show_error_with_suggestions(str(e), e.suggestions)
            return None
        
        # Ensure output directory exists
        try:
            os.makedirs(self.options.output_dir, exist_ok=True)
        except (OSError, PermissionError) as e:
            fs_error = self.error_handler.handle_file_system_error(e, "creating output directory", self.options.output_dir)
            self.logger.error(str(fs_error))
            if self.progress_tracker:
                self.progress_tracker.show_error_with_suggestions(str(fs_error), fs_error.suggestions)
            return None
        
        # Show stage message
        if self.progress_tracker:
            self.progress_tracker.show_stage_message("Retrieving video information")
        
        # First, get video info
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    self.logger.error(f"Could not extract video information for {url}")
                    if self.progress_tracker:
                        self.progress_tracker.show_error_with_suggestions(
                            "Could not retrieve video information",
                            ["Check if the URL is valid", "Verify internet connection", "Try again later"]
                        )
                    return None
        except Exception as e:
            self.logger.error(f"Failed to extract video info: {e}")
            if self.progress_tracker:
                self.progress_tracker.show_error_with_suggestions(
                    f"Failed to extract video info: {e}",
                    ["Check if the URL is valid", "Verify internet connection"]
                )
            return None
        
        # Show video information
        if self.progress_tracker:
            title = info.get('title', 'Unknown Title')
            uploader = info.get('uploader', 'Unknown Uploader')
            duration = info.get('duration')
            self.progress_tracker.show_video_info(title, uploader, duration)
        
        # Create sanitized filename
        title = info.get('title', 'Unknown Title')
        sanitized_title = sanitize_filename(title)
        output_filename = f"{sanitized_title}.mp3"
        output_path = os.path.join(self.options.output_dir, output_filename)
        
        # Update output template for this specific download
        ydl_opts_copy = self.ydl_opts.copy()
        ydl_opts_copy['outtmpl'] = output_path.replace('.mp3', '.%(ext)s')
        
        # Show download stage
        if self.progress_tracker:
            self.progress_tracker.show_stage_message("Downloading and extracting audio")
        
        # Retry logic for download
        for attempt in range(max_retries + 1):
            try:
                # Download and extract audio
                with yt_dlp.YoutubeDL(ydl_opts_copy) as download_ydl:
                    download_ydl.download([url])
                
                # Verify the file was created
                if os.path.exists(output_path):
                    self.logger.info(f"Successfully extracted audio: {output_path}")
                    return output_path
                else:
                    # Look for the file with different extension
                    base_path = output_path.replace('.mp3', '')
                    for ext in ['.mp3', '.m4a', '.webm', '.opus']:
                        potential_path = base_path + ext
                        if os.path.exists(potential_path):
                            self.logger.info(f"Successfully extracted audio: {potential_path}")
                            return potential_path
                    
                    # File not found - this is a file system issue
                    fs_error = FileSystemError(
                        "Audio file not found after extraction",
                        ["Check available disk space", "Verify write permissions", "Try a different output directory"]
                    )
                    self.logger.error(str(fs_error))
                    if self.progress_tracker:
                        self.progress_tracker.show_error_with_suggestions(str(fs_error), fs_error.suggestions)
                    return None
                    
            except yt_dlp.DownloadError as e:
                if attempt < max_retries:
                    wait_time = self.error_handler.get_retry_delay(attempt)
                    self.logger.warning(f"Download failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    if self.progress_tracker:
                        self.progress_tracker.show_stage_message(f"Retrying in {wait_time:.1f} seconds", f"Attempt {attempt + 1}/{max_retries + 1}")
                    time.sleep(wait_time)
                else:
                    network_error = self.error_handler.handle_network_error(e, "video download", max_retries)
                    self.logger.error(str(network_error))
                    if self.progress_tracker:
                        self.progress_tracker.show_error_with_suggestions(str(network_error), network_error.suggestions)
                    return None
                    
            except (OSError, PermissionError) as e:
                # File system related errors
                fs_error = self.error_handler.handle_file_system_error(e, "downloading audio", output_path)
                self.logger.error(str(fs_error))
                if self.progress_tracker:
                    self.progress_tracker.show_error_with_suggestions(str(fs_error), fs_error.suggestions)
                return None
                    
            except Exception as e:
                if attempt < max_retries:
                    wait_time = self.error_handler.get_retry_delay(attempt)
                    self.logger.warning(f"Download failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    if self.progress_tracker:
                        self.progress_tracker.show_stage_message(f"Retrying in {wait_time:.1f} seconds", f"Attempt {attempt + 1}/{max_retries + 1}")
                    time.sleep(wait_time)
                else:
                    # For unexpected errors, treat as network error with generic suggestions
                    network_error = self.error_handler.handle_network_error(e, "video download", max_retries)
                    self.logger.error(str(network_error))
                    if self.progress_tracker:
                        self.progress_tracker.show_error_with_suggestions(str(network_error), network_error.suggestions)
                    return None
        
        return None
    
    def is_playlist_url(self, url: str) -> bool:
        """
        Check if the provided URL is a YouTube playlist URL.
        
        Determines whether a given URL points to a YouTube playlist by attempting
        to extract information and checking for multiple entries. This helps the
        application decide whether to use single video or playlist processing logic.
        
        Args:
            url (str): URL to check for playlist characteristics
            
        Returns:
            bool: True if URL is a playlist containing multiple videos,
                  False if it's a single video or invalid URL
                  
        Example:
            >>> extractor = YouTubeExtractor(options)
            >>> is_playlist = extractor.is_playlist_url(
            ...     "https://youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMt9xaJGA6H_VjlXEL"
            ... )
            >>> if is_playlist:
            ...     print("Processing as playlist")
            ... else:
            ...     print("Processing as single video")
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                # Check if this is a playlist by looking for entries
                return info and 'entries' in info and len(info.get('entries', [])) > 1
        except Exception:
            return False
    
    def get_playlist_info(self, url: str) -> Optional[PlaylistInfo]:
        """
        Retrieve playlist information without downloading.
        
        Extracts comprehensive metadata from a YouTube playlist URL without downloading
        any content. This includes playlist details and information about all contained
        videos, which is essential for planning the download process and providing
        user feedback.
        
        Args:
            url (str): YouTube playlist URL to extract information from
            
        Returns:
            PlaylistInfo: Object containing playlist metadata (title, uploader,
                         video_count) and a list of VideoInfo objects for each
                         video in the playlist
            None: If extraction fails due to network issues, invalid URL, private
                  playlist, or other errors
                  
        Example:
            >>> extractor = YouTubeExtractor(options)
            >>> playlist = extractor.get_playlist_info(
            ...     "https://youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMt9xaJGA6H_VjlXEL"
            ... )
            >>> if playlist:
            ...     print(f"Playlist: {playlist.title}")
            ...     print(f"Videos: {playlist.video_count}")
            ...     for video in playlist.videos[:3]:  # Show first 3
            ...         print(f"  - {video.title}")
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info or 'entries' not in info:
                    self.logger.error(f"No playlist entries found for {url}")
                    return None
                
                # Show progress for large playlists
                entries = info.get('entries', [])
                total_entries = len(entries)
                
                if self.progress_tracker and total_entries > 10:
                    self.progress_tracker.show_stage_message(f"Processing {total_entries} videos in playlist")
                
                # Extract video information from playlist entries with progress
                videos = []
                for i, entry in enumerate(entries):
                    if entry:  # Skip None entries (unavailable videos)
                        video_info = VideoInfo(
                            title=entry.get('title', 'Unknown Title'),
                            uploader=entry.get('uploader', info.get('uploader', 'Unknown Uploader')),
                            duration=entry.get('duration', 0),
                            upload_date=entry.get('upload_date', ''),
                            url=entry.get('webpage_url', entry.get('url', '')),
                            id=entry.get('id', '')
                        )
                        videos.append(video_info)
                        
                        # Show progress for large playlists
                        if self.progress_tracker and total_entries > 20 and (i + 1) % 10 == 0:
                            self.progress_tracker.show_stage_message(f"Processed {i + 1}/{total_entries} videos")
                
                return PlaylistInfo(
                    title=info.get('title', 'Unknown Playlist'),
                    uploader=info.get('uploader', 'Unknown Uploader'),
                    video_count=len(videos),
                    videos=videos
                )
                
        except yt_dlp.DownloadError as e:
            self.logger.error(f"Failed to extract playlist info for {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error extracting playlist info for {url}: {e}")
            return None
    
    def extract_playlist_audio(self, url: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Extract audio from all videos in a YouTube playlist with error recovery.
        
        Processes an entire YouTube playlist by downloading audio from each video
        sequentially. Creates organized folder structure, handles individual video
        failures gracefully, and provides comprehensive progress tracking and
        error reporting.
        
        Args:
            url (str): YouTube playlist URL to process
            max_retries (int, optional): Maximum number of retry attempts per video.
                                       Defaults to 3.
            
        Returns:
            Dict[str, Any]: Comprehensive results dictionary containing:
                - success (bool): Whether any videos were successfully downloaded
                - playlist_title (str): Name of the playlist
                - playlist_folder (str): Path to created playlist folder
                - total_videos (int): Total number of videos in playlist
                - successful_downloads (List[Dict]): List of successful downloads
                - failed_downloads (List[Dict]): List of failed downloads
                - success_count (int): Number of successful downloads
                - failure_count (int): Number of failed downloads
                - error (str): Error message if playlist processing failed entirely
                
        Example:
            >>> extractor = YouTubeExtractor(options, progress_tracker)
            >>> results = extractor.extract_playlist_audio(
            ...     "https://youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMt9xaJGA6H_VjlXEL"
            ... )
            >>> if results['success']:
            ...     print(f"Downloaded {results['success_count']} of {results['total_videos']} videos")
            ...     print(f"Saved to: {results['playlist_folder']}")
        """
        # Show stage message
        if self.progress_tracker:
            self.progress_tracker.show_stage_message("Retrieving playlist information")
        
        # Get playlist information first
        playlist_info = self.get_playlist_info(url)
        if not playlist_info:
            error_msg = 'Failed to retrieve playlist information'
            if self.progress_tracker:
                self.progress_tracker.show_error_with_suggestions(
                    error_msg,
                    ["Check if the playlist URL is valid", "Verify the playlist is public", "Check internet connection"]
                )
            return {
                'success': False,
                'error': error_msg,
                'successful_downloads': [],
                'failed_downloads': [],
                'playlist_folder': None
            }
        
        # Show playlist information
        if self.progress_tracker:
            self.progress_tracker.show_playlist_info(playlist_info.title, playlist_info.uploader, playlist_info.video_count)
            
            # Ask for confirmation for large playlists
            if not self.progress_tracker.confirm_large_playlist(playlist_info.video_count):
                return {
                    'success': False,
                    'error': 'Operation cancelled by user',
                    'successful_downloads': [],
                    'failed_downloads': [],
                    'playlist_folder': None
                }
        
        # Create playlist folder
        playlist_folder_name = create_safe_directory_name(playlist_info.title)
        playlist_folder_path = os.path.join(self.options.output_dir, playlist_folder_name)
        
        try:
            os.makedirs(playlist_folder_path, exist_ok=True)
        except (OSError, PermissionError) as e:
            fs_error = self.error_handler.handle_file_system_error(e, "creating playlist folder", playlist_folder_path)
            self.logger.error(str(fs_error))
            return {
                'success': False,
                'error': str(fs_error),
                'successful_downloads': [],
                'failed_downloads': [],
                'playlist_folder': None
            }
        
        if self.progress_tracker:
            self.progress_tracker.show_stage_message("Creating playlist folder", playlist_folder_path)
        
        self.logger.info(f"Processing playlist: {playlist_info.title}")
        self.logger.info(f"Found {playlist_info.video_count} videos")
        self.logger.info(f"Saving to folder: {playlist_folder_path}")
        
        # Track results
        successful_downloads = []
        failed_downloads = []
        
        # Create playlist progress tracker
        playlist_progress = PlaylistProgressTracker(
            playlist_info.video_count, 
            verbose=self.progress_tracker.verbose if self.progress_tracker else False
        )
        
        # Create a temporary extractor with playlist folder as output directory
        playlist_options = ExtractionOptions(
            quality=self.options.quality,
            output_dir=playlist_folder_path,
            format_template=self.options.format_template,
            embed_metadata=self.options.embed_metadata
        )
        # Don't pass progress tracker to avoid duplicate progress displays
        playlist_extractor = YouTubeExtractor(playlist_options)
        
        # Process each video sequentially
        for i, video in enumerate(playlist_info.videos, 1):
            playlist_progress.start_video(i, video.title)
            self.logger.info(f"Processing video {i}/{playlist_info.video_count}: {video.title}")
            
            try:
                # Extract audio for this video
                output_path = playlist_extractor.extract_video_audio(video.url, max_retries)
                
                if output_path:
                    successful_downloads.append({
                        'title': video.title,
                        'url': video.url,
                        'output_path': output_path
                    })
                    playlist_progress.video_success(video.title, output_path)
                    self.logger.info(f"Successfully downloaded: {video.title}")
                else:
                    error_msg = 'Download failed after retries'
                    failed_downloads.append({
                        'title': video.title,
                        'url': video.url,
                        'error': error_msg
                    })
                    playlist_progress.video_failed(video.title, error_msg)
                    self.logger.error(f"Failed to download: {video.title}")
                    
            except Exception as e:
                error_msg = str(e)
                failed_downloads.append({
                    'title': video.title,
                    'url': video.url,
                    'error': error_msg
                })
                playlist_progress.video_failed(video.title, error_msg)
                self.logger.error(f"Error processing {video.title}: {e}")
                # Continue with next video instead of stopping
                continue
        
        # Return comprehensive results
        return {
            'success': len(successful_downloads) > 0,
            'playlist_title': playlist_info.title,
            'playlist_folder': playlist_folder_path,
            'total_videos': playlist_info.video_count,
            'successful_downloads': successful_downloads,
            'failed_downloads': failed_downloads,
            'success_count': len(successful_downloads),
            'failure_count': len(failed_downloads)
        }
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if the provided URL is a valid YouTube URL.
        
        Checks whether a given URL is a valid YouTube video or playlist URL that
        can be processed by the extractor. Uses the error handler's validation
        logic to ensure consistency across the application.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if URL is a valid YouTube URL that can be processed,
                  False if URL is invalid, malformed, or not accessible
                  
        Example:
            >>> extractor = YouTubeExtractor(options)
            >>> valid = extractor.validate_url("https://youtube.com/watch?v=dQw4w9WgXcQ")
            >>> if valid:
            ...     print("URL is valid and can be processed")
            ... else:
            ...     print("Invalid YouTube URL")
        """
        try:
            self.error_handler.validate_url(url)
            return True
        except (URLValidationError, NetworkError):
            return False
    
    def validate_url_lazy(self, url: str) -> bool:
        """
        Fast URL validation without full content checking.
        
        Performs basic URL format validation without fetching all playlist content.
        Much faster for large playlists but less thorough than full validation.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if URL format is valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        if not url.startswith(('http://', 'https://')):
            return False
        
        if 'youtube.com' not in url and 'youtu.be' not in url:
            return False
            
        return True