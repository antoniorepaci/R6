import os
from utils.ffmpeg import get_ffmpeg_path


def test_get_ffmpeg_path_exists():
    path = get_ffmpeg_path()
    assert isinstance(path, str)
    # Il progetto contiene ffmpeg/ffmpeg.exe nella root del repo
    assert os.path.exists(path), f"ffmpeg non trovato in: {path}"

