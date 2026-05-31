import os
from utils.ffmpeg import get_ffmpeg_path


def test_get_ffmpeg_path_exists():
    path = get_ffmpeg_path()
    assert isinstance(path, str)
    # The project contains ffmpeg/ffmpeg.exe in the repository root directory
    assert os.path.exists(path), f"ffmpeg not found at: {path}"
