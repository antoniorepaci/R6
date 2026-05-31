# YouTube Music Downloader

App desktop in Python (customtkinter) per scaricare audio e video da YouTube usando yt-dlp e ffmpeg.

## Requisiti
- Python 3.10+
- ffmpeg incluso in `ffmpeg/ffmpeg.exe`

## Installazione
```powershell
python -m pip install -r requirements.txt
```

## Avvio app
```powershell
python main.py
```

## Smoke test (senza aprire la GUI)
```powershell
python smoke_test.py
```

## Formati supportati
Audio:
- mp3 320kbps, mp3 192kbps, mp3 128kbps, m4a, wav

Video:
- mp4 1080p, mp4 720p, mp4 480p, mp4 360p, webm 1080p, webm 720p

## Build con PyInstaller
```powershell
pyinstaller --onedir --windowed --add-binary "ffmpeg/ffmpeg.exe;ffmpeg" --name "YTMusicDownloader" main.py
```

