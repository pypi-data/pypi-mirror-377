"""Progress tracking and user feedback utilities."""

import sys
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from threading import Lock

import click


@dataclass
class ProgressInfo:
    """
    Information about download progress.
    
    Data class that holds progress information for ongoing downloads.
    Used internally by progress tracking components to maintain state
    and calculate progress metrics.
    
    Attributes:
        filename (str): Name of the file being downloaded
        total_bytes (Optional[int]): Total file size in bytes (if known)
        downloaded_bytes (int): Number of bytes downloaded so far
        speed (Optional[float]): Current download speed in bytes per second
        eta (Optional[int]): Estimated time to completion in seconds
        status (str): Current download status ("downloading", "finished", "error")
    """
    filename: str
    total_bytes: Optional[int] = None
    downloaded_bytes: int = 0
    speed: Optional[float] = None
    eta: Optional[int] = None
    status: str = "downloading"


class ProgressTracker:
    """
    Handles progress tracking and user feedback for downloads.
    
    Provides comprehensive progress tracking for YouTube downloads including
    real-time progress bars, speed indicators, ETA calculations, and user
    feedback. Integrates with yt-dlp's progress hooks and provides both
    verbose and simple display modes.
    
    The tracker handles single video downloads and provides methods for
    displaying video information, processing stages, and error messages
    with troubleshooting suggestions.
    
    Attributes:
        verbose (bool): Whether to show detailed progress information
        current_progress: Current progress information
        start_time: Download start time for calculations
        lock (threading.Lock): Thread lock for progress updates
        
    Example:
        >>> tracker = ProgressTracker(verbose=True)
        >>> hook = tracker.create_yt_dlp_hook()
        >>> # Use hook with yt-dlp configuration
        >>> tracker.show_video_info("Video Title", "Channel Name", 180)
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the progress tracker.
        
        Sets up the progress tracker with the specified verbosity level
        and initializes internal state for tracking downloads.
        
        Args:
            verbose (bool): Whether to show detailed progress information
                          including timestamps, speed, and ETA
        """
        self.verbose = verbose
        self.current_progress = None
        self.start_time = None
        self.lock = Lock()
        
    def create_yt_dlp_hook(self) -> Callable:
        """
        Create a progress hook for yt-dlp.
        
        Creates a callback function that can be used with yt-dlp's progress_hooks
        configuration to receive real-time download progress updates. The hook
        handles different download states and updates the display accordingly.
        
        Returns:
            Callable: Function that accepts yt-dlp progress dictionaries and
                     updates the progress display. Can be added to yt-dlp's
                     progress_hooks list.
                     
        Example:
            >>> tracker = ProgressTracker()
            >>> ydl_opts = {
            ...     'progress_hooks': [tracker.create_yt_dlp_hook()],
            ...     # other yt-dlp options...
            ... }
        """
        def progress_hook(d: Dict[str, Any]) -> None:
            """Progress hook for yt-dlp downloads."""
            with self.lock:
                if d['status'] == 'downloading':
                    self._update_download_progress(d)
                elif d['status'] == 'finished':
                    self._finish_download_progress(d)
                elif d['status'] == 'error':
                    self._handle_download_error(d)
        
        return progress_hook
    
    def _update_download_progress(self, d: Dict[str, Any]) -> None:
        """Update download progress display."""
        filename = d.get('filename', 'Unknown file')
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes', 0)
        speed = d.get('speed')
        eta = d.get('eta')
        
        # Calculate percentage
        if total_bytes and total_bytes > 0:
            percentage = (downloaded_bytes / total_bytes) * 100
        else:
            percentage = 0
        
        # Format speed
        speed_str = ""
        if speed:
            if speed >= 1024 * 1024:  # MB/s
                speed_str = f" at {speed / (1024 * 1024):.1f} MB/s"
            elif speed >= 1024:  # KB/s
                speed_str = f" at {speed / 1024:.1f} KB/s"
            else:  # B/s
                speed_str = f" at {speed:.0f} B/s"
        
        # Format ETA
        eta_str = ""
        if eta:
            if eta > 60:
                eta_str = f" (ETA: {eta // 60}m {eta % 60}s)"
            else:
                eta_str = f" (ETA: {eta}s)"
        
        # Display progress
        if self.verbose:
            # Detailed progress with speed and ETA
            progress_line = f"\rDownloading: {percentage:.1f}%{speed_str}{eta_str}"
            click.echo(progress_line, nl=False)
        else:
            # Simple progress bar
            bar_length = 30
            filled_length = int(bar_length * percentage / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            progress_line = f"\r[{bar}] {percentage:.1f}%{speed_str}"
            click.echo(progress_line, nl=False)
        
        sys.stdout.flush()
    
    def _finish_download_progress(self, d: Dict[str, Any]) -> None:
        """Handle download completion."""
        click.echo()  # New line after progress
        filename = d.get('filename', 'Unknown file')
        click.echo(f"✓ Download completed: {click.style(filename, fg='green')}")
    
    def _handle_download_error(self, d: Dict[str, Any]) -> None:
        """Handle download errors."""
        click.echo()  # New line after progress
        error_msg = d.get('error', 'Unknown error')
        click.echo(f"✗ Download failed: {click.style(error_msg, fg='red')}")
    
    def show_stage_message(self, stage: str, details: str = "") -> None:
        """
        Display a message for the current processing stage.
        
        Args:
            stage: The current processing stage
            details: Additional details about the stage
        """
        if details:
            message = f"{stage}: {details}"
        else:
            message = stage
        
        if self.verbose:
            timestamp = time.strftime("%H:%M:%S")
            click.echo(f"[{timestamp}] {message}")
        else:
            click.echo(message)
    
    def show_video_info(self, title: str, uploader: str, duration: Optional[int] = None) -> None:
        """
        Display video information in a formatted way.
        
        Args:
            title: Video title
            uploader: Video uploader/channel name
            duration: Video duration in seconds
        """
        click.echo(f"Title: {click.style(title, fg='green')}")
        click.echo(f"Channel: {click.style(uploader, fg='blue')}")
        
        if duration:
            duration_str = f"{duration // 60}:{duration % 60:02d}"
            click.echo(f"Duration: {duration_str}")
    
    def show_playlist_info(self, title: str, uploader: str, video_count: int) -> None:
        """
        Display playlist information in a formatted way.
        
        Args:
            title: Playlist title
            uploader: Playlist uploader/channel name
            video_count: Number of videos in playlist
        """
        click.echo(f"Playlist: {click.style(title, fg='green')}")
        click.echo(f"Channel: {click.style(uploader, fg='blue')}")
        click.echo(f"Videos: {click.style(str(video_count), fg='cyan')}")
    
    def show_processing_summary(self, results: Dict[str, Any]) -> None:
        """
        Display a comprehensive summary of processing results.
        
        Args:
            results: Dictionary containing processing results
        """
        click.echo("\n" + "="*60)
        click.echo(click.style("PROCESSING COMPLETE", fg='green', bold=True))
        click.echo("="*60)
        
        # Single video results
        if 'output_path' in results:
            click.echo(f"✓ Successfully processed: {click.style(results['title'], fg='green')}")
            click.echo(f"Output file: {click.style(results['output_path'], fg='cyan')}")
            return
        
        # Playlist results
        if 'playlist_title' in results:
            click.echo(f"Playlist: {click.style(results['playlist_title'], fg='green')}")
            click.echo(f"Output folder: {click.style(results['playlist_folder'], fg='cyan')}")
            click.echo(f"Total videos: {results['total_videos']}")
            
            # Success/failure counts
            success_count = results.get('success_count', 0)
            failure_count = results.get('failure_count', 0)
            
            if success_count > 0:
                click.echo(f"✓ Successful: {click.style(str(success_count), fg='green')}")
            
            if failure_count > 0:
                click.echo(f"✗ Failed: {click.style(str(failure_count), fg='red')}")
            
            # Show successful downloads
            if results.get('successful_downloads'):
                click.echo(f"\n{click.style('Successfully downloaded:', fg='green')}")
                for download in results['successful_downloads']:
                    click.echo(f"  ✓ {download['title']}")
            
            # Show failed downloads if verbose or if there are failures
            if results.get('failed_downloads') and (self.verbose or failure_count > 0):
                click.echo(f"\n{click.style('Failed downloads:', fg='red')}")
                for failed in results['failed_downloads']:
                    error_msg = failed.get('error', 'Unknown error')
                    if self.verbose:
                        click.echo(f"  ✗ {failed['title']}: {error_msg}")
                    else:
                        click.echo(f"  ✗ {failed['title']}")
            
            # Calculate success rate
            if results['total_videos'] > 0:
                success_rate = (success_count / results['total_videos']) * 100
                click.echo(f"\nSuccess rate: {success_rate:.1f}%")
    
    def show_error_with_suggestions(self, error_msg: str, suggestions: list = None) -> None:
        """
        Display an error message with troubleshooting suggestions.
        
        Args:
            error_msg: The error message to display
            suggestions: List of troubleshooting suggestions
        """
        click.echo(click.style(f"Error: {error_msg}", fg='red'), err=True)
        
        if suggestions:
            click.echo("\nTroubleshooting suggestions:", err=True)
            for i, suggestion in enumerate(suggestions, 1):
                click.echo(f"  {i}. {suggestion}", err=True)
    
    def confirm_large_playlist(self, video_count: int, threshold: int = 10) -> bool:
        """
        Ask user confirmation for processing large playlists.
        
        Args:
            video_count: Number of videos in the playlist
            threshold: Threshold above which to ask for confirmation
            
        Returns:
            True if user confirms, False otherwise
        """
        if video_count <= threshold:
            return True
        
        return click.confirm(
            f"This playlist contains {video_count} videos. Continue?",
            default=True
        )


class PlaylistProgressTracker:
    """
    Specialized progress tracker for playlist processing.
    
    Handles progress tracking for playlist downloads where multiple videos
    are processed sequentially. Provides overall playlist progress, individual
    video status, success/failure tracking, and ETA calculations for the
    entire playlist operation.
    
    Tracks statistics like success rate, elapsed time, and provides detailed
    feedback about which videos succeeded or failed during processing.
    
    Attributes:
        total_videos (int): Total number of videos to process
        verbose (bool): Whether to show detailed progress information
        current_video (int): Currently processing video number
        successful (int): Number of successfully processed videos
        failed (int): Number of failed videos
        start_time (float): Processing start time for ETA calculations
        
    Example:
        >>> tracker = PlaylistProgressTracker(total_videos=10, verbose=True)
        >>> tracker.start_video(1, "First Video Title")
        >>> tracker.video_success("First Video Title", "/path/to/output.mp3")
        >>> summary = tracker.get_summary()
    """
    
    def __init__(self, total_videos: int, verbose: bool = False):
        """
        Initialize playlist progress tracker.
        
        Sets up tracking for a playlist with the specified number of videos
        and initializes counters and timing information.
        
        Args:
            total_videos (int): Total number of videos to process in the playlist
            verbose (bool): Whether to show detailed progress information
                          including ETA calculations and detailed error messages
        """
        self.total_videos = total_videos
        self.verbose = verbose
        self.current_video = 0
        self.successful = 0
        self.failed = 0
        self.start_time = time.time()
    
    def start_video(self, video_number: int, title: str) -> None:
        """
        Start processing a video.
        
        Args:
            video_number: Current video number (1-based)
            title: Video title
        """
        self.current_video = video_number
        
        # Show progress header
        progress_str = f"[{video_number}/{self.total_videos}]"
        click.echo(f"\n{click.style(progress_str, fg='cyan')} Processing: {title}")
        
        if self.verbose:
            elapsed = time.time() - self.start_time
            if video_number > 1:
                avg_time = elapsed / (video_number - 1)
                remaining_videos = self.total_videos - video_number + 1
                eta_seconds = avg_time * remaining_videos
                eta_str = f"ETA: {int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
                click.echo(f"  {eta_str}")
    
    def video_success(self, title: str, output_path: str) -> None:
        """
        Mark a video as successfully processed.
        
        Args:
            title: Video title
            output_path: Path to output file
        """
        self.successful += 1
        click.echo(f"  ✓ {click.style('Success', fg='green')}: {output_path}")
    
    def video_failed(self, title: str, error: str) -> None:
        """
        Mark a video as failed.
        
        Args:
            title: Video title
            error: Error message
        """
        self.failed += 1
        if self.verbose:
            click.echo(f"  ✗ {click.style('Failed', fg='red')}: {error}")
        else:
            click.echo(f"  ✗ {click.style('Failed', fg='red')}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get processing summary.
        
        Returns:
            Dictionary with summary information
        """
        elapsed = time.time() - self.start_time
        return {
            'total_videos': self.total_videos,
            'successful': self.successful,
            'failed': self.failed,
            'elapsed_time': elapsed,
            'success_rate': (self.successful / self.total_videos * 100) if self.total_videos > 0 else 0
        }