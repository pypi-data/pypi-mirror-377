import tkinter as tk
from tkinter import scrolledtext


class ResultViewer(tk.Toplevel):
    """Popup window to display ASCII art."""

    def __init__(self, parent, ascii_art: str, title: str, font_size: int = 10):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{parent.winfo_screenwidth()}x{parent.winfo_screenheight()}")

        text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=("Courier New", font_size))
        text_area.pack(expand=True, fill="both")
        text_area.insert(tk.END, ascii_art)
        text_area.config(state=tk.DISABLED)
