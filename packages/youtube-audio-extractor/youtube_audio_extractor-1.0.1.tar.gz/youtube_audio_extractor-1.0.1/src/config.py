"""Application configuration and default settings."""

import os
from pathlib import Path
from typing import Dict, Any


class AppConfig:
    """
    Application configuration with default settings.
    
    Centralized configuration class that holds all default values, supported
    options, and application metadata. Provides methods for validation and
    configuration management throughout the application.
    
    This class serves as a single source of truth for all configurable
    parameters and ensures consistency across different components.
    
    Attributes:
        APP_NAME (str): Application display name
        APP_VERSION (str): Current application version
        DEFAULT_QUALITY (str): Default audio quality in kbps
        DEFAULT_OUTPUT_DIR (str): Default output directory name
        SUPPORTED_QUALITIES (List[str]): List of supported quality options
        QUALITY_BITRATES (Dict[str, str]): Mapping of quality to ffmpeg bitrates
        Various other default settings for behavior, network, and file system
        
    Example:
        >>> config = AppConfig()
        >>> print(config.DEFAULT_QUALITY)  # "320"
        >>> print(config.validate_quality("192"))  # True
    """
    
    # Application metadata
    APP_NAME = "YouTube Audio Extractor"
    APP_VERSION = "1.0.0"
    
    # Default extraction settings
    DEFAULT_QUALITY = "320"  # kbps
    DEFAULT_OUTPUT_DIR = "downloads"
    DEFAULT_FORMAT_TEMPLATE = "%(title)s.%(ext)s"
    
    # Supported quality options
    SUPPORTED_QUALITIES = ["128", "192", "320"]
    
    # Quality bitrate mapping
    QUALITY_BITRATES = {
        "128": "128k",
        "192": "192k", 
        "320": "320k"
    }
    
    # Default behavior settings
    DEFAULT_EMBED_METADATA = True
    DEFAULT_CREATE_PLAYLIST_FOLDERS = True
    DEFAULT_VERBOSE = False
    
    # Network and retry settings
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 30
    
    # File system settings
    MAX_FILENAME_LENGTH = 200
    REQUIRED_FREE_SPACE_MB = 10
    
    # Logging configuration
    LOG_FORMAT_VERBOSE = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FORMAT_SIMPLE = '%(message)s'
    
    @classmethod
    def get_default_options(cls) -> Dict[str, Any]:
        """
        Get default extraction options as a dictionary.
        
        Returns a dictionary containing all default configuration options
        that can be used to initialize extraction components. This provides
        a convenient way to get all defaults in a single call.
        
        Returns:
            Dict[str, Any]: Dictionary containing default extraction options
                          including quality, output directory, format template,
                          metadata settings, and other behavioral options
                          
        Example:
            >>> defaults = AppConfig.get_default_options()
            >>> print(defaults['quality'])  # "320"
            >>> print(defaults['embed_metadata'])  # True
        """
        return {
            "quality": cls.DEFAULT_QUALITY,
            "output_dir": cls.DEFAULT_OUTPUT_DIR,
            "format_template": cls.DEFAULT_FORMAT_TEMPLATE,
            "embed_metadata": cls.DEFAULT_EMBED_METADATA,
            "create_playlist_folders": cls.DEFAULT_CREATE_PLAYLIST_FOLDERS,
            "verbose": cls.DEFAULT_VERBOSE,
            "max_retries": cls.MAX_RETRIES,
            "timeout": cls.TIMEOUT_SECONDS
        }
    
    @classmethod
    def validate_quality(cls, quality: str) -> bool:
        """
        Validate if the given quality is supported.
        
        Checks whether the provided quality string is one of the supported
        audio quality options. Used for parameter validation in CLI and
        other components.
        
        Args:
            quality (str): Quality string to validate (e.g., "128", "192", "320")
            
        Returns:
            bool: True if quality is supported, False otherwise
            
        Example:
            >>> AppConfig.validate_quality("320")  # True
            >>> AppConfig.validate_quality("256")  # False
            >>> AppConfig.validate_quality("192")  # True
        """
        return quality in cls.SUPPORTED_QUALITIES
    
    @classmethod
    def get_output_directory(cls, custom_dir: str = None) -> str:
        """
        Get the output directory, creating it if necessary.
        
        Returns the output directory path, using either the provided custom
        directory or the default. Creates the directory if it doesn't exist
        to ensure it's ready for use.
        
        Args:
            custom_dir (str, optional): Custom output directory path.
                                      If None, uses DEFAULT_OUTPUT_DIR.
            
        Returns:
            str: Path to the output directory (created if necessary)
            
        Example:
            >>> AppConfig.get_output_directory()  # "downloads"
            >>> AppConfig.get_output_directory("~/Music")  # "~/Music"
        """
        output_dir = custom_dir or cls.DEFAULT_OUTPUT_DIR
        
        # Create directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        return output_dir
    
    @classmethod
    def get_app_info(cls) -> Dict[str, str]:
        """
        Get application information.
        
        Returns basic application metadata including name and version.
        Useful for displaying application information in CLI output,
        logs, and error messages.
        
        Returns:
            Dict[str, str]: Dictionary containing 'name' and 'version' keys
                          with corresponding application information
                          
        Example:
            >>> info = AppConfig.get_app_info()
            >>> print(f"{info['name']} v{info['version']}")
            >>> # Output: YouTube Audio Extractor v1.0.0
        """
        return {
            "name": cls.APP_NAME,
            "version": cls.APP_VERSION
        }


# Global configuration instance
config = AppConfig()