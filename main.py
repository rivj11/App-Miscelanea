import tkinter as tk
from database.setup_db import crear_base_datos
from gui.splash_screen import splash_screen
from gui.login_window import login_window
from gui.main_window import main_window

def main():
    crear_base_datos()

    root = tk.Tk()
    root.withdraw()  

if __name__ == "__main__":
    main()