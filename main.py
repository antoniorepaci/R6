"""Minimal entry point of the project.

This file re-exports utility functions used by test scripts (e.g. `smoke_test.py`)
and executes the app when run as a script.
"""

from utils.ffmpeg import get_ffmpeg_path
from utils.path import resource_path
from ytdl_opts import build_ydl_opts

# Keep the main application UI separated in `app.py`
from app import App


# Keep build_ydl_opts aliased under the old name if backward compatibility is needed,
# but also define it clearly in English as requested.
costruisci_ydl_opts = build_ydl_opts


__all__ = ["get_ffmpeg_path", "build_ydl_opts", "costruisci_ydl_opts", "App"]


if __name__ == "__main__":
    app = App()
    try:
        app.iconbitmap(resource_path("img/icon.ico"))
    except Exception:
        pass
    app.mainloop()
