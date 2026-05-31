"""Entrypoint minimale del progetto.

Questo file re-esporta alcune utility usate dagli script di test (es. `smoke_test.py`)
e avvia l'app quando eseguito come script.
"""

from utils.ffmpeg import get_ffmpeg_path
from ytdl_opts import costruisci_ydl_opts

# Manteniamo l'app separata in `app.py`.
from app import App


__all__ = ["get_ffmpeg_path", "costruisci_ydl_opts", "App"]


if __name__ == "__main__":
    app = App()
    app.mainloop()
