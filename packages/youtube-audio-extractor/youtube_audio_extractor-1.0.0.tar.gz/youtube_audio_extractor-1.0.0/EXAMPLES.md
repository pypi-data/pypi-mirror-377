# YouTube Audio Extractor - Usage Examples

This document provides comprehensive examples of how to use the YouTube Audio Extractor for various scenarios.

## Basic Usage Examples

### Single Video Download

**Download with default settings (320kbps, downloads folder):**
```bash
python -m src.main "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Download with custom quality:**
```bash
python -m src.main -q 192 "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Download to specific directory:**
```bash
python -m src.main -o ~/Music "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Download with verbose logging:**
```bash
python -m src.main -v "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Playlist Download

**Download entire playlist:**
```bash
python -m src.main "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMt9xaJGA6H_VjlXEL"
```

**Download playlist with custom settings:**
```bash
python -m src.main -q 192 -o ~/Music/Playlists "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMt9xaJGA6H_VjlXEL"
```

**Download playlist without creating playlist folder:**
```bash
python -m src.main --no-playlist-folder "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMt9xaJGA6H_VjlXEL"
```

## Advanced Usage Examples

### Quality and Format Options

**High-quality download (320kbps):**
```bash
python -m src.main -q 320 "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Balanced quality (192kbps) for faster downloads:**
```bash
python -m src.main -q 192 "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Lower quality (128kbps) for limited bandwidth:**
```bash
python -m src.main -q 128 "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Metadata Options

**Download without metadata embedding:**
```bash
python -m src.main --no-metadata "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Download with metadata (default behavior):**
```bash
python -m src.main --metadata "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Output Organization

**Custom output directory:**
```bash
python -m src.main -o "/Users/username/Music/YouTube" "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Relative path output:**
```bash
python -m src.main -o "./downloads/music" "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Home directory output:**
```bash
python -m src.main -o "~/Downloads/Audio" "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Real-World Scenarios

### Scenario 1: Music Collection Building

**Download a music playlist for offline listening:**
```bash
# Create dedicated music directory
mkdir -p ~/Music/YouTube

# Download high-quality playlist with metadata
python -m src.main -q 320 -o ~/Music/YouTube -v \
  "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMt9xaJGA6H_VjlXEL"
```

### Scenario 2: Podcast Archive

**Download educational content with lower quality for space saving:**
```bash
# Create podcast directory
mkdir -p ~/Podcasts/YouTube

# Download with lower quality since speech doesn't need high bitrate
python -m src.main -q 128 -o ~/Podcasts/YouTube \
  "https://www.youtube.com/playlist?list=PODCAST_PLAYLIST_ID"
```

### Scenario 3: Quick Single Download

**Fast download of a single video:**
```bash
python -m src.main -q 192 "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Scenario 4: Batch Processing Multiple URLs

**Process multiple videos (using shell scripting):**
```bash
#!/bin/bash
# save as download_videos.sh

URLS=(
  "https://www.youtube.com/watch?v=VIDEO_ID_1"
  "https://www.youtube.com/watch?v=VIDEO_ID_2"
  "https://www.youtube.com/watch?v=VIDEO_ID_3"
)

for url in "${URLS[@]}"; do
  echo "Downloading: $url"
  python -m src.main -q 320 -o ~/Music/Singles "$url"
done
```

### Scenario 5: Large Playlist with Error Recovery

**Download large playlist with verbose logging for monitoring:**
```bash
python -m src.main -v -q 192 -o ~/Music/LargePlaylists \
  "https://www.youtube.com/playlist?list=LARGE_PLAYLIST_ID" 2>&1 | tee download.log
```

## Command Combinations

### Most Common Combinations

**High-quality single video to Music folder:**
```bash
python -m src.main -q 320 -o ~/Music "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Playlist with balanced quality and verbose output:**
```bash
python -m src.main -q 192 -v "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

**Quick download without metadata:**
```bash
python -m src.main -q 128 --no-metadata "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Power User Combinations

**Maximum quality with custom organization:**
```bash
python -m src.main -q 320 -o ~/Music/YouTube/$(date +%Y-%m-%d) -v \
  "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

**Minimal quality for testing:**
```bash
python -m src.main -q 128 --no-metadata -o /tmp/test \
  "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Using the Installed Package

If you've installed the package with `pip install -e .`, you can use the shorter command:

**Basic usage:**
```bash
youtube-audio-extractor "https://www.youtube.com/watch?v=VIDEO_ID"
```

**With options:**
```bash
youtube-audio-extractor -q 320 -o ~/Music -v "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

## Troubleshooting Examples

### Debug a Failed Download

**Enable verbose logging to see detailed error information:**
```bash
python -m src.main -v "https://www.youtube.com/watch?v=PROBLEMATIC_VIDEO_ID"
```

### Test with Known Working Video

**Use a reliable test video:**
```bash
python -m src.main -v "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

### Check Dependencies

**Verify ffmpeg installation:**
```bash
ffmpeg -version
```

**Check Python dependencies:**
```bash
pip list | grep -E "(yt-dlp|ffmpeg|mutagen|click)"
```

### Test Different Quality Settings

**Try lower quality if high quality fails:**
```bash
# If 320kbps fails, try 192kbps
python -m src.main -q 192 "https://www.youtube.com/watch?v=VIDEO_ID"

# If that fails, try 128kbps
python -m src.main -q 128 "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Output Examples

### Single Video Output Structure
```
downloads/
└── Never_Gonna_Give_You_Up.mp3
```

### Playlist Output Structure
```
downloads/
└── Best_of_Rick_Astley/
    ├── Never_Gonna_Give_You_Up.mp3
    ├── Together_Forever.mp3
    └── Whenever_You_Need_Somebody.mp3
```

### Custom Directory Structure
```
~/Music/YouTube/
├── 2024-01-15/
│   └── Daily_Mix_Playlist/
│       ├── Song_1.mp3
│       └── Song_2.mp3
└── Singles/
    └── Individual_Song.mp3
```

## Performance Optimizations

### New Performance Features

**Fast Validation (--fast-validation):**
- Skips thorough content checking during URL validation
- Reduces validation time from minutes to seconds for large playlists
- Recommended for playlists with 50+ videos

**Batch Processing (--batch-size N):**
- Processes multiple videos with improved efficiency
- Values: 1-10 (default: 5)
- Lower values = more stable, higher values = faster

### Performance Comparison

**Standard validation (80-video playlist):**
```bash
# Takes 3-5 minutes for validation
python -m src.main "LARGE_PLAYLIST_URL"
```

**Optimized for large playlists:**
```bash
# Takes 5-15 seconds for validation
python -m src.main --fast-validation --batch-size 3 "LARGE_PLAYLIST_URL"
```

## Performance Tips

### For Large Playlists
```bash
# Use fast validation and batch processing for large playlists
python -m src.main --fast-validation --batch-size 5 -q 192 "https://www.youtube.com/playlist?list=LARGE_PLAYLIST"

# Monitor progress with verbose output
python -m src.main -v --fast-validation "https://www.youtube.com/playlist?list=PLAYLIST_ID" 2>&1 | tee progress.log

# Maximum performance for very large playlists (100+ videos)
python -m src.main --fast-validation --batch-size 3 -q 128 "https://www.youtube.com/playlist?list=HUGE_PLAYLIST"
```

### For Slow Connections
```bash
# Use lower quality to reduce download time
python -m src.main -q 128 "https://www.youtube.com/watch?v=VIDEO_ID"
```

### For Limited Storage
```bash
# Use 128kbps and disable metadata to minimize file size
python -m src.main -q 128 --no-metadata "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

## Integration Examples

### Shell Script Integration
```bash
#!/bin/bash
# YouTube downloader wrapper script

QUALITY=${1:-320}
OUTPUT_DIR=${2:-~/Music/YouTube}
URL=$3

if [ -z "$URL" ]; then
    echo "Usage: $0 [quality] [output_dir] <youtube_url>"
    echo "Example: $0 192 ~/Music https://youtube.com/watch?v=..."
    exit 1
fi

echo "Downloading with quality: ${QUALITY}kbps"
echo "Output directory: $OUTPUT_DIR"
echo "URL: $URL"

python -m src.main -q "$QUALITY" -o "$OUTPUT_DIR" -v "$URL"
```

### Cron Job Example
```bash
# Add to crontab for daily playlist sync
# 0 2 * * * /path/to/download_daily_playlist.sh

#!/bin/bash
# download_daily_playlist.sh
cd /path/to/youtube-audio-extractor
python -m src.main -q 192 -o ~/Music/Daily \
  "https://www.youtube.com/playlist?list=DAILY_PLAYLIST_ID" >> ~/logs/youtube_download.log 2>&1
```

This examples document covers the most common use cases and provides practical guidance for using the YouTube Audio Extractor effectively.