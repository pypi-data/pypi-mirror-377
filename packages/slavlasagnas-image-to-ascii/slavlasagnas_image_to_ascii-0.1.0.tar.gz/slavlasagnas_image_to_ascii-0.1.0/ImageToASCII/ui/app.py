import tkinter as tk

from ImageToASCII.ascii_converter import ASCIIConverter, ImageProcessingError, FileTypeError
from ImageToASCII.ui.export_top import ExportTop
from ImageToASCII.ui.file_selector import FileSelector
from ImageToASCII.ui.size_selector import SizeSelector
from ImageToASCII.ui.char_selector import CharSelector
from ImageToASCII.ui.status_bar import StatusBar
from ImageToASCII.ui.result_viewer import ResultViewer


class App(tk.Tk):
    def __init__(self, backend: ASCIIConverter):
        super().__init__()
        self.backend = backend
        self.TITLE = "IToA - Image To ASCII Converter"

        # Main window config
        self.title(self.TITLE)
        self.geometry("640x480")

        self.size = None
        self.chars = None
        self.inverted = None

        self.create_widgets()

    def create_widgets(self) -> None:
        """ Creates/packs all widgets of the app """
        tk.Label(self, text="Welcome to IToA, the image to ASCII converter!").pack(pady=5)

        container = tk.Frame(self)

        # Status bar
        self.status_bar = StatusBar(self)

        # File selection
        file_frame = tk.Frame(container)
        self.file_selector = FileSelector(file_frame,
                                          on_file_selected=self.on_file_selected,
                                          on_clipboard_selected=self.on_clipboard_selected,
                                          status_bar=self.status_bar)

        # Size selector
        self.size_selector = SizeSelector(container)

        # Characters
        self.char_selector = CharSelector(container)

        # Inverted option
        self.inverted_var = tk.BooleanVar()
        inverted_button = tk.Checkbutton(
            container,
            text="Inverted colors (black on white for light apps)",
            variable=self.inverted_var
        )

        # Action buttons
        buttons = tk.Frame(self)

        # Packing
        container.pack(pady=5, expand=True)
        file_frame.pack(pady=5)
        self.file_selector.pack(fill="x")
        self.size_selector.pack(pady=15)
        self.char_selector.pack(pady=5)
        inverted_button.pack(pady=5)
        self.status_bar.pack(pady=10)
        buttons.pack(pady=10, fill="x")
        tk.Button(buttons, text="Quit", command=self.on_exit).pack(padx=10, side=tk.LEFT)
        tk.Button(buttons, text="Export to...", command=self.on_export).pack(padx=10, side=tk.RIGHT)
        tk.Button(buttons, text="Copy", command=self.on_copy).pack(padx=10, side=tk.RIGHT)
        tk.Button(buttons, text="Display", command=self.on_display).pack(padx=10, side=tk.RIGHT)

    def on_file_selected(self, filepath):
        """ Executes the appropriate response to selecting a local file """
        self.size_selector.unlock()
        try:
            self.backend.load_file(filepath)
            self.size_selector.set_size(self.backend.image.size)
            self.size_selector.lock()
            self.status_bar.set_success(f"Selected file: {filepath}")
        except ImageProcessingError as e:
            self.status_bar.set_error(f"Failed to load file {filepath}: {e}")
        except FileTypeError as e:
            self.status_bar.set_error(f"Failed to load file {filepath}: {e}")

    def on_clipboard_selected(self, image):
        self.size_selector.unlock()
        try:
            self.backend.load_clipboard(image)
            self.size_selector.set_size(self.backend.image.size)
            self.size_selector.lock()
            self.status_bar.set_success("Copied image from clipboard")
        except ImageProcessingError as e:
            self.status_bar.set_error(f"Failed to load file from clipboard: {e}")

    def retrieve_fields(self):
        self.size = self.size_selector.get_size()
        self.chars = self.char_selector.get_characters()
        self.inverted = self.inverted_var.get()

    def on_copy(self):
        self.retrieve_fields()
        try:
            ascii_art = self.backend.to_ascii(self.size, self.chars, self.inverted)
            self.clipboard_clear()
            self.clipboard_append(ascii_art)
            self.status_bar.set_success("ASCII copied to clipboard.")
        except Exception as e:
            self.status_bar.set_error(f"Conversion failed: {e}")

    def on_display(self):
        self.retrieve_fields()
        try:
            ascii_art = self.backend.to_ascii(self.size, self.chars, self.inverted)
            font_size = max(1, int(1024 / self.size[1]))
            ResultViewer(self, ascii_art, self.TITLE, font_size)
            self.status_bar.set_success("ASCII displayed.")
        except Exception as e:
            self.status_bar.set_error(f"Conversion failed: {e}")

    def on_export(self):
        self.retrieve_fields()
        try:
            ascii_art = self.backend.to_ascii(self.size, self.chars, self.inverted)
            ExportTop(self,self.TITLE, ascii_art, self.status_bar)
        except Exception as e:
            self.status_bar.set_error(f"Conversion failed: {e}")

    def on_exit(self):
        self.destroy()
        exit(0)
