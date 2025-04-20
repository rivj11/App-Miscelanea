from tkinter import ttk, messagebox, simpledialog, PhotoImage
import tkinter as tk
import sqlite3
import sys
from database.setup_db import crear_base_datos
crear_base_datos()

CLAVE_ADMIN = "clave123"

def verificar_credenciales():
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()

    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?", (usuario, contrasena))
    usuario_encontrado = cursor.fetchone()
    conn.close()

    if usuario_encontrado:
        messagebox.showinfo("Éxito", "Inicio de sesión exitoso")
        login_window.destroy()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

def registrar_usuario():
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()

    if not usuario or not contrasena:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
        return

    clave_ingresada = simpledialog.askstring("Clave de Administrador", "Ingresa la clave de administrador:", show="*")
    if clave_ingresada != CLAVE_ADMIN:
        messagebox.showerror("Error", "Clave de administrador incorrecta. No se puede registrar el usuario.")
        return
    
    try:
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", (usuario, contrasena))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Usuario registrado correctamente")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El usuario ya existe")

def cerrar_aplicacion():
    sys.exit()  

login_window = tk.Tk()
login_window.title("Inicio de Sesión")
login_window.geometry("800x600")


frame = tk.Frame(login_window)
frame.pack(pady=20)

try:
    img = PhotoImage(file="assets/login (1).png")
    img_label = tk.Label(frame, image=img, bg="#AED6F1")
    img_label.grid(row=0, column=0, columnspan=2, pady=10)
except:
    print("No se pudo cargar la imagen")

tk.Label(frame, text="Usuario:" , font=("Arial")).grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_usuario = tk.Entry(frame, width=20)
entry_usuario.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="Contraseña:", font=("Arial")).grid(row=2, column=0, sticky="e", padx=5, pady=5)
entry_contrasena = tk.Entry(frame, show="*", width=20)
entry_contrasena.grid(row=2, column=1, padx=5, pady=5)

btn_frame = tk.Frame(frame)
btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

ttk.Button(btn_frame, text="Ingresar", command=verificar_credenciales).pack(side="left", padx=5)
ttk.Button(btn_frame, text="Registrar", command=registrar_usuario).pack(side="left", padx=5)

login_window.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)

login_window.mainloop()