---
name: yt-video-downloader
description: Download YouTube videos in various formats and qualities. Use when you need to save videos for offline viewing, extract audio, download playlists, or get specific video formats.
metadata: {"openclaw":{"requires":{"bins":["yt-dlp"]},"install":[{"id":"python","kind":"pip","package":"yt-dlp","bins":["yt-dlp"],"label":"Install yt-dlp (pip)"}]}}

# YouTube Video Downloader

## Setup
Install yt-dlp:
```bash
pip install yt-dlp
```

Optional: Install ffmpeg for format conversion:

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
winget install ffmpeg

## Download Video
Best quality (default):
yt-dlp "VIDEO_URL"

Specific quality:

# Best video + best audio (merged)
yt-dlp -f "bestvideo+bestaudio/best" "VIDEO_URL"

# 1080p max
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" "VIDEO_URL"

# 720p max
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" "VIDEO_URL"

# 480p max
yt-dlp -f "bestvideo[height<=480]+bestaudio/best[height<=480]" "VIDEO_URL"

## Download Audio Only
Best audio as MP3:
yt-dlp -x --audio-format mp3 "VIDEO_URL"

Best audio as M4A:
yt-dlp -x --audio-format m4a "VIDEO_URL"

Best quality audio (original format):
yt-dlp -f "bestaudio" "VIDEO_URL"

With metadata:
yt-dlp -x --audio-format mp3 --embed-thumbnail --add-metadata "VIDEO_URL"

## List Available Formats
yt-dlp -F "VIDEO_URL"

Download specific format by ID:
yt-dlp -f 137+140 "VIDEO_URL"

# Custom template
yt-dlp -o "%(title)s.%(ext)s" "VIDEO_URL"

# With channel name
yt-dlp -o "%(channel)s - %(title)s.%(ext)s" "VIDEO_URL"

# With date
yt-dlp -o "%(upload_date)s - %(title)s.%(ext)s" "VIDEO_URL"

# To specific folder
yt-dlp -o "~/Videos/%(title)s.%(ext)s" "VIDEO_URL"

## Download Playlist
Entire playlist:
yt-dlp "PLAYLIST_URL"

With numbering:
yt-dlp -o "%(playlist_index)s - %(title)s.%(ext)s" "PLAYLIST_URL"

Specific range:

# Videos 1-10
yt-dlp --playlist-start 1 --playlist-end 10 "PLAYLIST_URL"

# Only first 5
yt-dlp -I 1:5 "PLAYLIST_URL"

## Download Channel
Recent videos from channel:
yt-dlp -I 1:10 "CHANNEL_URL"

All videos (careful - can be large!):
yt-dlp "CHANNEL_URL/videos"

## Download with Subtitles
Embed subtitles:
yt-dlp --write-sub --embed-subs "VIDEO_URL"

Auto-generated subtitles:
yt-dlp --write-auto-sub --embed-subs --sub-lang en "VIDEO_URL"

## Thumbnail & Metadata
Embed thumbnail:
yt-dlp --embed-thumbnail "VIDEO_URL"

Full metadata:
yt-dlp --embed-thumbnail --add-metadata --embed-chapters "VIDEO_URL"

## Speed & Resume
Limit download speed:
yt-dlp -r 1M "VIDEO_URL" # 1 MB/s limit

Resume interrupted download:
yt-dlp -c "VIDEO_URL"

## Archive (Skip Downloaded)
yt-dlp --download-archive downloaded.txt "PLAYLIST_URL"

## Common Format Codes
- `best`: Best single file
- `bestvideo+bestaudio`: Best quality (requires ffmpeg)
- `bestvideo[height<=1080]`: Max 1080p
- `bestaudio`: Best audio only
- `mp4`: Prefer MP4 container

## Output Template Variables
- `%(title)s`: Video title, `%(id)s`: Video ID, `%(channel)s`: Channel name
- `%(upload_date)s`: Upload date (YYYYMMDD)
- `%(duration)s`: Duration in seconds
- `%(playlist_index)s`: Index in playlist
- `%(ext)s`: File extension

## Notes
- Respect copyright and terms of service
- Some videos may be geo-restricted
- Age-restricted videos may need cookies
- Use `--cookies-from-browser chrome` for authenticated content
- ffmpeg required for merging separate video/audio streams
- Update regularly: `pip install -U yt-dlp`