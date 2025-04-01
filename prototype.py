import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from tkinter import messagebox
from tkinter import PhotoImage
import os
import pandas as pd
import time
from PIL import Image, ImageTk
import sys
    
#FRAME PANTALLA DE CARGA DEL LOGO
# Función para mostrar la pantalla de carga
def splash_screen():
    splash = tk.Tk()
    splash.title("INVENTORY")
    splash.geometry("800x600")
    splash.configure(bg="white")

 # Cargar la imagen del logo
    image = Image.open("logo light.png") 
    image = image.resize((700, 700)) 
    logo = ImageTk.PhotoImage(image)

    label_logo = tk.Label(splash, image=logo, bg="white")
    label_logo.pack(pady=20)    

    splash.update()
    time.sleep(1) 

    splash.destroy()
    

# Función para inicializar la base de datos
def init_db():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Función para verificar credenciales
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
        login_window.destroy()  # Cerrar la ventana de login
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

# Función para registrar un usuario
def registrar_usuario():
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()

    if not usuario or not contrasena:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
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

# Función para cerrar toda la aplicación cuando se cierre el login
def cerrar_aplicacion():
    sys.exit()  # Cierra completamente la aplicación

#FRAME INVENTARIO
# Función para conectar con la base de datos
def conectar_db():
    return sqlite3.connect("inventario.db")

# Función para listar productos en la tabla
def listar_productos():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos ORDER BY id")
    productos = cursor.fetchall()
    conexion.close()
    return productos

# Función para reordenar IDs después de eliminar
def reordenar_ids():
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT id FROM productos ORDER BY id")
    productos = cursor.fetchall()
    
    nuevo_id = 1
    for producto in productos:
        cursor.execute("UPDATE productos SET id = ? WHERE id = ?", (nuevo_id, producto[0]))
        nuevo_id += 1
    
    conexion.commit()
    conexion.close()

# Función para obtener el siguiente ID disponible
def obtener_siguiente_id():    
    with conectar_db() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT MAX(id) FROM productos")
        max_id = cursor.fetchone()[0]
        return (max_id + 1) if max_id else 1

# Función para agregar un producto
def agregar_producto():
    nombre = entry_nombre.get().strip()
    categoria = entry_categoria.get().strip()
    precio = entry_precio.get().strip()
    cantidad = entry_cantidad.get().strip()
    proveedor = entry_proveedor.get().strip()
    
    if not nombre or not precio or not cantidad:
        messagebox.showerror("Error", "Nombre, Precio y Cantidad son obligatorios")
        return
    
    try:
        precio = float(precio)
        cantidad = int(cantidad)
    except ValueError:
        messagebox.showerror("Error", "Precio y Cantidad deben ser números válidos")
        return
    
    nuevo_id = obtener_siguiente_id()
    
    with conectar_db() as conexion:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO productos (id, nombre, categoria, precio, cantidad, proveedor) VALUES (?, ?, ?, ?, ?, ?)",
                       (nuevo_id, nombre, categoria, precio, cantidad, proveedor))
        conexion.commit()
    
    messagebox.showinfo("Éxito", "Producto agregado correctamente")
    actualizar_lista()
    
# Función para eliminar un producto y reordenar IDs
def eliminar_producto():
    seleccionados = tabla_productos.selection()  # Obtiene los productos seleccionados
    if not seleccionados:
        messagebox.showerror("Error", "Seleccione al menos un producto para eliminar.")
        return
    
    confirmacion = messagebox.askyesno("Confirmación", f"¿Está seguro de que desea eliminar {len(seleccionados)} producto(s)?")
    if not confirmacion:
        return
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    for item in seleccionados:
        producto_id = tabla_productos.item(item)['values'][0]  # Obtiene el ID del producto
        cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
    
    conexion.commit()
    conexion.close()
    
    reordenar_ids()  # Reordenar IDs después de eliminar
    messagebox.showinfo("Éxito", "Productos eliminados correctamente.")
    actualizar_lista()  # Refrescar la tabla con los datos actualizados

def actualizar_lista():
    for row in tabla_productos.get_children():
        tabla_productos.delete(row)
    
    for producto in listar_productos():
        producto_formateado = (
            producto[0], producto[1], producto[2], f"$ {producto[3]:,.2f} COP", producto[4], producto[5]
        )
        tabla_productos.insert("", "end", values=producto_formateado)    

def generar_pdf_inventario():

    productos = listar_productos()
        # Crear la carpeta "Inventario" si no existe
    carpeta_inventario = "Inventario"
    if not os.path.exists(carpeta_inventario):
        os.makedirs(carpeta_inventario)

    if not productos:
        messagebox.showerror("Error", "No hay productos en el inventario para exportar")
        return
    
    # Nombre del archivo con fecha y hora        
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    archivo_pdf = os.path.join (carpeta_inventario, f"inventario_{fecha_actual}.pdf")
    
    doc = SimpleDocTemplate(archivo_pdf, pagesize=letter)
    elementos = []
    styles = getSampleStyleSheet()
    
    fecha_generacion = Paragraph(f"<b>Inventario generado el:</b> {datetime.now().strftime('%Y-%m-%d %I:%M %p')}", styles['Normal'])
    elementos.append(fecha_generacion)
    elementos.append(Spacer(1, 20))  # Espaciado antes de la tabla
    
    encabezados = ["ID", "Nombre", "Categoría", "Precio", "Cantidad", "Proveedor"]
    tabla_datos = [encabezados] + [[str(dato) for dato in producto] for producto in productos]
    
    tabla = Table(tabla_datos, colWidths=[50, 80, 80, 80, 80, 80])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elementos.append(tabla)
    doc.build(elementos)
    messagebox.showinfo("Éxito", f"PDF de inventario generado: {archivo_pdf}")

def exportar_inventario_excel():
    productos = listar_productos()  # Obtener los productos de la base de datos
    
    if not productos:
        messagebox.showerror("Error", "No hay productos en el inventario para exportar")
        return
    
    # Convertir a un DataFrame
    df = pd.DataFrame(productos, columns=["ID", "Nombre", "Categoría", "Precio", "Cantidad", "Proveedor"])
    
    # Crear la carpeta "Exportaciones" si no existe
    carpeta_exportacion = "Inventario"
    if not os.path.exists(carpeta_exportacion):
        os.makedirs(carpeta_exportacion)

    # Guardar el archivo con fecha
    fecha_actual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    archivo_excel = os.path.join(carpeta_exportacion, f"inventario_{fecha_actual}.xlsx")
    
    # Guardar en Excel
    df.to_excel(archivo_excel, index=False)
    
    messagebox.showinfo("Éxito", f"Inventario exportado a: {archivo_excel}")

#FRAME VENTAS
# Función para registrar una venta usando nombre y cantidad
def registrar_venta():
    producto_input = entry_nombre_venta.get()
    cantidad_vendida = entry_cantidad_venta.get()
    
    if not producto_input or not cantidad_vendida:
        messagebox.showerror("Error", "Ingrese el ID o nombre del producto y la cantidad")
        return
    
    try:
        cantidad_vendida = int(cantidad_vendida)
    except ValueError:
        messagebox.showerror("Error", "La cantidad debe ser un número válido")
        return
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Verificar si la entrada es un número (ID) o un nombre
    if producto_input.isdigit():
        cursor.execute("SELECT id, cantidad, precio FROM productos WHERE id = ?", (int(producto_input),))
    else:
        cursor.execute("SELECT id, cantidad, precio FROM productos WHERE nombre = ?", (producto_input,))
    
    producto = cursor.fetchone()
    
    if not producto:
        messagebox.showerror("Error", "Producto no encontrado")
        conexion.close()
        return
    
    producto_id, cantidad_disponible, precio = producto
    if cantidad_vendida > cantidad_disponible:
        messagebox.showerror("Error", "Cantidad insuficiente en inventario")
        conexion.close()
        return
    
    nueva_cantidad = cantidad_disponible - cantidad_vendida
    total_venta = precio * cantidad_vendida  

    cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, producto_id))
    cursor.execute("INSERT INTO ventas (producto_id, cantidad_vendida, fecha, total) VALUES (?, ?, ?, ?)",
                   (producto_id, cantidad_vendida, datetime.now(), total_venta))
    
    conexion.commit()
    conexion.close()
    
    actualizar_lista()
    calcular_ventas()
    messagebox.showinfo("Éxito", "Venta registrada correctamente puedes desplazarte hacia la pestaña de inventario y registro diario para ver cambios")

    # Limpiar los campos de entrada
    entry_nombre_venta.delete(0, tk.END)
    entry_cantidad_venta.delete(0, tk.END)
    
#FRAME REGISTRO DIARIO    
# Función para generar el PDF de estadísticas
def generar_pdf():
    conexion = conectar_db()
    cursor = conexion.cursor()

    # Obtener estadísticas de ventas y gastos
    cursor.execute("SELECT SUM(total) FROM ventas")
    total_ventas = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(precio * cantidad) FROM productos")
    total_gastos = cursor.fetchone()[0] or 0
    cursor.execute("SELECT v.producto_id, p.nombre, v.cantidad_vendida, v.total, strftime('%Y-%m-%d %I:%M %p', v.fecha) "
                   "FROM ventas v JOIN productos p ON v.producto_id = p.id "
                   "ORDER BY v.fecha DESC")
    ventas = cursor.fetchall()
    conexion.close()

    if not ventas:
        messagebox.showerror("Error", "No hay ventas registradas para exportar")
        return
    
    # Crear la carpeta "Registro Diario" si no existe
    carpeta_registro = "Registro Diario"
    if not os.path.exists(carpeta_registro):
        os.makedirs(carpeta_registro)

    # Nombre del archivo con fecha y hora
    fecha_hora_actual = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    archivo_pdf = os.path.join(carpeta_registro, datetime.now().strftime('registro_diario_%Y-%m-%d_%H-%M-%S.pdf'))
    
    doc = SimpleDocTemplate(archivo_pdf, pagesize=letter)
    elementos = []
    styles = getSampleStyleSheet()
    
    encabezado = Paragraph(f"<b>Registro generado el:</b> {fecha_hora_actual}", styles['Normal'])
    elementos.append(encabezado)
    elementos.append(Spacer(1, 12))
    
    elementos.append(Paragraph(f"<b>Total Ventas:</b> $ {total_ventas:,.2f} COP", styles['Normal']))
    elementos.append(Paragraph(f"<b>Total Gastos:</b> $ {total_gastos:,.2f} COP", styles['Normal']))
    elementos.append(Paragraph(f"<b>Ganancia Neta:</b> $ {(total_ventas - total_gastos):,.2f} COP", styles['Normal']))
    elementos.append(Spacer(1, 20))
    
    # Crear tabla de ventas
    encabezados = ["ID", "Nombre", "Cantidad", "Total", "Fecha"]
    tabla_datos = [encabezados] + [[str(dato) for dato in venta] for venta in ventas]
    
    tabla = Table(tabla_datos, colWidths=[50, 80, 80, 80, 110])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elementos.append(tabla)
    doc.build(elementos)
    messagebox.showinfo("Éxito", f"PDF generado: {archivo_pdf}")

def exportar_ventas_excel():
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute(
        "SELECT v.producto_id, p.nombre, v.cantidad_vendida, v.total, v.fecha "
        "FROM ventas v JOIN productos p ON v.producto_id = p.id "
        "ORDER BY v.fecha DESC"
    )
    
    ventas = cursor.fetchall()
    conexion.close()
    
    if not ventas:
        messagebox.showerror("Error", "No hay ventas registradas para exportar")
        return
    
    # Convertir a DataFrame
    df = pd.DataFrame(ventas, columns=["ID Producto", "Nombre", "Cantidad Vendida", "Total", "Fecha"])
    
    # Crear la carpeta "Registro Diario" si no existe
    carpeta_exportacion = "Registro Diario"
    if not os.path.exists(carpeta_exportacion):
        os.makedirs(carpeta_exportacion)

    # Guardar el archivo con fecha
    fecha_actual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    archivo_excel = os.path.join(carpeta_exportacion, f"ventas_{fecha_actual}.xlsx")
    
    df.to_excel(archivo_excel, index=False)
    
    messagebox.showinfo("Éxito", f"Ventas exportadas a: {archivo_excel}")

# Función para calcular estadísticas de ventas y ganancias
def calcular_ventas():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT SUM(total) FROM ventas")
    total_ventas = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(precio * cantidad) FROM productos")
    total_gastos = cursor.fetchone()[0] or 0
    cursor.execute(
        "SELECT v.producto_id, p.nombre, v.cantidad_vendida, v.total, strftime('%Y-%m-%d %I:%M %p', v.fecha) "
        "FROM ventas v JOIN productos p ON v.producto_id = p.id "
        "ORDER BY v.fecha DESC"
    )  
    ventas = cursor.fetchall()
    conexion.close()

    label_total_ventas.config(text=f"Total Ventas: $ {total_ventas:,.2f} COP")
    label_total_gastos.config(text=f"Total Gastos: $ {total_gastos:,.2f} COP")
    label_ganancias.config(text=f"Ganancia Neta: $ {(total_ventas - total_gastos):,.2f} COP")

    for row in tabla_ventas.get_children():
        tabla_ventas.delete(row)

    for venta in ventas:
        tabla_ventas.insert("", "end", values=venta)

# Función para eliminar historial de ventas
def eliminar_historial_ventas():
    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM ventas")
    cantidad_ventas = cursor.fetchone()[0]

    if cantidad_ventas == 0:
        messagebox.showerror("Advertencia", "No hay historial de ventas para eliminar.")
        conexion.close()
        return 
    
    if messagebox.askyesno("Confirmación", "¿Seguro que desea eliminar el historial de ventas?"):
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM ventas")
        conexion.commit()
        conexion.close()
        calcular_ventas()
        messagebox.showinfo("Éxito", "Historial de ventas eliminado correctamente")


# Ejecutar la pantalla de carga antes de la app principal
splash_screen()


# Crear la ventana de login
login_window = tk.Tk()
login_window.title("Inicio de Sesión")
login_window.geometry("800x600")
# login_window.configure(bg="#000000") #para configurar el background


frame = tk.Frame(login_window)
frame.pack(pady=20)

#Cargar la imagen
try:
    img = PhotoImage(file="login (1).png")
    img_label = tk.Label(frame, image=img, bg="#BDBDBD")
    img_label.grid(row=0, column=0, columnspan=2, pady=10)
except:
    print("No se pudo cargar la imagen")

#Campos de usuario y contraseña
tk.Label(frame, text="Usuario:" , font=("Arial")).grid(row=1, column=0, sticky="e", padx=5, pady=5)
entry_usuario = tk.Entry(frame, width=20)
entry_usuario.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="Contraseña:", font=("Arial")).grid(row=2, column=0, sticky="e", padx=5, pady=5)
entry_contrasena = tk.Entry(frame, show="*", width=20)
entry_contrasena.grid(row=2, column=1, padx=5, pady=5)

#Botones de ingreso y registro
btn_frame = tk.Frame(frame)
btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

tk.Button(btn_frame, text="Ingresar", command=verificar_credenciales).pack(side="left", padx=5)
tk.Button(btn_frame, text="Registrar", command=registrar_usuario).pack(side="left", padx=5)

# Asociar el evento de cierre con la función para cerrar toda la aplicación
login_window.protocol("WM_DELETE_WINDOW", cerrar_aplicacion)

# Inicializar la base de datos
init_db()

# Ejecutar la ventana de login
login_window.mainloop()

# Ahora se abre la aplicación principal
# Crea la ventana principal pero oculta hasta q el login se verifique
root = tk.Tk()
root.title("Inventario Miscelánea")
root.geometry("800x600")

# Pestañas/notebook
notebook = ttk.Notebook(root)
frame_productos = ttk.Frame(notebook)
frame_ventas = ttk.Frame(notebook)
notebook.add(frame_productos, text="Inventario")
notebook.add(frame_ventas, text="Ventas")
notebook.pack(expand=True, fill="both")

# Sección de productos
frame_form = tk.Frame(frame_productos)
frame_form.pack(pady=10)


labels = ["Nombre", "Categoría", "Precio", "Cantidad", "Proveedor"]
entries = []
for i, label in enumerate(labels):
    tk.Label(frame_form, text=label).grid(row=i, column=0, padx=5, pady=5)
    entry = tk.Entry(frame_form)
    entry.grid(row=i, column=1, padx=5, pady=5)
    entries.append(entry)

entry_nombre, entry_categoria, entry_precio, entry_cantidad, entry_proveedor = entries

btn_agregar = tk.Button(frame_form, text="Agregar Producto", command=agregar_producto)
btn_agregar.grid(row=len(labels), column=0, columnspan=2, pady=10)

btn_eliminar = tk.Button(frame_form, text="Eliminar Producto", command=eliminar_producto)
btn_eliminar.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)

# Crear la pestaña de productos y agregar el botón para generar PDF de inventario
btn_generar_pdf_inventario = tk.Button(frame_productos, text="Generar PDF Inventario", command=generar_pdf_inventario)
btn_generar_pdf_inventario.pack(pady=5)

# Botón para exportar inventario a Excel
btn_exportar_inventario_excel = tk.Button(frame_productos, text="Exportar a Excel", command=exportar_inventario_excel)
btn_exportar_inventario_excel.pack(pady=5)

columns_productos = ("ID", "Nombre", "Categoría", "Precio", "Cantidad", "Proveedor")
tabla_productos = ttk.Treeview(frame_productos, columns=columns_productos, show="headings")
for col in columns_productos:
    tabla_productos.heading(col, text=col, anchor="center")
    tabla_productos.column(col, width=100, anchor="center")

tabla_productos.pack(expand=True, fill="both", padx=10, pady=10)
# Habilitar selección múltiple en el Treeview
tabla_productos.configure(selectmode="extended")

# Sección de ventas
frame_venta_form = tk.Frame(frame_ventas)
frame_venta_form.pack(pady=10)

tk.Label(frame_venta_form, text="Nombre del Producto o Id").grid(row=0, column=0, padx=5, pady=5)
entry_nombre_venta = tk.Entry(frame_venta_form)
entry_nombre_venta.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_venta_form, text="Cantidad vendida").grid(row=1, column=0, padx=5, pady=5)
entry_cantidad_venta = tk.Entry(frame_venta_form)
entry_cantidad_venta.grid(row=1, column=1, padx=5, pady=5)

btn_vender = tk.Button(frame_venta_form, text="Registrar Venta", command=registrar_venta)
btn_vender.grid(row=2, column=0, columnspan=2, pady=10)

# Crear la pestaña de estadísticas
frame_estadisticas = ttk.Frame(notebook)
notebook.add(frame_estadisticas, text="Registro Diario")

label_total_ventas = tk.Label(frame_estadisticas, text="Total Ventas: $ 0 COP", font=("Arial", 12))
label_total_ventas.pack(pady=5)

label_total_gastos = tk.Label(frame_estadisticas, text="Total Gastos: $ 0 COP", font=("Arial", 12))
label_total_gastos.pack(pady=5)

label_ganancias = tk.Label(frame_estadisticas, text="Ganancia Neta: $ 0 COP", font=("Arial", 12))
label_ganancias.pack(pady=5)

btn_generar_pdf = tk.Button(frame_estadisticas, text="Generar PDF", command=generar_pdf)
btn_generar_pdf.pack(pady=5)

# Botón para exportar ventas a Excel
btn_exportar_ventas_excel = tk.Button(frame_estadisticas, text="Exportar Ventas a Excel", command=exportar_ventas_excel)
btn_exportar_ventas_excel.pack(pady=5)

btn_calcular_totales = tk.Button(frame_estadisticas, text="Actualizar Totales", command=calcular_ventas)
btn_calcular_totales.pack(pady=5)

btn_eliminar_ventas = tk.Button(frame_estadisticas, text="Eliminar Historial de Ventas", command=eliminar_historial_ventas)
btn_eliminar_ventas.pack(pady=5)

columns_ventas = ("ID", "Nombre", "Cantidad Vendida", "Total", "Fecha")
tabla_ventas = ttk.Treeview(frame_estadisticas, columns=columns_ventas, show="headings")
for col in columns_ventas:
    tabla_ventas.heading(col, text=col, anchor="center")
    tabla_ventas.column(col, width=150, anchor="center") #para centrar el texto

tabla_ventas.pack(expand=True, fill="both", padx=10, pady=10)

actualizar_lista()
root.mainloop()