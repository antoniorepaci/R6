import os
import sys


def get_ffmpeg_path() -> str:
    """Returns the absolute path of ffmpeg.exe,
    compatible with both standard run and PyInstaller bundle execution."""
    if getattr(sys, "frozen", False):
        # PyInstaller extracts files into sys._MEIPASS; ffmpeg.exe lives at _MEIPASS/ffmpeg/ffmpeg.exe
        base: str = str(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        # In normal execution __file__ is utils/ffmpeg.py, so go up one level to the project root
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "ffmpeg", "ffmpeg.exe")
