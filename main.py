import sys
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter
import yt_dlp

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


def get_ffmpeg_path() -> str:
    """Restituisce il percorso assoluto di ffmpeg.exe,
    compatibile sia con esecuzione normale che bundle PyInstaller."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "ffmpeg", "ffmpeg.exe")


def costruisci_ydl_opts(formato: str, cartella_output: str, progress_hook, logger=None, allow_playlist: bool = False, playlist_items: str = None) -> dict:
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


# ---------------------------------------------------------------------------
# Classe principale dell'applicazione
# ---------------------------------------------------------------------------
class App(customtkinter.CTk):

    def __init__(self):
        super().__init__()

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

    # -----------------------------------------------------------------------
    # Costruzione UI
    # -----------------------------------------------------------------------
    def _build_ui(self):
        padding = {"padx": 20, "pady": 8}

        # Titolo
        self._lbl_titolo = customtkinter.CTkLabel(
            self,
            text="YouTube Music & Video Downloader",
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        self._lbl_titolo.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 4))

        # 1. Campo URL
        self._lbl_url = customtkinter.CTkLabel(self, text="URL YouTube:", anchor="w")
        self._lbl_url.grid(row=1, column=0, sticky="ew", **padding)

        self._entry_url = customtkinter.CTkEntry(
            self, placeholder_text="Incolla URL YouTube...", height=38,
        )
        self._entry_url.grid(row=2, column=0, sticky="ew", **padding)

        # 2. Selezione formato (audio + video)
        self._lbl_formato = customtkinter.CTkLabel(self, text="Formato:", anchor="w")
        self._lbl_formato.grid(row=3, column=0, sticky="ew", **padding)

        self._var_formato = customtkinter.StringVar(value=TUTTI_I_FORMATI[0])
        self._menu_formato = customtkinter.CTkOptionMenu(
            self, values=TUTTI_I_FORMATI, variable=self._var_formato, height=38,
        )
        self._menu_formato.grid(row=4, column=0, sticky="ew", **padding)

        # Checkbox scarica playlist
        self._chk_playlist = customtkinter.CTkCheckBox(self, text="Scarica playlist (se presente)", variable=self._var_allow_playlist)
        self._chk_playlist.grid(row=5, column=0, sticky="w", padx=20, pady=(0, 8))


        # 3. Cartella di output
        self._lbl_output = customtkinter.CTkLabel(self, text="Cartella di output:", anchor="w")
        self._lbl_output.grid(row=6, column=0, sticky="ew", **padding)

        self._frame_output = customtkinter.CTkFrame(self, fg_color="transparent")
        self._frame_output.grid(row=7, column=0, sticky="ew", **padding)
        self._frame_output.grid_columnconfigure(0, weight=1)

        self._entry_output = customtkinter.CTkEntry(
            self._frame_output,
            placeholder_text="Nessuna cartella selezionata...",
            state="disabled",
            height=38,
        )
        self._entry_output.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._btn_sfoglia = customtkinter.CTkButton(
            self._frame_output, text="Sfoglia", width=90, height=38,
            command=self._sfoglia_cartella,
        )
        self._btn_sfoglia.grid(row=0, column=1)

        # 4. Bottone Scarica
        self._btn_scarica = customtkinter.CTkButton(
            self,
            text="Scarica",
            height=44,
            font=customtkinter.CTkFont(size=15, weight="bold"),
            command=self._avvia_download,
        )
        self._btn_scarica.grid(row=8, column=0, sticky="ew", padx=20, pady=(16, 8))

        # 5. Barra di progresso (file corrente)
        self._progressbar = customtkinter.CTkProgressBar(self, height=14)
        self._progressbar.set(0)
        self._progressbar.grid(row=9, column=0, sticky="ew", **padding)

        # Barra di progresso playlist (totale) - inizialmente nascosta impostando height a 10
        self._progress_playlist = customtkinter.CTkProgressBar(self, height=10)
        self._progress_playlist.set(0)
        self._progress_playlist.grid(row=10, column=0, sticky="ew", padx=20, pady=(4, 0))

        # 6. Label di stato
        self._lbl_stato = customtkinter.CTkLabel(
            self, text="In attesa...", anchor="w",
            font=customtkinter.CTkFont(size=13),
        )
        self._lbl_stato.grid(row=11, column=0, sticky="ew", padx=20, pady=(4, 0))

        # 7. Log testuale scrollabile
        self._lbl_log = customtkinter.CTkLabel(self, text="Log:", anchor="w")
        self._lbl_log.grid(row=12, column=0, sticky="ew", **padding)

        self._textbox_log = customtkinter.CTkTextbox(self, height=220, state="disabled")
        self._textbox_log.grid(row=13, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.grid_rowconfigure(13, weight=1)

    # -----------------------------------------------------------------------
    # Azioni UI
    # -----------------------------------------------------------------------
    def _sfoglia_cartella(self):
        """Apre il dialogo di selezione cartella."""
        cartella = filedialog.askdirectory(title="Seleziona cartella di output")
        if cartella:
            self._entry_output.configure(state="normal")
            self._entry_output.delete(0, tk.END)
            self._entry_output.insert(0, cartella)
            self._entry_output.configure(state="disabled")

    def _avvia_download(self):
        """Valida gli input e avvia il download in un thread separato."""
        if self._download_attivo:
            return

        url = self._entry_url.get().strip()
        cartella = self._entry_output.get().strip()
        formato = self._var_formato.get()
        allow_playlist = self._var_allow_playlist.get()

        # Validazione input
        if not url:
            self._imposta_stato("[!] Inserisci un URL YouTube valido.", colore="red")
            return
        if "youtube.com" not in url and "youtu.be" not in url:
            self._imposta_stato("[!] L'URL non sembra un link YouTube.", colore="red")
            return
        if not cartella:
            self._imposta_stato("[!] Seleziona una cartella di output.", colore="red")
            return
        if not os.path.isdir(cartella):
            self._imposta_stato("[!] La cartella di output non esiste.", colore="red")
            return
        if not os.path.isfile(get_ffmpeg_path()):
            self._imposta_stato("[!] ffmpeg.exe mancante in ./ffmpeg.", colore="red")
            self._log("ERRORE: ffmpeg.exe non trovato in ffmpeg/ffmpeg.exe")
            return

        # Avvio download
        self._download_attivo = True
        self._btn_scarica.configure(state="disabled")
        self._progressbar.set(0)
        self._progress_playlist.set(0)
        self._playlist_total = None
        self._playlist_done = 0
        self._imposta_stato("Recupero informazioni...", colore="default")
        self._log(f"URL: {url}")
        self._log(f"Formato selezionato: {formato}")
        self._log(f"Destinazione: {cartella}")
        self._log(f"Scarica playlist: {allow_playlist}")
        self._log("-" * 50)

        thread = threading.Thread(
            target=self._thread_download,
            args=(url, formato, cartella),
            daemon=True,
        )
        thread.start()

    # -----------------------------------------------------------------------
    # Thread di download
    # -----------------------------------------------------------------------
    def _thread_download(self, url: str, formato: str, cartella: str):
        """Esegue il download nel thread separato."""
        try:
            allow_playlist = self._var_allow_playlist.get()
            ydl_opts = costruisci_ydl_opts(
                formato,
                cartella,
                self._progress_hook,
                logger=self._YdlLogger(self),
                allow_playlist=allow_playlist,
            )

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Recupera informazioni prima del download
                info = ydl.extract_info(url, download=False)

                # se è playlist e l'utente ha scelto di scaricare la playlist, chiedi conferma per playlist grandi
                entries = info.get("entries") if isinstance(info, dict) else None
                total_entries = None
                if entries is not None:
                    # some entries might be generators; try to get len safely
                    try:
                        total_entries = len(entries)
                    except Exception:
                        total_entries = info.get("playlist_count") or info.get("n_entries")

                if total_entries is None and isinstance(info, dict) and info.get("_type") == "playlist":
                    total_entries = info.get("playlist_count")

                if total_entries:
                    self._playlist_total = total_entries
                else:
                    self._playlist_total = 1

                # Se l'utente ha scelto di scaricare la playlist ma la playlist è grande, chiedi conferma
                if allow_playlist and self._playlist_total and self._playlist_total > 20:
                    # crea evento di sincronizzazione
                    self._playlist_confirm_event = threading.Event()

                    def _prompt_confirm():
                        risposta = messagebox.askyesno("Conferma playlist", f"La playlist contiene {self._playlist_total} elementi. Vuoi continuare?")
                        self._playlist_confirm_result = risposta
                        self._playlist_confirm_event.set()

                    self.after(0, _prompt_confirm)
                    # aspetta la scelta dell'utente
                    self._playlist_confirm_event.wait()
                    if not self._playlist_confirm_result:
                        # utente ha annullato
                        self.after(0, self._on_download_errore, "Download playlist annullato dall'utente.")
                        return

                titolo = info.get("title", "Titolo sconosciuto") if isinstance(info, dict) else "Titolo"
                self.after(0, self._log, f"Titolo: {titolo}")
                self.after(0, self._imposta_stato, f"Download in corso: {titolo}", "default")

                # Avvia il download effettivo
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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
