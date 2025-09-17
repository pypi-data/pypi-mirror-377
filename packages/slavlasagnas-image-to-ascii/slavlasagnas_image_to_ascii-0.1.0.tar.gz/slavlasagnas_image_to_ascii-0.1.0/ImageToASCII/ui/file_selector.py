import tkinter as tk
from tkinter import filedialog
from PIL import ImageGrab

from ImageToASCII.ui.status_bar import StatusBar

class FileSelector(tk.Frame):
    """
    Widget that provides:
     - 'Choose an image' button -> calls on_file_selected(filepath)
     - 'Copy from clipboard' button -> calls on_clipboard_selected(PIL.Image)
     - small label showing the current status / selected file
    """

    def __init__(self, parent, on_file_selected=None, on_clipboard_selected=None, status_bar: StatusBar=None):
        super().__init__(parent)
        self.on_file_selected = on_file_selected
        self.on_clipboard_selected = on_clipboard_selected
        self.status_bar = status_bar

        self._build()

    def _build(self):
        # Buttons
        file_button = tk.Button(self, text="Choose an image", command=self._choose_file)
        file_button.pack(side=tk.LEFT, padx=5)

        clipboard_button = tk.Button(self, text="Copy from clipboard", command=self._from_clipboard)
        clipboard_button.pack(side=tk.RIGHT, padx=5)

    def _choose_file(self):
        filepath = filedialog.askopenfilename()
        if not filepath:
            return
        if callable(self.on_file_selected):
            self.on_file_selected(filepath)


    def _from_clipboard(self):
        try:
            image = ImageGrab.grabclipboard()
        except Exception:
            image = None
        if callable(self.on_clipboard_selected):
            self.on_clipboard_selected(image)

