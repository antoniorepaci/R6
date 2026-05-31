import yt_dlp


class DummyYDL:
    def __init__(self, opts):
        self.opts = opts or {}
        self._extracted = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def extract_info(self, url, download=False):
        self._extracted = True
        # Simulate a simple video download info retrieval
        return {"title": "dummy", "_type": "video"}

    def download(self, urls):
        # Simulate invocation of progress hooks (if present)
        for hook in self.opts.get("progress_hooks", []):
            hook({"status": "downloading", "downloaded_bytes": 50, "total_bytes": 100, "_speed_str": "1.0", "_eta_str": "1"})
            hook({"status": "finished"})
        return None


def test_mock_yt_dlp(monkeypatch):
    calls = []

    def ph(d):
        calls.append(d.get("status"))

    # Replace YoutubeDL class with our Dummy mock class
    monkeypatch.setattr(yt_dlp, "YoutubeDL", DummyYDL)

    ydl_opts = {"progress_hooks": [ph]}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info("http://example.com", download=False)
        assert info["title"] == "dummy"
        ydl.download(["http://example.com"])

    assert "downloading" in calls and "finished" in calls
