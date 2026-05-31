import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter
import yt_dlp

from utils.ffmpeg import get_ffmpeg_path
from ytdl_opts import costruisci_ydl_opts
from ui.modal import show_copyright_modal

# Tema di default: dark
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# ---------------------------------------------------------------------------
# Opzioni di formato disponibili
# ---------------------------------------------------------------------------
FORMATI_AUDIO = [
    "mp3 320kbps",
    "mp3 192kbps",
    "mp3 128kbps",
    "m4a",
    "wav",
]

FORMATI_VIDEO = [
    "mp4 1080p",
    "mp4 720p",
    "mp4 480p",
    "mp4 360p",
    "webm 1080p",
    "webm 720p",
]

TUTTI_I_FORMATI = FORMATI_AUDIO + FORMATI_VIDEO


class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

        # Nascondi la finestra principale finché non viene accettato l'avviso
        self.withdraw()

        # Configurazione finestra principale
        self.title("YouTube Music & Video Downloader")
        self.minsize(640, 800)
        self.resizable(True, True)
        self.grid_columnconfigure(0, weight=1)

        # Variabile di stato per il download in corso
        self._download_attivo = False

        # Variabile per scelta playlist
        self._var_allow_playlist = tk.BooleanVar(value=False)
        self._var_playlist_threshold = tk.IntVar(value=20)
        self._var_playlist_range = tk.StringVar(value="")

        # Stato playlist (usato per progressione)
        self._playlist_total = None
        self._playlist_done = 0
        self._playlist_confirm_event = None
        self._playlist_confirm_result = True
        self._playlist_range_start = None
        self._playlist_range_end = None

        # Costruzione dell'interfaccia
        self._build_ui()

        # Mostra la finestra modale di benvenuto/copyright
        show_copyright_modal(self)

    # -----------------------------------------------------------------------
    # Costruzione UI
    # -----------------------------------------------------------------------
    def _build_ui(self):
        padding = {"padx": 20, "pady": 8}

        # Abilita due colonne: colonna 0 si espande, colonna 1 fissa per il bottone tema
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Titolo
        self._lbl_titolo = customtkinter.CTkLabel(
            self,
            text="YouTube Music & Video Downloader",
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        self._lbl_titolo.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        # Bottone switch tema giorno/notte
        self._btn_tema = customtkinter.CTkButton(
            self,
            text="Giorno",
            width=80,
            height=32,
            command=self._toggle_tema,
        )
        self._btn_tema.grid(row=0, column=1, sticky="e", padx=(0, 20), pady=(20, 10))

        # Row 1-2: URL
        self._lbl_url = customtkinter.CTkLabel(self, text="URL YouTube:", anchor="w")
        self._lbl_url.grid(row=1, column=0, columnspan=2, sticky="ew", **padding)
        self._entry_url = customtkinter.CTkEntry(self, placeholder_text="Incolla URL YouTube...", height=38)
        self._entry_url.grid(row=2, column=0, columnspan=2, sticky="ew", **padding)

        # Row 3-4: Formato
        self._lbl_formato = customtkinter.CTkLabel(self, text="Formato:", anchor="w")
        self._lbl_formato.grid(row=3, column=0, columnspan=2, sticky="ew", **padding)
        self._var_formato = customtkinter.StringVar(value=TUTTI_I_FORMATI[0])
        self._menu_formato = customtkinter.CTkOptionMenu(self, values=TUTTI_I_FORMATI, variable=self._var_formato, height=38)
        self._menu_formato.grid(row=4, column=0, columnspan=2, sticky="ew", **padding)

        # Row 5: Checkbox Playlist
        self._chk_playlist = customtkinter.CTkCheckBox(self, text="Scarica playlist (se presente)", variable=self._var_allow_playlist)
        self._chk_playlist.grid(row=5, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 5))

        # Row 6: Frame Opzioni Avanzate Playlist (Threshold & Range)
        self._frame_playlist_opts = customtkinter.CTkFrame(self, fg_color="transparent")
        self._frame_playlist_opts.grid(row=6, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))
        self._frame_playlist_opts.grid_columnconfigure(1, weight=1)
        self._frame_playlist_opts.grid_columnconfigure(3, weight=1)

        self._lbl_threshold = customtkinter.CTkLabel(self._frame_playlist_opts, text="Conf. se >", font=("Arial", 11))
        self._lbl_threshold.grid(row=0, column=0, sticky="w", padx=(0, 5))
        self._spin_threshold = customtkinter.CTkEntry(self._frame_playlist_opts, textvariable=self._var_playlist_threshold, width=45, height=28)
        self._spin_threshold.grid(row=0, column=1, sticky="w")

        self._lbl_range = customtkinter.CTkLabel(self._frame_playlist_opts, text="Range (es. 1-5)", font=("Arial", 11))
        self._lbl_range.grid(row=0, column=2, sticky="w", padx=(15, 5))
        self._entry_range = customtkinter.CTkEntry(self._frame_playlist_opts, textvariable=self._var_playlist_range, placeholder_text="1-10", width=80, height=28)
        self._entry_range.grid(row=0, column=3, sticky="w")

        # Row 7: Cartella Output Label
        self._lbl_output = customtkinter.CTkLabel(self, text="Cartella di output:", anchor="w")
        self._lbl_output.grid(row=7, column=0, columnspan=2, sticky="ew", **padding)

        # Row 8: Cartella Output Entry + Button
        self._frame_output = customtkinter.CTkFrame(self, fg_color="transparent")
        self._frame_output.grid(row=8, column=0, columnspan=2, sticky="ew", **padding)
        self._frame_output.grid_columnconfigure(0, weight=1)
        self._entry_output = customtkinter.CTkEntry(self._frame_output, placeholder_text="Nessuna cartella selezionata...", state="disabled", height=38)
        self._entry_output.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._btn_sfoglia = customtkinter.CTkButton(self._frame_output, text="Sfoglia", width=90, height=38, command=self._sfoglia_cartella)
        self._btn_sfoglia.grid(row=0, column=1)

        # Row 9: Bottone Scarica
        self._btn_scarica = customtkinter.CTkButton(self, text="Scarica", height=44, font=customtkinter.CTkFont(size=15, weight="bold"), command=self._avvia_download)
        self._btn_scarica.grid(row=9, column=0, columnspan=2, sticky="ew", padx=20, pady=(15, 5))

        # Row 10: ProgressBar File
        self._progressbar = customtkinter.CTkProgressBar(self, height=12)
        self._progressbar.set(0)
        self._progressbar.grid(row=10, column=0, columnspan=2, sticky="ew", padx=20, pady=(5, 2))

        # Row 11: ProgressBar Playlist
        self._progress_playlist = customtkinter.CTkProgressBar(self, height=8)
        self._progress_playlist.set(0)
        self._progress_playlist.grid(row=11, column=0, columnspan=2, sticky="ew", padx=20, pady=(2, 5))

        # Row 12: Label Stato
        self._lbl_stato = customtkinter.CTkLabel(self, text="In attesa...", anchor="w", font=customtkinter.CTkFont(size=12))
        self._lbl_stato.grid(row=12, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 5))

        # Row 13: Log
        self._lbl_log = customtkinter.CTkLabel(self, text="Log:", anchor="w")
        self._lbl_log.grid(row=13, column=0, columnspan=2, sticky="ew", padx=20, pady=(5, 0))
        self._textbox_log = customtkinter.CTkTextbox(self, height=180, state="disabled")
        self._textbox_log.grid(row=14, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 20))
        self.grid_rowconfigure(14, weight=1)

    # -----------------------------------------------------------------------
    # Toggle tema giorno / notte
    # -----------------------------------------------------------------------
    def _toggle_tema(self):
        """Alterna tra dark mode e light mode."""
        modo_attuale = customtkinter.get_appearance_mode()
        if modo_attuale == "Dark":
            customtkinter.set_appearance_mode("light")
            self._btn_tema.configure(text="Notte")
        else:
            customtkinter.set_appearance_mode("dark")
            self._btn_tema.configure(text="Giorno")

    # -----------------------------------------------------------------------
    # Azioni UI Utility
    # -----------------------------------------------------------------------
    def _sfoglia_cartella(self):
        """Apre il dialogo di selezione cartella."""
        cartella = filedialog.askdirectory(title="Seleziona cartella di output")
        if cartella:
            self._entry_output.configure(state="normal")
            self._entry_output.delete(0, tk.END)
            self._entry_output.insert(0, cartella)
            self._entry_output.configure(state="disabled")

    def _parse_range_string(self, range_str: str):
        """Parsa una stringa di range (es. '1-10') e ritorna (start, end) o (None, None)."""
        if not range_str or not range_str.strip():
            return None, None
        try:
            parts = range_str.strip().replace(" ", "").split("-")
            if len(parts) == 2:
                return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            pass
        return None, None

    def _avvia_download(self):
        """Valida gli input e avvia il download in un thread separato."""
        if self._download_attivo: return

        url = self._entry_url.get().strip()
        cartella = self._entry_output.get().strip()
        formato = self._var_formato.get()
        allow_playlist = self._var_allow_playlist.get()
        threshold = self._var_playlist_threshold.get()
        range_str = self._var_playlist_range.get().strip()

        # Validazione
        if not url or ("youtube.com" not in url and "youtu.be" not in url):
            self._imposta_stato("[!] Inserisci un URL YouTube valido.", "red"); return
        if not cartella or not os.path.isdir(cartella):
            self._imposta_stato("[!] Seleziona una cartella di output valida.", "red"); return
        if not os.path.isfile(get_ffmpeg_path()):
            self._imposta_stato("[!] ffmpeg.exe mancante in ./ffmpeg.", "red"); return

        # Avvio
        self._download_attivo = True
        self._btn_scarica.configure(state="disabled")
        self._progressbar.set(0)
        self._progress_playlist.set(0)
        self._playlist_total = None
        self._playlist_done = 0
        self._imposta_stato("Recupero informazioni...", "default")
        self._log(f"Config: Playlist={allow_playlist}, Threshold={threshold}, Range='{range_str}'")

        thread = threading.Thread(target=self._thread_download, args=(url, formato, cartella, threshold, range_str), daemon=True)
        thread.start()

    def _thread_download(self, url: str, formato: str, cartella: str, threshold: int, range_str: str):
        """Esegue il download nel thread separato."""
        try:
            playlist_items = None
            if range_str:
                start, end = self._parse_range_string(range_str)
                if start is not None: playlist_items = f"{start}:{end}"

            ydl_opts = costruisci_ydl_opts(formato, cartella, self._progress_hook, logger=self._YdlLogger(self), allow_playlist=self._var_allow_playlist.get(), playlist_items=playlist_items)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                # Calcolo entries
                count = 1
                if info.get("_type") == "playlist" or "entries" in info:
                    entries = info.get("entries")
                    try: count = len(entries) if entries else (info.get("playlist_count") or 0)
                    except: count = info.get("playlist_count") or 0

                self._playlist_total = count

                # Check threshold
                if self._var_allow_playlist.get() and count > threshold:
                    self._playlist_confirm_event = threading.Event()
                    def _ask():
                        self._playlist_confirm_result = messagebox.askyesno("Conferma", f"Playlist di {count} elementi. Continuare?")
                        self._playlist_confirm_event.set()
                    self.after(0, _ask)
                    self._playlist_confirm_event.wait()
                    if not self._playlist_confirm_result:
                        self.after(0, self._on_download_errore, "Annullato."); return

                self.after(0, self._log, f"Titolo: {info.get('title', 'N/A')}")
                ydl.download([url])

            self.after(0, self._on_download_completato)

        except Exception as e:
            self.after(0, self._on_download_errore, str(e))

    # -----------------------------------------------------------------------
    # Hook di progresso (chiamato da yt_dlp nel thread di download)
    # -----------------------------------------------------------------------
    def _progress_hook(self, d: dict):
        """Aggiorna la progress bar e la label di stato in modo thread-safe."""
        stato = d.get("status")

        if stato == "downloading":
            scaricati = d.get("downloaded_bytes", 0)
            totali = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            velocita = d.get("_speed_str", "N/A").strip()
            eta = d.get("_eta_str", "N/A").strip()

            file_frac = 0.0
            if totali and totali > 0:
                file_frac = scaricati / totali
                percentuale = file_frac * 100
                testo = f"Download {percentuale:.1f}%  -  velocita: {velocita}  -  ETA: {eta}"
                self.after(0, self._progressbar.set, file_frac)
                self.after(0, self._imposta_stato, testo, "default")

            # progresso complessivo playlist
            playlist_total = getattr(self, "_playlist_total", None) or d.get("info_dict", {}).get("playlist_count")
            current_index = d.get("playlist_index") or d.get("info_dict", {}).get("playlist_index")
            try:
                if playlist_total:
                    # playlist_index è 1-based
                    idx = int(current_index) if current_index else getattr(self, "_playlist_done", 0)
                    overall = (max(0, idx - 1) + file_frac) / float(playlist_total)
                    self.after(0, self._progress_playlist.set, overall)
            except Exception:
                pass

        elif stato == "finished":
            # incrementa contatore playlist se presente
            try:
                playlist_total = getattr(self, "_playlist_total", None)
                if playlist_total:
                    self._playlist_done = min(getattr(self, "_playlist_done", 0) + 1, playlist_total)
                    overall = self._playlist_done / float(playlist_total)
                    self.after(0, self._progress_playlist.set, overall)
                    self.after(0, self._log, f"Elementi completati: {self._playlist_done}/{playlist_total}")
            except Exception:
                pass

            self.after(0, self._progressbar.set, 1.0)
            self.after(0, self._imposta_stato, "Elaborazione in corso...", "default")
            self.after(0, self._log, "Download completato, elaborazione file...")

    # -----------------------------------------------------------------------
    # Callback completamento / errore
    # -----------------------------------------------------------------------
    def _on_download_completato(self):
        self._download_attivo = False
        self._btn_scarica.configure(state="normal")
        self._progressbar.set(1.0)
        self._progress_playlist.set(1.0)
        self._imposta_stato("Completato!", colore="green")
        self._log("Download e conversione completati con successo.")
        self._log("=" * 50)

    def _on_download_errore(self, messaggio: str):
        self._download_attivo = False
        self._btn_scarica.configure(state="normal")
        self._progressbar.set(0)
        self._progress_playlist.set(0)
        self._imposta_stato(f"Errore: {messaggio[:80]}", colore="red")
        self._log(f"ERRORE: {messaggio}")
        self._log("=" * 50)

    # -----------------------------------------------------------------------
    # Utility UI
    # -----------------------------------------------------------------------
    def _imposta_stato(self, testo: str, colore: str = "default"):
        """Aggiorna il testo della label di stato con il colore specificato."""
        mappa_colori = {
            "green": "#2ecc71",
            "red":   "#e74c3c",
            "default": customtkinter.ThemeManager.theme["CTkLabel"]["text_color"],
        }
        self._lbl_stato.configure(text=testo, text_color=mappa_colori.get(colore, mappa_colori["default"]))

    def _log(self, testo: str):
        """Aggiunge una riga al log testuale."""
        self._textbox_log.configure(state="normal")
        self._textbox_log.insert(tk.END, testo + "\n")
        self._textbox_log.see(tk.END)
        self._textbox_log.configure(state="disabled")


    class _YdlLogger:
        """Logger minimo per yt_dlp con output nel textbox."""
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

