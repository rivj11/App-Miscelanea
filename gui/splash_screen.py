import tkinter as tk
import time
from PIL import Image, ImageTk

def splash_screen():
    splash = tk.Tk()
    splash.title("INVENTORY")
    splash.geometry("800x600")
    splash.configure(bg="white")

    image = Image.open("assets/splash.png") 
    image = image.resize((700, 700)) 
    logo = ImageTk.PhotoImage(image)


    label_logo = tk.Label(splash,image=logo, bg="white")
    label_logo.image = logo
    label_logo.pack(pady=20)    

    splash.update()
    time.sleep(1) 

    splash.destroy()
splash_screen()