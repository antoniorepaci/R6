import os
from ytdl_opts import build_ydl_opts


class DummyProgressHook:
    def __call__(self, d):
        pass


def test_build_ydl_opts_audio():
    # Build options for mp3 128kbps
    out_dir = os.getcwd()
    opts = build_ydl_opts("mp3 128kbps", out_dir, DummyProgressHook(), logger=None, allow_playlist=False)
    assert isinstance(opts, dict)
    assert "ffmpeg_location" in opts
    assert "outtmpl" in opts
    assert "progress_hooks" in opts
    # Check that postprocessor is set for mp3 128kbps
    assert "postprocessors" in opts
    pp = opts["postprocessors"]
    assert isinstance(pp, list) and pp, "Missing postprocessors"
    assert pp[0]["preferredcodec"] == "mp3"
    assert str(pp[0]["preferredquality"]).startswith("128")


def test_build_ydl_opts_video_and_playlist():
    out_dir = os.getcwd()
    opts = build_ydl_opts("mp4 720p", out_dir, DummyProgressHook(), logger=None, allow_playlist=True, playlist_items="1:5")
    assert isinstance(opts, dict)
    # Video downloads should have merge_output_format set
    assert opts.get("merge_output_format") == "mp4"
    # When allow_playlist is True, outtmpl must support playlist_index
    assert "%(playlist_index)" in opts.get("outtmpl", "")
    # playlist_items must be correctly mapped
    assert "playlist_items" in opts and opts["playlist_items"] == "1:5"


def test_build_ydl_opts_unknown_format():
    """Negative case: unknown format -> should not contain format, postprocessors, or merge_output_format keys."""
    out_dir = os.getcwd()
    opts = build_ydl_opts("invalid_format_name", out_dir, DummyProgressHook(), logger=None, allow_playlist=False)
    assert isinstance(opts, dict)
    assert "format" not in opts
    assert "postprocessors" not in opts
    assert "merge_output_format" not in opts
