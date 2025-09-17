from os.path import splitext
from PIL import Image

class ImageProcessingError(Exception):
    """Custom exception for image processing errors."""
    pass

class FileTypeError(Exception):
    """Custom exception for unwanted file type errors."""
    pass

class ASCIIConverter:
    FONT_RATIO = 0.44

    def __init__(self):
        self.image = None

    def load_file(self, filepath: str) -> None:
        """Load image from a file."""
        self.image = None
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.webm', '.bmp']
        try:
            self.image = Image.open(filepath)
        except Exception as e:
            name, ext = splitext(filepath)
            if ext.lower() not in allowed_extensions:
                raise FileTypeError(f"File extension is not from an image") from e
            else:
                raise ImageProcessingError(f"Could not open file: {filepath}") from e

    def load_clipboard(self, image: Image.Image) -> None:
        """Load image from clipboard (expects a PIL.Image object)."""
        self.image = None
        if image is None:
            raise ImageProcessingError("No image found in clipboard")
        self.image = image

    def to_ascii(self, size: tuple[int, int], characters: str, inverted: bool) -> str:
        """Convert the current image to ASCII art."""
        if self.image is None:
            raise ImageProcessingError("No image loaded")

        if not isinstance(size, tuple) or len(size) != 2:
            raise ValueError("Size must be a tuple of two integers (width, height)")
        if not characters or not isinstance(characters, str):
            raise ValueError("Characters must be a non-empty string")

        width, height = size[0], int(size[1] * self.FONT_RATIO)
        image = self.image.resize((width, height)).convert("L")

        if inverted:
            characters = characters[::-1]
        length = len(characters) - 1

        data = image.getdata()
        ascii_str = ""
        for y in range(height):
            for x in range(width):
                pixel = data[y * width + x]
                ascii_str += characters[(pixel * length) // 255]
            ascii_str += "\n"

        return ascii_str
