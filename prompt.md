# Prompt per GitHub Copilot — App GUI YouTube Downloader

## Contesto del progetto

Crea un'applicazione desktop completa in **Python** per scaricare audio da YouTube.
L'app deve essere standalone e portabile: verrà distribuita come eseguibile tramite **PyInstaller**,
senza richiedere Python installato sul sistema dell'utente.

---

## Stack tecnologico

- **GUI:** `customtkinter` (tema moderno, supporto dark/light mode)
- **Download:** libreria `yt_dlp` importata direttamente (NON come subprocess)
- **Conversione audio:** `ffmpeg.exe` esterno, incluso nella sottocartella `./ffmpeg/ffmpeg.exe`
- **Threading:** modulo stdlib `threading` per non bloccare la GUI durante il download
- **Bundling:** compatibile con PyInstaller (`--onedir`)

---

## Struttura del progetto attesa

```
progetto/
├── main.py
├── requirements.txt
└── ffmpeg/
    └── ffmpeg.exe
```

Il file `requirements.txt` deve contenere:
```
yt-dlp
customtkinter
```

---

## Funzionalità richieste

### Interfaccia grafica
- Finestra principale ridimensionabile, larghezza minima 600px
- Titolo finestra: "YouTube Music Downloader"
- Supporto dark/light mode tramite CustomTkinter (default: dark)
- Layout verticale pulito con padding generoso

### Componenti UI (dall'alto verso il basso)
1. **Campo URL** — `CTkEntry` a larghezza piena con placeholder "Incolla URL YouTube..."
2. **Riga formato** — `CTkOptionMenu` con opzioni: `mp3 320kbps`, `mp3 192kbps`, `mp3 128kbps`, `m4a`, `wav`
3. **Riga cartella output** — `CTkEntry` (non editabile) + `CTkButton` "Sfoglia" che apre `filedialog.askdirectory()`
4. **Bottone "Scarica"** — `CTkButton` principale, disabilitato durante il download
5. **Barra di progresso** — `CTkProgressBar`, inizialmente a 0, aggiornata durante il download
6. **Label di stato** — testo dinamico che mostra lo stato corrente (es. "Download in corso...", "Completato!", errori)
7. **Log testuale** — `CTkTextbox` scrollabile (sola lettura) che mostra l'output dettagliato

### Logica di download
- Il download deve avvenire in un **thread separato** (`threading.Thread`) per non bloccare la GUI
- Usare `yt_dlp.YoutubeDL` con un dizionario `ydl_opts` configurato così:
  - `format`: selezionato in base alla scelta dell'utente nel menu formato
  - `outtmpl`: `{cartella_output}/%(title)s.%(ext)s`
  - `ffmpeg_location`: percorso risolto a `./ffmpeg/ffmpeg.exe`, gestendo sia l'esecuzione normale che il bundle PyInstaller tramite `sys._MEIPASS`
  - `postprocessors`: per mp3 usare `FFmpegExtractAudio` con `preferredcodec` e `preferredquality` appropriati
  - `progress_hooks`: lista con una funzione hook personalizzata
- La funzione hook di progresso deve:
  - Aggiornare la `CTkProgressBar` con il valore `downloaded_bytes / total_bytes`
  - Aggiornare la label di stato con percentuale e velocità
  - Usare `after()` di Tkinter per aggiornare la GUI dal thread secondario in modo thread-safe

### Gestione percorso ffmpeg (PyInstaller-safe)
```python
import sys, os

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'ffmpeg', 'ffmpeg.exe')
```

### Validazione input
- Prima di avviare il download, verificare che:
  - Il campo URL non sia vuoto
  - L'URL contenga `youtube.com` o `youtu.be`
  - La cartella di output sia stata selezionata
- In caso di validazione fallita, mostrare un messaggio nella label di stato (colore rosso)

### Gestione errori
- Racchiudere il download in `try/except`
- In caso di errore mostrare il messaggio nella label di stato e nel log
- Riabilitare il bottone "Scarica" al termine (sia successo che errore), sempre tramite `after()`

---

## Comportamento atteso durante un download

1. L'utente incolla l'URL e clicca "Scarica"
2. Il bottone si disabilita, la label mostra "Recupero informazioni..."
3. La progress bar si anima, la label aggiorna percentuale e velocità in tempo reale
4. Il log mostra il titolo del video e il formato scelto
5. A completamento: label verde "✓ Completato!", progress bar al 100%, bottone riabilitato

---

## Note per il bundling con PyInstaller

Dopo aver sviluppato e testato l'app, il comando di build corretto è:

```bash
pyinstaller --onedir --windowed --add-binary "ffmpeg/ffmpeg.exe;ffmpeg" --name "YTMusicDownloader" main.py
```

- `--onedir`: crea una cartella invece di un singolo exe (più veloce all'avvio)
- `--windowed`: nessuna finestra console
- `--add-binary`: include ffmpeg.exe nel bundle nella sottocartella `ffmpeg`

---

## Requisiti di qualità del codice

- Tutto il codice in un singolo file `main.py`
- Classe principale `App(customtkinter.CTk)` con metodi ben separati
- Nessun hardcoding di percorsi assoluti
- Commenti in italiano sui blocchi principali
- Codice compatibile con Python 3.10+
