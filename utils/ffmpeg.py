import os
import sys


def get_ffmpeg_path() -> str:
    """Restituisce il percorso assoluto di ffmpeg.exe,
    compatibile sia con esecuzione normale che bundle PyInstaller."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "..", "ffmpeg", "ffmpeg.exe")

