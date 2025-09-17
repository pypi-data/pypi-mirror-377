import tkinter as tk


class StatusBar(tk.Frame):
    """Widget to display success/error messages."""

    def __init__(self, parent):
        super().__init__(parent)
        self.success_label = tk.Label(self, fg="green")
        self.success_label.pack(pady=5)
        self.error_label = tk.Label(self, fg="red")
        self.error_label.pack(pady=5)

    def set_success(self, text: str):
        self.success_label.config(text=text)
        self.error_label.config(text="")

    def set_error(self, text: str):
        self.error_label.config(text=text)
        self.success_label.config(text="")
