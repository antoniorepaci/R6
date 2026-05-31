from typing import Optional
import os

from utils.ffmpeg import get_ffmpeg_path


def costruisci_ydl_opts(formato: str, cartella_output: str, progress_hook, logger=None, allow_playlist: bool = False, playlist_items: Optional[str] = None) -> dict:
    """Costruisce il dizionario di opzioni per yt_dlp in base al formato scelto.
    Se `allow_playlist` è True include %(playlist_index) nell'outtmpl e permette il download della playlist.
    Se `playlist_items` è fornito (es. "1-10"), lo usa per limitare gli elementi."""
    ffmpeg_path = get_ffmpeg_path()
    if allow_playlist:
        outtmpl = os.path.join(cartella_output, "%(playlist_index)03d - %(title)s.%(ext)s")
    else:
        outtmpl = os.path.join(cartella_output, "%(title)s.%(ext)s")

    opts = {
        "ffmpeg_location": ffmpeg_path,
        "outtmpl": outtmpl,
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
    }
    # se non permettiamo playlist, forziamo noplaylist
    if not allow_playlist:
        opts["noplaylist"] = True
    elif playlist_items:
        opts["playlist_items"] = playlist_items

    if logger is not None:
        opts["logger"] = logger

    # --- Formati audio ---
    if formato == "mp3 320kbps":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"}]
    elif formato == "mp3 192kbps":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
    elif formato == "mp3 128kbps":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "128"}]
    elif formato == "m4a":
        opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a", "preferredquality": "0"}]
    elif formato == "wav":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "0"}]

    # --- Formati video ---
    elif formato == "mp4 1080p":
        opts["format"] = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best"
        opts["merge_output_format"] = "mp4"
    elif formato == "mp4 720p":
        opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best"
        opts["merge_output_format"] = "mp4"
    elif formato == "mp4 480p":
        opts["format"] = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best"
        opts["merge_output_format"] = "mp4"
    elif formato == "mp4 360p":
        opts["format"] = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best"
        opts["merge_output_format"] = "mp4"
    elif formato == "webm 1080p":
        opts["format"] = "bestvideo[height<=1080][ext=webm]+bestaudio[ext=webm]/bestvideo[height<=1080]+bestaudio/best"
        opts["merge_output_format"] = "webm"
    elif formato == "webm 720p":
        opts["format"] = "bestvideo[height<=720][ext=webm]+bestaudio[ext=webm]/bestvideo[height<=720]+bestaudio/best"
        opts["merge_output_format"] = "webm"

    return opts

