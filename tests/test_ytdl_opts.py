import os
from ytdl_opts import costruisci_ydl_opts


class DummyProgressHook:
    def __call__(self, d):
        pass


def test_costruisci_ydl_opts_audio():
    # crea opzioni per mp3 128kbps
    outdir = os.getcwd()
    opts = costruisci_ydl_opts("mp3 128kbps", outdir, DummyProgressHook(), logger=None, allow_playlist=False)
    assert isinstance(opts, dict)
    assert "ffmpeg_location" in opts
    assert "outtmpl" in opts
    assert "progress_hooks" in opts
    # controlla che il postprocessor sia impostato per mp3 128kbps
    assert "postprocessors" in opts
    pp = opts["postprocessors"]
    assert isinstance(pp, list) and pp, "postprocessors mancante"
    assert pp[0]["preferredcodec"] == "mp3"
    assert str(pp[0]["preferredquality"]).startswith("128")


def test_costruisci_ydl_opts_video_and_playlist():
    outdir = os.getcwd()
    opts = costruisci_ydl_opts("mp4 720p", outdir, DummyProgressHook(), logger=None, allow_playlist=True, playlist_items="1:5")
    assert isinstance(opts, dict)
    # per i video ci deve essere merge_output_format
    assert opts.get("merge_output_format") == "mp4"
    # quando allow_playlist è True l'outtmpl deve contenere playlist_index
    assert "%(playlist_index)" in opts.get("outtmpl", "")
    # playlist_items deve essere passato se fornito
    assert "playlist_items" in opts and opts["playlist_items"] == "1:5"


def test_costruisci_ydl_opts_unknown_format():
    """Caso negativo: formato sconosciuto -> nessuna chiave 'format' o 'postprocessors' o 'merge_output_format'"""
    outdir = os.getcwd()
    opts = costruisci_ydl_opts("formato_non_valido", outdir, DummyProgressHook(), logger=None, allow_playlist=False)
    assert isinstance(opts, dict)
    assert "format" not in opts
    assert "postprocessors" not in opts
    assert "merge_output_format" not in opts

