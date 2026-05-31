import os

import main


def run_smoke_test() -> int:
    ffmpeg_path = main.get_ffmpeg_path()
    exists = os.path.exists(ffmpeg_path)
    print(f"ffmpeg_path={ffmpeg_path}")
    print(f"ffmpeg_exists={exists}")

    # Verifica creazione opzioni per un formato audio e uno video
    opts_audio = main.costruisci_ydl_opts("mp3 128kbps", os.getcwd(), lambda _d: None, logger=None, allow_playlist=False)
    opts_video = main.costruisci_ydl_opts("mp4 720p", os.getcwd(), lambda _d: None, logger=None, allow_playlist=True)

    print(f"opts_audio_ok={'format' in opts_audio}")
    print(f"opts_video_ok={'format' in opts_video}")

    return 0


if __name__ == "__main__":
    raise SystemExit(run_smoke_test())
