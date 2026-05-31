import os
import sys


def get_ffmpeg_path() -> str:
    """Returns the absolute path of ffmpeg.exe,
    compatible with both standard run and PyInstaller bundle execution."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "..", "ffmpeg", "ffmpeg.exe")
