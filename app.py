import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter
import yt_dlp

from utils.ffmpeg import get_ffmpeg_path
from utils.path import resource_path
from ytdl_opts import build_ydl_opts
from ui.modal import show_copyright_modal
from utils.localization import TRANSLATIONS

# Default appearance mode: dark
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# ---------------------------------------------------------------------------
# Available format options
# ---------------------------------------------------------------------------
AUDIO_FORMATS = [
    "mp3 320kbps",
    "mp3 192kbps",
    "mp3 128kbps",
    "m4a",
    "wav",
]

VIDEO_FORMATS = [
    "mp4 1080p",
    "mp4 720p",
    "mp4 480p",
    "mp4 360p",
    "webm 1080p",
    "webm 720p",
]

ALL_FORMATS = AUDIO_FORMATS + VIDEO_FORMATS


class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        # Hide the main window until the copyright warning is accepted
        self.withdraw()

        # Main window configuration
        self.title("R6 Downloader")
        try:
            self.iconbitmap(resource_path("img/icon.ico"))
        except Exception:
            pass
        self.minsize(640, 800)
        self.resizable(True, True)

        # Download active state variable
        self._download_active = False

        # Variables for playlist options
        self._var_allow_playlist = tk.BooleanVar(value=False)
        self._var_playlist_threshold = tk.IntVar(value=20)
        self._var_playlist_range = tk.StringVar(value="")

        # Playlist progression state
        self._playlist_total = None
        self._playlist_done = 0
        self._playlist_confirm_event = None
        self._playlist_confirm_result = True
        self._playlist_range_start = None
        self._playlist_range_end = None

        # Build user interface
        self._build_ui()

        # Setup default language to English and apply translations
        self._current_lang = "en"
        self._var_lang = customtkinter.StringVar(value="English")
        self._update_locale()

        # Show copyright modal window
        show_copyright_modal(self, lang=self._current_lang)

    # -----------------------------------------------------------------------
    # UI Building
    # -----------------------------------------------------------------------
    def _build_ui(self):
        padding = {"padx": 20, "pady": 8}

        # Grid configuration: Title(col 0) expands, Lang(col 1) and Theme(col 2) are fixed
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)

        # Title
        self._lbl_title = customtkinter.CTkLabel(
            self,
            text="YouTube Music & Video Downloader",
            font=customtkinter.CTkFont(size=18, weight="bold"),
        )
        self._lbl_title.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # Language dropdown selector
        self._menu_lang = customtkinter.CTkOptionMenu(
            self,
            values=["English", "Italiano"],
            width=100,
            height=32,
            command=self._on_language_changed,
        )
        self._menu_lang.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=(20, 10))

        # Day/Night theme switcher button
        self._btn_theme = customtkinter.CTkButton(
            self,
            text="Light",
            width=80,
            height=32,
            command=self._toggle_theme,
        )
        self._btn_theme.grid(row=0, column=2, sticky="e", padx=(0, 20), pady=(20, 10))

        # Row 1-2: URL
        self._lbl_url = customtkinter.CTkLabel(self, text="YouTube URL:", anchor="w")
        self._lbl_url.grid(row=1, column=0, columnspan=3, sticky="ew", **padding)
        self._entry_url = customtkinter.CTkEntry(self, placeholder_text="Paste YouTube URL...", height=38)
        self._entry_url.grid(row=2, column=0, columnspan=3, sticky="ew", **padding)

        # Row 3-4: Format
        self._lbl_format = customtkinter.CTkLabel(self, text="Format:", anchor="w")
        self._lbl_format.grid(row=3, column=0, columnspan=3, sticky="ew", **padding)
        self._var_format = customtkinter.StringVar(value=ALL_FORMATS[0])
        self._menu_format = customtkinter.CTkOptionMenu(self, values=ALL_FORMATS, variable=self._var_format, height=38)
        self._menu_format.grid(row=4, column=0, columnspan=3, sticky="ew", **padding)

        # Row 5: Playlist Checkbox
        self._chk_playlist = customtkinter.CTkCheckBox(self, text="Download playlist (if present)", variable=self._var_allow_playlist)
        self._chk_playlist.grid(row=5, column=0, columnspan=3, sticky="w", padx=20, pady=(10, 5))

        # Row 6: Playlist Advanced Options Frame (Threshold & Range)
        self._frame_playlist_opts = customtkinter.CTkFrame(self, fg_color="transparent")
        self._frame_playlist_opts.grid(row=6, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 10))
        self._frame_playlist_opts.grid_columnconfigure(1, weight=1)
        self._frame_playlist_opts.grid_columnconfigure(3, weight=1)

        self._lbl_threshold = customtkinter.CTkLabel(self._frame_playlist_opts, text="Confirm if >", font=("Arial", 11))
        self._lbl_threshold.grid(row=0, column=0, sticky="w", padx=(0, 5))
        self._entry_threshold = customtkinter.CTkEntry(self._frame_playlist_opts, textvariable=self._var_playlist_threshold, width=45, height=28)
        self._entry_threshold.grid(row=0, column=1, sticky="w")

        self._lbl_range = customtkinter.CTkLabel(self._frame_playlist_opts, text="Range (e.g. 1-5)", font=("Arial", 11))
        self._lbl_range.grid(row=0, column=2, sticky="w", padx=(15, 5))
        self._entry_range = customtkinter.CTkEntry(self._frame_playlist_opts, textvariable=self._var_playlist_range, placeholder_text="1-10", width=80, height=28)
        self._entry_range.grid(row=0, column=3, sticky="w")

        # Row 7: Output Folder Label
        self._lbl_output = customtkinter.CTkLabel(self, text="Output folder:", anchor="w")
        self._lbl_output.grid(row=7, column=0, columnspan=3, sticky="ew", **padding)

        # Row 8: Output Folder Entry + Browse Button
        self._frame_output = customtkinter.CTkFrame(self, fg_color="transparent")
        self._frame_output.grid(row=8, column=0, columnspan=3, sticky="ew", **padding)
        self._frame_output.grid_columnconfigure(0, weight=1)
        self._entry_output = customtkinter.CTkEntry(self._frame_output, placeholder_text="No folder selected...", state="disabled", height=38)
        self._entry_output.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._btn_browse = customtkinter.CTkButton(self._frame_output, text="Browse", width=90, height=38, command=self._browse_folder)
        self._btn_browse.grid(row=0, column=1)

        # Row 9: Download Button
        self._btn_download = customtkinter.CTkButton(self, text="Download", height=44, font=customtkinter.CTkFont(size=15, weight="bold"), command=self._start_download)
        self._btn_download.grid(row=9, column=0, columnspan=3, sticky="ew", padx=20, pady=(15, 5))

        # Row 10: File ProgressBar
        self._progressbar = customtkinter.CTkProgressBar(self, height=12)
        self._progressbar.set(0)
        self._progressbar.grid(row=10, column=0, columnspan=3, sticky="ew", padx=20, pady=(5, 2))

        # Row 11: Playlist ProgressBar
        self._progress_playlist = customtkinter.CTkProgressBar(self, height=8)
        self._progress_playlist.set(0)
        self._progress_playlist.grid(row=11, column=0, columnspan=3, sticky="ew", padx=20, pady=(2, 5))

        # Row 12: Status Label
        self._lbl_status = customtkinter.CTkLabel(self, text="Waiting...", anchor="w", font=customtkinter.CTkFont(size=12))
        self._lbl_status.grid(row=12, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 5))

        # Row 13: Log Label and TextBox
        self._lbl_log = customtkinter.CTkLabel(self, text="Log:", anchor="w")
        self._lbl_log.grid(row=13, column=0, columnspan=3, sticky="ew", padx=20, pady=(5, 0))
        self._textbox_log = customtkinter.CTkTextbox(self, height=180, state="disabled")
        self._textbox_log.grid(row=14, column=0, columnspan=3, sticky="nsew", padx=20, pady=(0, 20))
        self.grid_rowconfigure(14, weight=1)

    # -----------------------------------------------------------------------
    # Language Localization Setup
    # -----------------------------------------------------------------------
    def _on_language_changed(self, choice: str):
        """Callback when language option is modified in the dropdown menu."""
        self._var_lang.set(choice)
        self._update_locale()

    def _update_locale(self):
        """Updates all UI widget texts on-the-fly dynamically based on language settings."""
        lang_str = self._var_lang.get()
        self._current_lang = "en" if lang_str == "English" else "it"
        texts = TRANSLATIONS[self._current_lang]

        self._lbl_title.configure(text=texts["title"])
        self._lbl_url.configure(text=texts["lbl_url"])
        self._entry_url.configure(placeholder_text=texts["placeholder_url"])
        self._lbl_format.configure(text=texts["lbl_format"])
        self._chk_playlist.configure(text=texts["chk_playlist"])
        self._lbl_threshold.configure(text=texts["lbl_threshold"])
        self._lbl_range.configure(text=texts["lbl_range"])
        self._entry_range.configure(placeholder_text=texts["placeholder_range"])
        self._lbl_output.configure(text=texts["lbl_output"])
        self._btn_browse.configure(text=texts["btn_browse"])
        self._btn_download.configure(text=texts["btn_download"])
        self._lbl_log.configure(text=texts["log_label"])

        # Update Theme button label based on mode and language
        mode = customtkinter.get_appearance_mode()
        if mode == "Dark":
            self._btn_theme.configure(text=texts["theme_light"])
        else:
            self._btn_theme.configure(text=texts["theme_dark"])

        # Update output placeholder text if empty
        if not self._entry_output.get():
            self._entry_output.configure(state="normal")
            self._entry_output.delete(0, tk.END)
            self._entry_output.configure(placeholder_text=texts["placeholder_output"])
            self._entry_output.configure(state="disabled")

        # Update state label if not actively running
        if not self._download_active:
            self._set_status(texts["lbl_status_waiting"], "default")

    # -----------------------------------------------------------------------
    # Theme toggling
    # -----------------------------------------------------------------------
    def _toggle_theme(self):
        """Alternates between Dark mode and Light mode."""
        current_mode = customtkinter.get_appearance_mode()
        texts = TRANSLATIONS[self._current_lang]
        if current_mode == "Dark":
            customtkinter.set_appearance_mode("light")
            self._btn_theme.configure(text=texts["theme_dark"])
        else:
            customtkinter.set_appearance_mode("dark")
            self._btn_theme.configure(text=texts["theme_light"])

    # -----------------------------------------------------------------------
    # UI Utility Actions
    # -----------------------------------------------------------------------
    def _browse_folder(self):
        """Opens directory selection dialog."""
        texts = TRANSLATIONS[self._current_lang]
        folder = filedialog.askdirectory(title=texts["lbl_output"])
        if folder:
            self._entry_output.configure(state="normal")
            self._entry_output.delete(0, tk.END)
            self._entry_output.insert(0, folder)
            self._entry_output.configure(state="disabled")

    def _parse_range_string(self, range_str: str):
        """Parses range bounds (e.g. '1-10') and returns (start, end) or (None, None)."""
        if not range_str or not range_str.strip():
            return None, None
        try:
            parts = range_str.strip().replace(" ", "").split("-")
            if len(parts) == 2:
                return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            pass
        return None, None

    def _start_download(self):
        """Validates all visual inputs and launches the download on a separate daemon thread."""
        if self._download_active:
            return

        texts = TRANSLATIONS[self._current_lang]
        url = self._entry_url.get().strip()
        folder = self._entry_output.get().strip()
        file_format = self._var_format.get()
        allow_playlist = self._var_allow_playlist.get()
        threshold = self._var_playlist_threshold.get()
        range_str = self._var_playlist_range.get().strip()

        # Input validations
        if not url or ("youtube.com" not in url and "youtu.be" not in url):
            self._set_status(texts["err_invalid_url"], "red")
            return
        if not folder or not os.path.isdir(folder):
            self._set_status(texts["err_invalid_dir"], "red")
            return
        if not os.path.isfile(get_ffmpeg_path()):
            self._set_status(texts["err_missing_ffmpeg"], "red")
            return

        # Start execution
        self._download_active = True
        self._btn_download.configure(state="disabled")
        self._progressbar.set(0)
        self._progress_playlist.set(0)
        self._playlist_total = None
        self._playlist_done = 0
        self._set_status(texts["lbl_status_retrieving"], "default")
        self._log(texts["log_config"].format(playlist=allow_playlist, threshold=threshold, range=range_str))

        thread = threading.Thread(
            target=self._download_thread,
            args=(url, file_format, folder, threshold, range_str),
            daemon=True
        )
        thread.start()

    def _download_thread(self, url: str, file_format: str, folder: str, threshold: int, range_str: str):
        """Background thread executing the core yt-dlp downloader engine."""
        texts = TRANSLATIONS[self._current_lang]
        try:
            playlist_items = None
            if range_str:
                start, end = self._parse_range_string(range_str)
                if start is not None:
                    playlist_items = f"{start}:{end}"

            ydl_opts = build_ydl_opts(
                file_format,
                folder,
                self._progress_hook,
                logger=self._YdlLogger(self),
                allow_playlist=self._var_allow_playlist.get(),
                playlist_items=playlist_items
            )

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # Count items
                count = 1
                if info.get("_type") == "playlist" or "entries" in info:
                    entries = info.get("entries")
                    try:
                        count = len(entries) if entries else (info.get("playlist_count") or 0)
                    except Exception:
                        count = info.get("playlist_count") or 0

                self._playlist_total = count

                # Verify playlist item threshold
                if self._var_allow_playlist.get() and count > threshold:
                    self._playlist_confirm_event = threading.Event()

                    def _ask():
                        self._playlist_confirm_result = messagebox.askyesno(
                            texts["playlist_confirm_title"],
                            texts["playlist_confirm_message"].format(count=count)
                        )
                        self._playlist_confirm_event.set()

                    self.after(0, _ask)
                    self._playlist_confirm_event.wait()
                    if not self._playlist_confirm_result:
                        self.after(0, self._on_download_error, texts["playlist_cancel"])
                        return

                self.after(0, self._log, texts["log_title"].format(title=info.get("title", 'N/A')))
                ydl.download([url])

            self.after(0, self._on_download_completed)

        except Exception as e:
            self.after(0, self._on_download_error, str(e))

    # -----------------------------------------------------------------------
    # Progress hook callback triggered by yt_dlp on download steps
    # -----------------------------------------------------------------------
    def _progress_hook(self, d: dict):
        """Thread-safe update of UI elements and progress status messages."""
        status = d.get("status")
        texts = TRANSLATIONS[self._current_lang]

        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            speed = d.get("_speed_str", "N/A").strip()
            eta = d.get("_eta_str", "N/A").strip()

            file_frac = 0.0
            if total and total > 0:
                file_frac = downloaded / total
                percent = file_frac * 100
                msg = texts["lbl_status_downloading"].format(percent=percent, speed=speed, eta=eta)
                self.after(0, self._progressbar.set, file_frac)
                self.after(0, self._set_status, msg, "default")

            # Overall playlist progression
            playlist_total = getattr(self, "_playlist_total", None) or d.get("info_dict", {}).get("playlist_count")
            current_index = d.get("playlist_index") or d.get("info_dict", {}).get("playlist_index")
            try:
                if playlist_total:
                    idx = int(current_index) if current_index else getattr(self, "_playlist_done", 0)
                    overall = (max(0, idx - 1) + file_frac) / float(playlist_total)
                    self.after(0, self._progress_playlist.set, overall)
            except Exception:
                pass

        elif status == "finished":
            try:
                playlist_total = getattr(self, "_playlist_total", None)
                if playlist_total:
                    self._playlist_done = min(getattr(self, "_playlist_done", 0) + 1, playlist_total)
                    overall = self._playlist_done / float(playlist_total)
                    self.after(0, self._progress_playlist.set, overall)
                    self.after(0, self._log, texts["log_completed"].format(done=self._playlist_done, total=playlist_total))
            except Exception:
                pass

            self.after(0, self._progressbar.set, 1.0)
            self.after(0, self._set_status, texts["lbl_status_processing"], "default")
            self.after(0, self._log, texts["log_finished"])

    # -----------------------------------------------------------------------
    # Download Completed / Error Callbacks
    # -----------------------------------------------------------------------
    def _on_download_completed(self):
        texts = TRANSLATIONS[self._current_lang]
        self._download_active = False
        self._btn_download.configure(state="normal")
        self._progressbar.set(1.0)
        self._progress_playlist.set(1.0)
        self._set_status(texts["lbl_status_completed"], "green")
        self._log(texts["log_success"])
        self._log(texts["log_separator"])

    def _on_download_error(self, message: str):
        texts = TRANSLATIONS[self._current_lang]
        self._download_active = False
        self._btn_download.configure(state="normal")
        self._progressbar.set(0)
        self._progress_playlist.set(0)
        self._set_status(texts["lbl_status_error"].format(msg=message[:80]), "red")
        self._log(texts["log_error"].format(msg=message))
        self._log(texts["log_separator"])

    # -----------------------------------------------------------------------
    # State update and logging utilities
    # -----------------------------------------------------------------------
    def _set_status(self, text: str, color: str = "default"):
        """Thread-safe wrapper to set state text label with its color map."""
        color_map = {
            "green": "#2ecc71",
            "red":   "#e74c3c",
            "default": customtkinter.ThemeManager.theme["CTkLabel"]["text_color"],
        }
        self._lbl_status.configure(text=text, text_color=color_map.get(color, color_map["default"]))

    def _log(self, text: str):
        """Helper to safely append entries in the log GUI textbox widget."""
        self._textbox_log.configure(state="normal")
        self._textbox_log.insert(tk.END, text + "\n")
        self._textbox_log.see(tk.END)
        self._textbox_log.configure(state="disabled")

    class _YdlLogger:
        """Simple silent console mock logger passed to yt-dlp to print to textbox."""
        def __init__(self, app: "App"):
            self._app = app

        def debug(self, msg):
            pass

        def warning(self, msg):
            if msg:
                self._app.after(0, self._app._log, f"WARNING: {msg}")

        def error(self, msg):
            if msg:
                self._app.after(0, self._app._log, f"ERROR: {msg}")
