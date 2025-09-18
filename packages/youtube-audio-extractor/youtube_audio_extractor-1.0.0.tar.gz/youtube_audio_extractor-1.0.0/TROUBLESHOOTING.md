# YouTube Audio Extractor - Troubleshooting Guide

This guide helps you diagnose and resolve common issues when using the YouTube Audio Extractor.

## Quick Diagnostics

### System Check Commands

Run these commands to verify your system setup:

```bash
# Check Python version (should be 3.8+)
python --version

# Check ffmpeg installation
ffmpeg -version

# Check required Python packages
pip list | grep -E "(yt-dlp|ffmpeg|mutagen|click)"

# Test with a known working video
python -m src.main -v "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

## Common Error Messages and Solutions

### 1. ffmpeg Not Found

**Error Messages:**
```
Error: ffmpeg is not installed or not found in PATH
ConversionError: ffmpeg not found in system PATH
```

**Cause:** ffmpeg is not installed or not accessible from the command line.

**Solutions:**

**On macOS:**
```bash
# Using Homebrew (recommended)
brew install ffmpeg

# Using MacPorts
sudo port install ffmpeg

# Verify installation
ffmpeg -version
```

**On Ubuntu/Debian:**
```bash
# Update package list
sudo apt update

# Install ffmpeg
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

**On Windows:**
1. Download ffmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your system PATH
4. Restart command prompt and test: `ffmpeg -version`

**Alternative Windows installation:**
```bash
# Using Chocolatey
choco install ffmpeg

# Using Scoop
scoop install ffmpeg
```

### 2. Permission Denied Errors

**Error Messages:**
```
Error: Permission denied when creating output directory
PermissionError: [Errno 13] Permission denied: '/path/to/directory'
```

**Cause:** Insufficient permissions to write to the specified directory.

**Solutions:**

**Change output directory:**
```bash
# Use your home directory
python -m src.main -o ~/Downloads "URL"

# Use a directory you own
python -m src.main -o ./my_downloads "URL"
```

**Fix directory permissions (macOS/Linux):**
```bash
# Make directory writable
chmod 755 /path/to/directory

# Change ownership if needed
sudo chown $USER:$USER /path/to/directory
```

**Create directory first:**
```bash
# Create the directory manually
mkdir -p ~/Music/YouTube
python -m src.main -o ~/Music/YouTube "URL"
```

### 3. Network and URL Issues

**Error Messages:**
```
Error: Video is unavailable or private
Error: The provided URL is not a valid YouTube URL
URLValidationError: Invalid YouTube URL format
NetworkError: Network timeout during download
```

**Cause:** Network connectivity issues, invalid URLs, or restricted content.

**Solutions:**

**Verify URL format:**
```bash
# Correct formats:
https://www.youtube.com/watch?v=VIDEO_ID
https://youtube.com/watch?v=VIDEO_ID
https://www.youtube.com/playlist?list=PLAYLIST_ID

# Test with a known working URL:
python -m src.main "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

**Check network connectivity:**
```bash
# Test internet connection
ping google.com

# Test YouTube access
curl -I https://www.youtube.com
```

**Try different approaches:**
```bash
# Use verbose mode for detailed error info
python -m src.main -v "URL"

# Try lower quality for faster download
python -m src.main -q 128 "URL"

# Test the URL in a web browser first
```

### 4. Disk Space Issues

**Error Messages:**
```
Error: Insufficient disk space
FileSystemError: No space left on device
```

**Cause:** Not enough free disk space for the download.

**Solutions:**

**Check available space:**
```bash
# On macOS/Linux
df -h

# On Windows
dir
```

**Free up space or change location:**
```bash
# Use a different drive/directory with more space
python -m src.main -o /path/to/larger/drive "URL"

# Use lower quality to reduce file size
python -m src.main -q 128 "URL"
```

### 5. Python Package Issues

**Error Messages:**
```
ImportError: No module named 'yt_dlp'
ModuleNotFoundError: No module named 'ffmpeg'
```

**Cause:** Required Python packages are not installed.

**Solutions:**

**Install missing packages:**
```bash
# Install all requirements
pip install -r requirements.txt

# Install individual packages
pip install yt-dlp ffmpeg-python mutagen click

# Upgrade existing packages
pip install --upgrade yt-dlp ffmpeg-python mutagen click
```

**Check Python environment:**
```bash
# Verify you're using the correct Python
which python
which pip

# Check installed packages
pip list

# If using virtual environment, activate it first
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 6. Playlist Issues

**Error Messages:**
```
Error: Could not retrieve playlist information
Error: Playlist not found or is private
```

**Cause:** Playlist is private, deleted, or URL is incorrect.

**Solutions:**

**Verify playlist accessibility:**
```bash
# Check if playlist is public by opening in browser
# Try a known public playlist for testing:
python -m src.main "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMt9xaJGA6H_VjlXEL"
```

**Handle large playlists:**
```bash
# Use verbose mode to monitor progress
python -m src.main -v "PLAYLIST_URL"

# Use lower quality for faster processing
python -m src.main -q 192 "PLAYLIST_URL"
```

### 7. Metadata Issues

**Error Messages:**
```
Warning: Failed to embed metadata
ConversionError: Error embedding metadata
```

**Cause:** Issues with MP3 file format or metadata content.

**Solutions:**

**Disable metadata embedding:**
```bash
# Skip metadata if it's causing issues
python -m src.main --no-metadata "URL"
```

**Try different quality settings:**
```bash
# Some quality settings may work better
python -m src.main -q 192 "URL"
```

## Advanced Troubleshooting

### Enable Debug Logging

**Get detailed error information:**
```bash
# Enable verbose logging
python -m src.main -v "URL" 2>&1 | tee debug.log

# Check the debug.log file for detailed error information
cat debug.log
```

### Test Individual Components

**Test yt-dlp directly:**
```bash
# Test if yt-dlp can access the video
yt-dlp --list-formats "URL"

# Test basic download
yt-dlp -f "bestaudio" "URL"
```

**Test ffmpeg directly:**
```bash
# Test ffmpeg conversion
ffmpeg -i input.webm -acodec mp3 -ab 320k output.mp3
```

### Environment Issues

**Virtual Environment Problems:**
```bash
# Create fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # macOS/Linux
# or
fresh_env\Scripts\activate     # Windows

# Install requirements in clean environment
pip install -r requirements.txt

# Test the tool
python -m src.main "URL"
```

**Path Issues:**
```bash
# Check if the tool is in your PATH
which youtube-audio-extractor

# Run from the project directory
cd /path/to/youtube-audio-extractor
python -m src.main "URL"
```

## Performance Issues

### Slow Downloads

**Causes and Solutions:**

**Network bandwidth:**
```bash
# Use lower quality for faster downloads
python -m src.main -q 128 "URL"

# Test network speed
speedtest-cli  # if installed
```

**Large playlists:**
```bash
# Monitor progress with verbose output
python -m src.main -v "PLAYLIST_URL"

# Process smaller batches if needed
```

### High CPU/Memory Usage

**Solutions:**
```bash
# Use lower quality settings
python -m src.main -q 128 "URL"

# Process one video at a time instead of large playlists
# Close other applications to free up resources
```

## Platform-Specific Issues

### macOS Issues

**Gatekeeper warnings:**
```bash
# If macOS blocks ffmpeg execution
xattr -d com.apple.quarantine /usr/local/bin/ffmpeg
```

**Permission issues with directories:**
```bash
# Use directories in your home folder
python -m src.main -o ~/Music "URL"
```

### Windows Issues

**Path length limitations:**
```bash
# Use shorter output paths
python -m src.main -o C:\Music "URL"
```

**Antivirus interference:**
- Add the project directory to antivirus exclusions
- Temporarily disable real-time scanning during downloads

### Linux Issues

**Missing system libraries:**
```bash
# Install additional dependencies
sudo apt install python3-dev build-essential

# For audio processing
sudo apt install libavcodec-extra
```

## Getting Help

### Collect Information for Bug Reports

**System information:**
```bash
# Gather system details
python --version
ffmpeg -version
pip list | grep -E "(yt-dlp|ffmpeg|mutagen|click)"
uname -a  # On macOS/Linux
```

**Error reproduction:**
```bash
# Run with verbose logging and save output
python -m src.main -v "PROBLEMATIC_URL" 2>&1 | tee error_report.log
```

### Community Resources

1. **Check the project's issue tracker** for similar problems
2. **Search YouTube-dl/yt-dlp documentation** for URL format issues
3. **Test with the latest version** of dependencies
4. **Provide complete error messages** when asking for help

### Last Resort Solutions

**Complete reinstallation:**
```bash
# Remove and reinstall all dependencies
pip uninstall yt-dlp ffmpeg-python mutagen click
pip install -r requirements.txt

# Or create fresh environment
python -m venv new_env
source new_env/bin/activate
pip install -r requirements.txt
```

**Alternative approaches:**
```bash
# Try different video if the issue is video-specific
# Use different output directory if the issue is path-related
# Try different quality settings if the issue is conversion-related
```

Remember: Most issues are related to missing dependencies (especially ffmpeg), network connectivity, or file permissions. Start with the basic system checks before diving into advanced troubleshooting.