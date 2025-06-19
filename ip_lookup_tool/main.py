# main.py
import tkinter as tk
from ui.app_gui import IPToolGUI

def main():
    """Initializes and runs the Tkinter GUI application."""
    root = tk.Tk()
    app = IPToolGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()