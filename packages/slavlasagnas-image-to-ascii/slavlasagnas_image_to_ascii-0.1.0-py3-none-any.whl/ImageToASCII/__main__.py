from ImageToASCII.ascii_converter import ASCIIConverter
from ImageToASCII.ui.app import App

def run():
    converter = ASCIIConverter()
    app = App(converter)
    app.mainloop()

if __name__ == "__main__":
    run()
