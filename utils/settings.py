"""
Persistent user settings stored in settings.json next to the executable (or project root).

Uses sys.executable dir when frozen (PyInstaller), otherwise cwd so the file
is always written to a user-writable location, never inside sys._MEIPASS.
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


def _settings_path() -> str:
    """Returns the absolute path to settings.json."""
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller bundle
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath(".")
    return os.path.join(base, "settings.json")


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

