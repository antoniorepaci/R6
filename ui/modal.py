import customtkinter
from utils.localization import TRANSLATIONS


def show_copyright_modal(root, lang: str = "en"):
    """Shows a copyright warning modal window before the main application window is shown."""
    modal = customtkinter.CTkToplevel(root)
    texts = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

    modal.title(texts["modal_title"])
    modal.resizable(False, False)
    modal.grab_set()

    # Center the modal window on the screen
    modal.update_idletasks()
    width = 520
    height = 280
    x = (modal.winfo_screenwidth() // 2) - (width // 2)
    y = (modal.winfo_screenheight() // 2) - (height // 2)
    modal.geometry(f"{width}x{height}+{x}+{y}")

    # Prevent closure via the 'X' button to force explicit agreement
    modal.protocol("WM_DELETE_WINDOW", lambda: None)

    # Internal title / header
    lbl_title = customtkinter.CTkLabel(
        modal,
        text=texts["modal_header"],
        font=customtkinter.CTkFont(size=17, weight="bold"),
    )
    lbl_title.pack(pady=(28, 12), padx=24)

    # Detailed warning text
    lbl_text = customtkinter.CTkLabel(
        modal,
        text=texts["modal_text"],
        font=customtkinter.CTkFont(size=13),
        justify="center",
        wraplength=460,
    )
    lbl_text.pack(pady=(0, 20), padx=24)

    def _accept():
        modal.grab_release()
        modal.destroy()
        root.deiconify()

    btn_accept = customtkinter.CTkButton(
        modal,
        text=texts["modal_btn"],
        height=40,
        font=customtkinter.CTkFont(size=14, weight="bold"),
        command=_accept,
    )
    btn_accept.pack(pady=(0, 24))
