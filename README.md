# YouTube Music Downloader

A Python desktop app (customtkinter) to download audio and video from YouTube using yt-dlp and ffmpeg.

## Requirements
- Python 3.10+
- ffmpeg included in `ffmpeg/ffmpeg.exe`

## Installation
```powershell
python -m pip install -r requirements.txt
```

## Run the app
```powershell
python main.py
```

## Smoke test (without opening the GUI)
```powershell
python smoke_test.py
```

## Supported formats
Audio:
- mp3 320kbps, mp3 192kbps, mp3 128kbps, m4a, wav

Video:
- mp4 1080p, mp4 720p, mp4 480p, mp4 360p, webm 1080p, webm 720p

## Build with PyInstaller
```powershell
pyinstaller --onedir --windowed --add-binary "ffmpeg/ffmpeg.exe;ffmpeg" --name "YTMusicDownloader" main.py
```
