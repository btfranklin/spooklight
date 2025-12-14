import tkinter as tk
from spooklight.gui.app import SpooklightApp

def main():
    root = tk.Tk()
    app = SpooklightApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
