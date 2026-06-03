from typing import Optional
import os

from utils.ffmpeg import get_ffmpeg_path


def build_ydl_opts(file_format: str, output_dir: str, progress_hook, logger=None, allow_playlist: bool = False, playlist_items: Optional[str] = None) -> dict:
    """Builds the dictionary of options for yt_dlp based on the chosen format.
    If `allow_playlist` is True, includes %(playlist_index) in outtmpl and permits playlist downloading.
    If `playlist_items` is provided (e.g. "1-10"), it limits the downloading range."""
    ffmpeg_path = get_ffmpeg_path()
    if allow_playlist:
        outtmpl = os.path.join(output_dir, "%(playlist_index)03d - %(title)s.%(ext)s")
    else:
        outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")

    opts = {
        "ffmpeg_location": ffmpeg_path,
        "outtmpl": outtmpl,
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
    }

    # if playlist is not explicitly allowed, force noplaylist
    if not allow_playlist:
        opts["noplaylist"] = True
    elif playlist_items:
        opts["playlist_items"] = playlist_items

    if logger is not None:
        opts["logger"] = logger

    # --- Audio Formats ---
    if file_format == "mp3 320kbps":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"}]
    elif file_format == "mp3 192kbps":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
    elif file_format == "mp3 128kbps":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "128"}]
    elif file_format == "m4a":
        opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a", "preferredquality": "0"}]
    elif file_format == "wav":
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "wav", "preferredquality": "0"}]

    # --- Video Formats ---
    elif file_format == "mp4 1080p":
        opts["format"] = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best"
        opts["merge_output_format"] = "mp4"
    elif file_format == "mp4 720p":
        opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best"
        opts["merge_output_format"] = "mp4"
    elif file_format == "mp4 480p":
        opts["format"] = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best"
        opts["merge_output_format"] = "mp4"
    elif file_format == "mp4 360p":
        opts["format"] = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=360]+bestaudio/best"
        opts["merge_output_format"] = "mp4"
    elif file_format == "webm 1080p":
        opts["format"] = "bestvideo[height<=1080][ext=webm]+bestaudio[ext=webm]/bestvideo[height<=1080]+bestaudio/best"
        opts["merge_output_format"] = "webm"
    elif file_format == "webm 720p":
        opts["format"] = "bestvideo[height<=720][ext=webm]+bestaudio[ext=webm]/bestvideo[height<=720]+bestaudio/best"
        opts["merge_output_format"] = "webm"

    return opts
