# IToA - Image To ASCII Converter

IToA (Image To ASCII) is a simple Python application that converts images into ASCII art. It comes with a graphical interface
built using Tkinter and Pillow (PIL), allowing you to load images, adjust the output size, choose characters, copy the result
to the clipboard, and export to text files.

---

## Features

- **Load images** from:
  - A file (`.png`, `.jpg`, etc.)
  - The system clipboard (if an image is copied)
- **Adjust output size** with width and height spinboxes
  - Lock/unlock aspect ratio
- **Character sets**:
  - Predefined sets (e.g. `░▒▓█`, ` .,:;=#`)
  - Custom character string
- **Inverted colors option** (useful for light vs dark backgrounds)
- **View result**:
  - Display ASCII art in a scrollable new window
  - Copy ASCII art to clipboard
  - Export ASCII art to text files
  - Automatically open text files after exporting and saving 
- **Error handling** with simple popup messages

---

## Requirements

- Python **3.10+** (earlier versions may also work)
- Dependencies:
  - [Pillow](https://pypi.org/project/pillow/) `pip install pillow`
  - [Tkinter](https://docs.python.org/fr/3.13/library/tkinter.html) `pip install tkinter` (usually comes preinstalled with Python)
  - Pillow-compatible clipboard package such as `xclip` or `wl-clipboard` (Linux only) 

---

## Installation

Clone the repository:

```bash
git clone https://github.com/SlavLasagna/IToA.git
```

Install dependencies:
```bash
cd IToA
pip install pillow
pip install tkinter
```

---

## Usage

Run the program:
```bash
python main.py
```

### Steps:

1. Choose an image file, or copy an image from clipboard
2. Adjust width and height (and lock ratio between the two)
3. Select a character set (or enter custom characters if choosing `"Custom..."`)
4. Optionally switch from white text on black background, to black text on white background (`Inverted Colors` checkbox)
5. Convert:
   - Display ASCII art in a new window
   - Copy ASCII art directly to clipboard
   - Open the "Export to file" pop-up:
     - Specify the type of export wanted (only to .txt file for now)
     - Toggle opening the file in the default app after exporting and saving. <br>
     ⚠ **May not work on every OS** (utils functions were designed for Windows, Linux and macOS)

---

## Examples

### Using the GUI

Image input: [GitHub Logo](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSbqj9Ii13d6hx5a9kyLnC5A8A96LDSaSZv_w&s)

Settings:
- Size = 64 x 64 px
- Characters = ` ░▒▓█`
- Not inverted (white on black)

Output ASCII :
```
████████████████████████████████████████████████████████████████
████████████████████████████████████████████████████████████████
████████████████████████████████████████████████████████████████
███████████████████████▓▓▓▓▒▒▒▒▒▒▒▒▒▒▓▓▓▓███████████████████████
███████████████████▓▒▒░                  ░▒▒▓███████████████████
████████████████▓▒░                          ░▒▓████████████████
█████████████▓▒░                                ░▒▓█████████████
████████████▒░                                    ░▒████████████
██████████▓░      ░▓▓▓▓▒░   ░░░░░░░░   ░▒▓▓▓▓░      ░▓██████████
█████████▓        ▒██████▓▓▓████████▓▓▓██████▒        ▓█████████
████████▓         ░▓▓██████████████████████▓█░         ▓████████
███████▓░        ░▓▓▓████████████████████████▓░        ░▓███████
███████▓        ░▓█████████████████████████████░        ▓███████
███████▒        ▒█▓████████████████████████████▒        ▒███████
███████▒        ▒██████████████████████████████▒        ▒███████
███████▒         ▓████████████████████████████▓░        ▒███████
███████▓         ░▓██████████████████████████▓░         ▓███████
████████▒          ▒▓██████████████████████▓▒          ▒████████
███████▓█▒    ░▒░    ░░▒▒▓▓▓▓███████▓▓▓▒▒░░           ▒█▓███████
██████████▒    ░▓▓▒       ░▓████████▓░               ▒██████████
███████████▓░    ▒█▓▒░░░░▒▓██████████▓             ░▓███████████
████████████▓▒░   ░▒▓▓▓▓▓▓▓▓█████████▓░          ░▒▓████████████
██████████████▓▓░         ▓██████████▓         ░▓▓██████████████
█████████████████▓▓▒░     ▓██████████▓     ░▒▓▓█████████████████
█████████████████████▓▓▒▒▒▓▓█████████▓▒▒▒▓▓█████████████████████
████████████████████████████████████████████████████████████████
████████████████████████████████████████████████████████████████
████████████████████████████████████████████████████████████████
```

### Using only the ASCIIConverter

Loading an image from a file:

```python

import ImageToASCII as ac

filepath = r"/path/to/image"
ascii_converter = ac.ASCIIConverter()
ascii_converter.load_image(filepath)
```
`ASCIIConverter.load_image` **may raise custom exceptions**, such as:
- `ascii_converter.FileTypeError`, whenever the extension of the loaded file does not match the accepted extensions
- `ascii_converter.ImageProcessingError`, for any other type of exception due to Pillow's image loading

These exceptions are mainly used to have custom error display.

Converting the loaded image to ASCII:

```python

import ImageToASCII as ac

filepath = r"/path/to/file"
size = (64, 64)
characters = " .,:;/#"
inverted = False

ascii_converter = ac.ASCIIConverter()
try:
    ascii_converter.load_file(filepath)
    result = ascii_converter.to_ascii(size, characters, inverted)
    # Custom handling of the result
except Exception as e:
    # Custom handling of the exceptions
    pass
```
Here, `size` is the size of the image in pixels/characters, `characters` is the list of characters corresponding 
to the B&W value of the pixels and `inverted` is a boolean which reverses `characters` before converting, effectively
inverting the values of the pixels.

---

## Project Structure

```
IToA/
├── converter.py
├── main.py
├── ui/
│   ├── app.py
│   ├── char_selector.py
│   ├── export_top.py
│   ├── file_selector.py
│   ├── result_viewer.py
│   ├── size_selector.py
│   └── status_bar.py
└── utils.py
```

---

## Roadmap

☑ Factorize code (split backend logic and UI) <br>
☑ Add export options (saving to text file ~~or bitmap~~ and opening file on export) <br>
☐ Package as a standalone executable

---

## Notes & Warnings

- Pixels of images that are completely transparent will be rendered black.
- Because fonts are not equal in width and height, ASCII arts tend to warp vertically the smaller the font size is.
  This means that, because font size is locked to the image size, when displayed in the GUI, the bigger the image,
  the bigger the distortion.

---

## License


This project is licensed under the GNU General Public License v3.0 (GPL-3.0) - see the [LICENSE](LICENSE) file for details.