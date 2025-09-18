"""Comprehensive error handling for YouTube Audio Extractor."""

import os
import shutil
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import yt_dlp


class YouTubeExtractorError(Exception):
    """
    Base exception for YouTube Extractor errors.

    Custom exception class that extends the standard Exception to include
    troubleshooting suggestions. All specific error types in the application
    inherit from this base class to provide consistent error handling.

    Attributes:
        suggestions (List[str]): List of troubleshooting suggestions for the user

    Example:
        >>> error = YouTubeExtractorError(
        ...     "Something went wrong",
        ...     ["Try again", "Check your connection"]
        ... )
        >>> print(error.suggestions)  # ["Try again", "Check your connection"]
    """

    def __init__(self, message: str, suggestions: Optional[List[str]] = None):
        """
        Initialize the error with message and suggestions.

        Args:
            message (str): Human-readable error message describing what went wrong
            suggestions (Optional[List[str]]): List of troubleshooting suggestions
                                             to help the user resolve the issue
        """
        super().__init__(message)
        self.suggestions = suggestions or []


class NetworkError(YouTubeExtractorError):
    """
    Network-related errors.

    Raised when network connectivity issues prevent successful operation,
    such as timeouts, connection failures, or DNS resolution problems.

    Example:
        >>> raise NetworkError(
        ...     "Connection timeout",
        ...     ["Check internet connection", "Try again later"]
        ... )
    """

    pass


class FileSystemError(YouTubeExtractorError):
    """
    File system-related errors.

    Raised when file system operations fail due to permissions, disk space,
    invalid paths, or other file system issues.

    Example:
        >>> raise FileSystemError(
        ...     "Permission denied",
        ...     ["Check directory permissions", "Try different output directory"]
        ... )
    """

    pass


class ConversionError(YouTubeExtractorError):
    """
    Audio conversion-related errors.

    Raised when audio conversion operations fail due to missing dependencies
    (like ffmpeg), unsupported formats, or conversion process errors.

    Example:
        >>> raise ConversionError(
        ...     "ffmpeg not found",
        ...     ["Install ffmpeg", "Add ffmpeg to PATH"]
        ... )
    """

    pass


class URLValidationError(YouTubeExtractorError):
    """
    URL validation errors.

    Raised when provided URLs are invalid, inaccessible, or not supported
    YouTube URLs. Includes format validation and accessibility checks.

    Example:
        >>> raise URLValidationError(
        ...     "Invalid YouTube URL",
        ...     ["Check URL format", "Verify video is public"]
        ... )
    """

    pass


class ErrorHandler:
    """
    Centralized error handling and validation.

    Provides comprehensive error handling, validation, and user-friendly error
    messages with troubleshooting suggestions. Handles URL validation, file
    system checks, network errors, and dependency validation.

    This class ensures consistent error handling across the application and
    provides helpful suggestions to users for resolving common issues.

    Attributes:
        logger (logging.Logger): Logger instance for error reporting

    Example:
        >>> handler = ErrorHandler()
        >>> try:
        ...     handler.validate_url("invalid-url")
        ... except URLValidationError as e:
        ...     print(f"Error: {e}")
        ...     for suggestion in e.suggestions:
        ...         print(f"  - {suggestion}")
    """

    def __init__(self):
        """
        Initialize the error handler.

        Sets up the error handler with logging capabilities for consistent
        error reporting throughout the application.
        """
        self.logger = logging.getLogger(__name__)

    def validate_url(self, url: str) -> None:
        """
        Validate YouTube URL format and accessibility.

        Args:
            url: URL to validate

        Raises:
            URLValidationError: If URL is invalid or inaccessible
        """
        if not url or not isinstance(url, str):
            raise URLValidationError(
                "URL cannot be empty", ["Provide a valid YouTube video or playlist URL"]
            )

        # Basic format validation
        if not url.startswith(("http://", "https://")):
            raise URLValidationError(
                "URL must start with http:// or https://",
                [
                    "Ensure the URL includes the protocol (https://)",
                    "Copy the full URL from your browser",
                ],
            )

        if "youtube.com" not in url and "youtu.be" not in url:
            raise URLValidationError(
                "URL must be a YouTube URL",
                [
                    "Ensure the URL is from youtube.com or youtu.be",
                    "Check that you copied the complete URL",
                    "Verify the URL works in your browser",
                ],
            )

        # Test accessibility with yt-dlp
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                ydl.extract_info(url, download=False)
        except yt_dlp.DownloadError as e:
            error_msg = str(e).lower()

            if "private" in error_msg or "unavailable" in error_msg:
                raise URLValidationError(
                    f"Video/playlist is not accessible: {e}",
                    [
                        "Check if the video/playlist is public",
                        "Verify the video hasn't been deleted",
                        "Try accessing the URL in your browser",
                        "Check if you need to be logged in to access the content",
                    ],
                )
            elif "network" in error_msg or "connection" in error_msg:
                raise NetworkError(
                    f"Network error while validating URL: {e}",
                    [
                        "Check your internet connection",
                        "Try again in a few moments",
                        "Check if YouTube is accessible from your location",
                    ],
                )
            else:
                raise URLValidationError(
                    f"Invalid or inaccessible URL: {e}",
                    [
                        "Verify the URL is correct",
                        "Check if the video/playlist exists",
                        "Try copying the URL again from your browser",
                    ],
                )
        except Exception as e:
            raise URLValidationError(
                f"Unexpected error validating URL: {e}",
                [
                    "Check your internet connection",
                    "Verify the URL format is correct",
                    "Try again later",
                ],
            )

    def validate_file_system(
        self, output_dir: str, required_space_mb: int = 100
    ) -> None:
        """
        Validate file system permissions and available space.

        Args:
            output_dir: Output directory path
            required_space_mb: Required free space in MB

        Raises:
            FileSystemError: If file system validation fails
        """
        try:
            # Convert to Path object for easier handling
            output_path = Path(output_dir)

            # Check if parent directory exists and is writable
            if not output_path.exists():
                try:
                    output_path.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    raise FileSystemError(
                        f"Permission denied creating directory: {output_dir}",
                        [
                            "Check directory permissions",
                            "Try running with appropriate permissions",
                            "Choose a different output directory",
                            "Ensure the parent directory is writable",
                        ],
                    )
                except OSError as e:
                    raise FileSystemError(
                        f"Cannot create output directory: {e}",
                        [
                            "Check if the path is valid",
                            "Ensure sufficient permissions",
                            "Try a different output directory",
                            "Check available disk space",
                        ],
                    )

            # Check write permissions
            if not os.access(output_path, os.W_OK):
                raise FileSystemError(
                    f"No write permission for directory: {output_dir}",
                    [
                        "Check directory permissions",
                        "Try running with appropriate permissions",
                        "Choose a different output directory",
                    ],
                )

            # Check available disk space
            try:
                stat = shutil.disk_usage(output_path)
                available_mb = stat.free / (1024 * 1024)

                if available_mb < required_space_mb:
                    raise FileSystemError(
                        f"Insufficient disk space. Available: {available_mb:.1f}MB, Required: {required_space_mb}MB",
                        [
                            "Free up disk space",
                            "Choose a different output directory",
                            "Delete unnecessary files",
                        ],
                    )
            except OSError as e:
                self.logger.warning(f"Could not check disk space: {e}")
                # Don't fail on disk space check errors, just log a warning

        except FileSystemError:
            raise  # Re-raise FileSystemError as-is
        except Exception as e:
            raise FileSystemError(
                f"Unexpected file system error: {e}",
                [
                    "Check the output directory path",
                    "Verify file system permissions",
                    "Try a different output directory",
                ],
            )

    def validate_ffmpeg(self) -> None:
        """
        Validate ffmpeg availability.

        Raises:
            ConversionError: If ffmpeg is not available
        """
        if not shutil.which("ffmpeg"):
            raise ConversionError(
                "ffmpeg not found in system PATH",
                [
                    "Install ffmpeg using your system package manager",
                    "On macOS: brew install ffmpeg",
                    "On Ubuntu/Debian: sudo apt install ffmpeg",
                    "On Windows: Download from https://ffmpeg.org/download.html",
                    "Ensure ffmpeg is added to your system PATH",
                ],
            )

    def handle_network_error(
        self, error: Exception, operation: str, max_retries: int = 3
    ) -> NetworkError:
        """
        Handle network-related errors with appropriate suggestions.

        Args:
            error: The original error
            operation: Description of the operation that failed
            max_retries: Maximum number of retries attempted

        Returns:
            NetworkError: Formatted network error with suggestions
        """
        error_msg = str(error).lower()

        suggestions = [
            "Check your internet connection",
            "Verify YouTube is accessible from your location",
            "Try again in a few moments",
        ]

        if "timeout" in error_msg:
            suggestions.extend(
                ["Check if your connection is stable", "Try using a different network"]
            )
        elif "connection refused" in error_msg or "connection reset" in error_msg:
            suggestions.extend(
                ["Check firewall settings", "Try using a VPN if YouTube is blocked"]
            )
        elif "dns" in error_msg:
            suggestions.extend(
                [
                    "Check DNS settings",
                    "Try using a different DNS server (8.8.8.8, 1.1.1.1)",
                ]
            )

        if max_retries > 0:
            suggestions.append(f"Operation was retried {max_retries} times")

        return NetworkError(f"Network error during {operation}: {error}", suggestions)

    def handle_conversion_error(
        self, error: Exception, input_file: str, output_file: str
    ) -> ConversionError:
        """
        Handle audio conversion errors with appropriate suggestions.

        Args:
            error: The original error
            input_file: Input file path
            output_file: Output file path

        Returns:
            ConversionError: Formatted conversion error with suggestions
        """
        error_msg = str(error).lower()

        suggestions = [
            "Verify ffmpeg is properly installed",
            "Check if the input file is not corrupted",
            "Ensure sufficient disk space",
        ]

        if "permission" in error_msg:
            suggestions.extend(
                [
                    "Check file permissions",
                    "Ensure the output directory is writable",
                    "Try running with appropriate permissions",
                ]
            )
        elif "space" in error_msg or "disk" in error_msg:
            suggestions.extend(
                ["Free up disk space", "Choose a different output directory"]
            )
        elif "codec" in error_msg or "format" in error_msg:
            suggestions.extend(
                [
                    "The audio format may not be supported",
                    "Try downloading the original format without conversion",
                ]
            )

        return ConversionError(f"Audio conversion failed: {error}", suggestions)

    def handle_file_system_error(
        self, error: Exception, operation: str, file_path: str
    ) -> FileSystemError:
        """
        Handle file system errors with appropriate suggestions.

        Args:
            error: The original error
            operation: Description of the operation that failed
            file_path: File or directory path involved

        Returns:
            FileSystemError: Formatted file system error with suggestions
        """
        error_msg = str(error).lower()

        suggestions = []

        if "permission" in error_msg:
            suggestions.extend(
                [
                    "Check file/directory permissions",
                    "Try running with appropriate permissions",
                    "Ensure you have write access to the directory",
                ]
            )
        elif "space" in error_msg or "disk full" in error_msg:
            suggestions.extend(
                [
                    "Free up disk space",
                    "Choose a different output directory",
                    "Delete unnecessary files",
                ]
            )
        elif "not found" in error_msg:
            suggestions.extend(
                [
                    "Check if the path exists",
                    "Verify the file/directory name is correct",
                    "Ensure the parent directory exists",
                ]
            )
        elif "exists" in error_msg:
            suggestions.extend(
                [
                    "File already exists",
                    "Choose a different filename",
                    "Delete the existing file if safe to do so",
                ]
            )
        else:
            suggestions.extend(
                [
                    "Check the file/directory path",
                    "Verify file system permissions",
                    "Try a different location",
                ]
            )

        return FileSystemError(
            f"File system error during {operation}: {error}", suggestions
        )

    def get_retry_delay(
        self, attempt: int, base_delay: float = 1.0, max_delay: float = 30.0
    ) -> float:
        """
        Calculate retry delay using exponential backoff.

        Args:
            attempt: Current attempt number (0-based)
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds

        Returns:
            Delay in seconds
        """
        delay = base_delay * (2**attempt)
        return min(delay, max_delay)
