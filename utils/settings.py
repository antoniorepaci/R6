"""
Persistent user settings stored in settings.json inside %PROGRAMDATA%\\R6\\
(typically C:\\ProgramData\\R6\\).

This folder is shared between all users on the machine and does not require
administrator privileges to write.
The directory is created automatically if it does not exist.
"""

import json
import os
import sys

DEFAULTS: dict = {
    "language": "English",
    "theme": "dark",
    "output_folder": "",
    "format": "mp3 320kbps",
    "allow_playlist": False,
    "playlist_threshold": 20,
    "playlist_range": "",
}


SETTINGS_DIR = os.path.join(os.environ.get("PROGRAMDATA", r"C:\ProgramData"), "R6")


def _settings_path() -> str:
    """Returns the absolute path to settings.json inside %PROGRAMDATA%\\R6\\."""
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    return os.path.join(SETTINGS_DIR, "settings.json")


def load() -> dict:
    """Load settings from disk, merging with defaults for any missing keys."""
    path = _settings_path()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {**DEFAULTS, **data}
        except Exception:
            pass
    return dict(DEFAULTS)


def save(settings: dict) -> None:
    """Persist settings dict to disk as formatted JSON."""
    path = _settings_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

