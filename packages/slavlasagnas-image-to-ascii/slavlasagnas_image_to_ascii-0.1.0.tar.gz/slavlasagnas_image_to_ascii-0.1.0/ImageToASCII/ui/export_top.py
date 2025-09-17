import tkinter as tk
from tkinter import ttk, filedialog

from ImageToASCII.utils import open_with_default_app
from ImageToASCII.ui.status_bar import StatusBar

class ExportTop(tk.Toplevel):
    def __init__(self, parent, title: str, ascii_art, status_bar: StatusBar=None):
        super().__init__(parent)
        self.title(title)
        self.config(padx=10,pady=10)

        self.export_functions = {
            "To .txt file": self.save_to_txt_file,
        }
        self.ascii_art = ascii_art
        self.status_bar = status_bar

        export_label = tk.Label(self, text="Choose how you would like to export:")
        export_label.pack(side="top", fill="x")

        self.export_options = ttk.Combobox(self, values=list(self.export_functions.keys()))
        self.export_options.current(0)
        self.export_options.pack(padx=5, pady=5)

        self.open_on_export_var = tk.BooleanVar()
        self.open_on_export_checkbox = tk.Checkbutton(
            self,
            text="Open file in default app on export",
            variable=self.open_on_export_var
        )
        self.open_on_export_checkbox.pack(padx=5, pady=5)

        self.export_button = tk.Button(self, text="Export", command=self.on_export)
        self.export_button.pack(padx=5, pady=5)

    def on_export(self):
        export_function = self.export_functions[self.export_options.get()]
        file = export_function()
        if self.open_on_export_var.get():
            open_with_default_app(file)

    def save_to_txt_file(self) -> str:
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.ascii_art)
        self.status_bar.set_success("Successfully exported and saved to " + filepath)
        return filepath
