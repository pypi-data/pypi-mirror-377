import tkinter as tk
from tkinter import ttk, simpledialog


class CharSelector(tk.Frame):
    """Widget to select or input custom character set."""

    PRESETS = [" ░▒▓█", " .,:;=#", "Custom..."]

    def __init__(self, parent, title="Characters:", font=("Courier New", 12)):
        super().__init__(parent)

        tk.Label(self, text=title).pack(side=tk.LEFT, padx=5)
        self.combo = ttk.Combobox(self, values=self.PRESETS, font=font)
        self.combo.current(0)
        self.combo.pack(side=tk.LEFT, padx=5)

        self.title = title

    def get_characters(self) -> str:
        value = self.combo.get()
        if value == "Custom...":
            tmp = None
            while tmp is None:
                tmp = simpledialog.askstring(
                    "Custom characters",
                    "Enter a list of characters, ordered from lightest to darkest (e.g.: \" .,:;=#\")."
                )
            return tmp
        return value
