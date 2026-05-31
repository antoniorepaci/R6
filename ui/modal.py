import customtkinter


def show_copyright_modal(root):
    """Mostra una finestra modale di avviso copyright prima dell'app principale."""
    modale = customtkinter.CTkToplevel(root)
    modale.title("⚠️ Avviso sul Copyright")
    modale.resizable(False, False)
    modale.grab_set()

    # Centra la finestra modale sullo schermo
    modale.update_idletasks()
    larghezza = 520
    altezza = 280
    x = (modale.winfo_screenwidth() // 2) - (larghezza // 2)
    y = (modale.winfo_screenheight() // 2) - (altezza // 2)
    modale.geometry(f"{larghezza}x{altezza}+{x}+{y}")

    # Impedisce la chiusura tramite il tasto X
    modale.protocol("WM_DELETE_WINDOW", lambda: None)

    # Icona / titolo interno
    lbl_titolo = customtkinter.CTkLabel(
        modale,
        text="⚠️ Avviso sul Copyright",
        font=customtkinter.CTkFont(size=17, weight="bold"),
    )
    lbl_titolo.pack(pady=(28, 12), padx=24)

    # Testo dell'avviso
    testo_avviso = (
        "Questo strumento è destinato esclusivamente al download di contenuti\n"
        "di cui hai i diritti o che sono rilasciati con licenza libera.\n\n"
        "Scaricare musica protetta da copyright senza autorizzazione è illegale.\n\n"
        "Utilizzando questa app accetti di esserne l'unico responsabile."
    )
    lbl_testo = customtkinter.CTkLabel(
        modale,
        text=testo_avviso,
        font=customtkinter.CTkFont(size=13),
        justify="center",
        wraplength=460,
    )
    lbl_testo.pack(pady=(0, 20), padx=24)

    def _accetta():
        modale.grab_release()
        modale.destroy()
        root.deiconify()

    btn_accetta = customtkinter.CTkButton(
        modale,
        text="Ho capito, continua",
        height=40,
        font=customtkinter.CTkFont(size=14, weight="bold"),
        command=_accetta,
    )
    btn_accetta.pack(pady=(0, 24))

