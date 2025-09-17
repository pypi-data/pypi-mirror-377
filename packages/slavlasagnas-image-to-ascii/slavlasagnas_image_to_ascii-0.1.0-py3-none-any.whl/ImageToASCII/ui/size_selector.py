import tkinter as tk
from tkinter import ttk
from math import ceil


class SizeSelector(tk.Frame):
    """Widget to select output width/height with aspect ratio lock."""

    def __init__(self, parent, default_size=(1, 1)):
        super().__init__(parent)

        self.size_ratio_lock = False
        self.size_ratio = 1
        self.size_spinbox_mutex = True

        # Width
        tk.Label(self, text="Width:").pack(side=tk.LEFT, padx=5)
        self.width_var = tk.IntVar(value=default_size[0])
        self.width_var.trace_add("write", self.on_width_change)
        self.width_spinbox = ttk.Spinbox(self, from_=1, to=1024, textvariable=self.width_var)
        self.width_spinbox.pack(side=tk.LEFT, padx=(5, 15))

        # Height
        tk.Label(self, text="Height:").pack(side=tk.LEFT, padx=(15, 5))
        self.height_var = tk.IntVar(value=default_size[1])
        self.height_var.trace_add("write", self.on_height_change)
        self.height_spinbox = ttk.Spinbox(self, from_=1, to=1024, textvariable=self.height_var)
        self.height_spinbox.pack(side=tk.LEFT, padx=5)

        # Ratio lock button
        self.lock_button = tk.Button(self, text="Lock ratio", command=self.toggle_lock)
        self.lock_button.pack(side=tk.RIGHT, padx=15)

    def lock(self):
        self.size_ratio_lock = True
        self.lock_button.config(text="Unlock ratio")
        self.size_ratio = self.width_var.get() / self.height_var.get()

    def unlock(self):
        self.size_ratio_lock = False
        self.lock_button.config(text="Lock ratio")

    def toggle_lock(self):
        if not self.size_ratio_lock and (self.width_var.get() or self.height_var.get()):
            self.lock()
        else:
            self.unlock()

    def on_width_change(self, *args):
        if self.size_ratio_lock and self.size_spinbox_mutex:
            try:
                width = self.width_var.get()
                self.size_spinbox_mutex = False
                self.height_var.set(ceil(width / self.size_ratio))
                self.size_spinbox_mutex = True
            except Exception:
                pass

    def on_height_change(self, *args):
        if self.size_ratio_lock and self.size_spinbox_mutex:
            try:
                height = self.height_var.get()
                self.size_spinbox_mutex = False
                self.width_var.set(ceil(height * self.size_ratio))
                self.size_spinbox_mutex = True
            except Exception:
                pass

    def get_size(self) -> tuple[int, int]:
        return (self.width_var.get(), self.height_var.get())

    def set_size(self, size: tuple[int, int]):
        self.width_var.set(size[0])
        self.height_var.set(size[1])
        self.size_ratio = size[0] / size[1]
