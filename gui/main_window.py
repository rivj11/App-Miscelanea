import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from tkinter import messagebox
import os
import pandas as pd
from PIL import Image, ImageTk
from fpdf import FPDF

CLAVE_ADMIN = "clave123"

def conectar_db():
    return sqlite3.connect("inventario.db")

def listar_productos():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos ORDER BY id")
    productos = cursor.fetchall()
    conexion.close()
    return productos

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

def obtener_siguiente_id():    
    with conectar_db() as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT MAX(id) FROM productos")
        max_id = cursor.fetchone()[0]
        return (max_id + 1) if max_id else 1

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
    
def eliminar_producto():
    seleccionados = tabla_productos.selection()
    if not seleccionados:
        messagebox.showerror("Error", "Seleccione al menos un producto para eliminar.")
        return

    # Solicitar clave del administrador
    clave_admin = simpledialog.askstring("Clave Administrador", "Introduce la clave del administrador:", show='*')
    if clave_admin != "clave123":  # Reemplaza "clave123" por tu clave real
        messagebox.showerror("Acceso Denegado", "Clave incorrecta. No se eliminó ningún producto.")
        return

    confirmacion = messagebox.askyesno("Confirmación", f"¿Está seguro de que desea eliminar {len(seleccionados)} producto(s)?")
    if not confirmacion:
        return

    conexion = conectar_db()
    cursor = conexion.cursor()

    for item in seleccionados:
        producto_id = tabla_productos.item(item)['values'][0]
        cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))

    conexion.commit()
    conexion.close()

    reordenar_ids()
    messagebox.showinfo("Éxito", "Productos eliminados correctamente.")
    actualizar_lista()

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
    carpeta_inventario = "Inventario"
    if not os.path.exists(carpeta_inventario):
        os.makedirs(carpeta_inventario)

    if not productos:
        messagebox.showerror("Error", "No hay productos en el inventario para exportar")
        return
    
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    archivo_pdf = os.path.join (carpeta_inventario, f"inventario_{fecha_actual}.pdf")
    
    doc = SimpleDocTemplate(archivo_pdf, pagesize=letter)
    elementos = []
    styles = getSampleStyleSheet()
    
    fecha_generacion = Paragraph(f"<b>Inventario generado el:</b> {datetime.now().strftime('%Y-%m-%d %I:%M %p')}", styles['Normal'])
    elementos.append(fecha_generacion)
    elementos.append(Spacer(1, 20))
    
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
    os.startfile(archivo_pdf)

def exportar_inventario_excel():
    productos = listar_productos()
    
    if not productos:
        messagebox.showerror("Error", "No hay productos en el inventario para exportar")
        return
    
    df = pd.DataFrame(productos, columns=["ID", "Nombre", "Categoría", "Precio", "Cantidad", "Proveedor"])
    
    carpeta_exportacion = "Inventario"
    if not os.path.exists(carpeta_exportacion):
        os.makedirs(carpeta_exportacion)

    fecha_actual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    archivo_excel = os.path.join(carpeta_exportacion, f"inventario_{fecha_actual}.xlsx")
    
    df.to_excel(archivo_excel, index=False)
    
    messagebox.showinfo("Éxito", f"Inventario exportado a: {archivo_excel}")
    os.startfile(archivo_excel)

def registrar_venta():
    producto_input = entry_nombre_venta.get()
    cantidad_vendida = entry_cantidad_venta.get()
    nombre_cliente = entry_nombre_cliente.get()
    apellido_cliente = entry_apellido_cliente.get()
    celular_cliente = entry_celular_cliente.get()

    if not producto_input or not cantidad_vendida or not nombre_cliente or not apellido_cliente:
        messagebox.showerror("Error", "Debe completar todos los campos obligatorios (producto, cantidad, nombre y apellido del cliente).")
        return

    try:
        cantidad_vendida = int(cantidad_vendida)
    except ValueError:
        messagebox.showerror("Error", "La cantidad debe ser un número válido.")
        return

    conexion = conectar_db()
    cursor = conexion.cursor()

    if producto_input.isdigit():
        cursor.execute("SELECT id, nombre, cantidad, precio FROM productos WHERE id = ?", (int(producto_input),))
    else:
        cursor.execute("SELECT id, nombre, cantidad, precio FROM productos WHERE nombre = ?", (producto_input,))
    
    producto = cursor.fetchone()

    if not producto:
        messagebox.showerror("Error", "Producto no encontrado.")
        conexion.close()
        return

    producto_id, nombre_producto, cantidad_disponible, precio = producto
    if cantidad_vendida > cantidad_disponible:
        messagebox.showerror("Error", "Cantidad insuficiente en inventario.")
        conexion.close()
        return

    nueva_cantidad = cantidad_disponible - cantidad_vendida
    total_venta = precio * cantidad_vendida

    ts = datetime.now()
    fecha_actual = datetime.now().isoformat(" ")

    cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nueva_cantidad, producto_id))
    cursor.execute("INSERT INTO ventas (producto_id, cantidad_vendida, fecha, total) VALUES (?, ?, ?, ?)",
                   (producto_id, cantidad_vendida, fecha_actual, total_venta))

    conexion.commit()
    conexion.close()

    actualizar_lista()
    calcular_ventas()

    if not os.path.exists("ventas"):
        os.makedirs("ventas")

    timestamp_str = ts.strftime('%Y_%m_%d_%H_%M_%S')
    nombre_archivo = os.path.join("ventas", f"{nombre_cliente}_{apellido_cliente}_{timestamp_str}.pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Factura de Compra - Farmacia Cardozo", ln=True, align="C")
    pdf.ln(10)
    fecha_formateada = datetime.fromisoformat(fecha_actual).strftime('%Y-%m-%d %I:%M %p')
    pdf.cell(200, 10, txt=f"Fecha y hora: {fecha_formateada}", ln=True)
    pdf.cell(200, 10, txt=f"Cliente: {nombre_cliente} {apellido_cliente}", ln=True)
    if celular_cliente:
        pdf.cell(200, 10, txt=f"Celular: {celular_cliente}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Producto: {nombre_producto}", ln=True)
    pdf.cell(200, 10, txt=f"Cantidad: {cantidad_vendida}", ln=True)
    pdf.cell(200, 10, txt=f"Total: ${total_venta:.2f}", ln=True)

    pdf.output(nombre_archivo)

    os.startfile(nombre_archivo)

    messagebox.showinfo("Éxito", "Venta registrada y factura generada correctamente.")

    entry_nombre_venta.delete(0, tk.END)
    entry_cantidad_venta.delete(0, tk.END)
    entry_nombre_cliente.delete(0, tk.END)
    entry_apellido_cliente.delete(0, tk.END)
    entry_celular_cliente.delete(0, tk.END)

def generar_factura_pdf(nombre, apellido, celular, producto, cantidad, total, fecha):
    if not os.path.exists("ventas"):
        os.makedirs("ventas")

    nombre_archivo = f"{nombre}_{apellido}_{fecha.replace(':', '-').replace(' ', '_')}.pdf"
    ruta_archivo = os.path.join("ventas", nombre_archivo)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Miscelánea XYZ - Factura", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Fecha: {fecha}", ln=True)
    pdf.cell(200, 10, txt=f"Cliente: {nombre} {apellido}", ln=True)
    if celular:
        pdf.cell(200, 10, txt=f"Celular: {celular}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, txt="Detalle de compra:", ln=True)
    pdf.cell(200, 10, txt=f"Producto: {producto}", ln=True)
    pdf.cell(200, 10, txt=f"Cantidad: {cantidad}", ln=True)
    pdf.cell(200, 10, txt=f"Total: ${total:.2f}", ln=True)

    pdf.output(ruta_archivo)
    print(f"Factura guardada en: {ruta_archivo}")

def generar_pdf():
    conexion = conectar_db()
    cursor = conexion.cursor()

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
    
    carpeta_registro = "Registro Diario"
    if not os.path.exists(carpeta_registro):
        os.makedirs(carpeta_registro)

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
    
    os.startfile(archivo_pdf)

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
    
    df = pd.DataFrame(ventas, columns=["ID Producto", "Nombre", "Cantidad Vendida", "Total", "Fecha"])
    
    df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.strftime('%Y-%m-%d %I:%M %p')

    carpeta_exportacion = "Registro Diario"
    if not os.path.exists(carpeta_exportacion):
        os.makedirs(carpeta_exportacion)

    fecha_actual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    archivo_excel = os.path.join(carpeta_exportacion, f"registro_diario_{fecha_actual}.xlsx")
    
    df.to_excel(archivo_excel, index=False)

    messagebox.showinfo("Éxito", f"Ventas exportadas a: {archivo_excel}")
    
    os.startfile(archivo_excel)

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

def eliminar_historial_ventas():
    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM ventas")
    cantidad_ventas = cursor.fetchone()[0]

    if cantidad_ventas == 0:
        messagebox.showerror("Advertencia", "No hay historial de ventas para eliminar.")
        conexion.close()
        return 
    
    clave_admin = simpledialog.askstring("Clave Administrador", "Introduce la clave del administrador:", show='*')
    
    if clave_admin != "clave123":
        messagebox.showerror("Acceso Denegado", "Clave incorrecta. No se eliminó el historial.")
        return
    
    if messagebox.askyesno("Confirmación", "¿Seguro que desea eliminar el historial de ventas?"):
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM ventas")
        conexion.commit()
        conexion.close()
        calcular_ventas()
        messagebox.showinfo("Éxito", "Historial de ventas eliminado correctamente")

def actualizar_usuarios():
    for row in tabla_usuarios.get_children():
        tabla_usuarios.delete(row)

    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario FROM usuarios")
    for usuario in cursor.fetchall():
        tabla_usuarios.insert("", "end", values=usuario)
    conn.close()

def eliminar_usuario():
    seleccionado = tabla_usuarios.selection()
    if not seleccionado:
        messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar")
        return

    clave_admin = simpledialog.askstring("Clave Admin", "Ingrese la clave de administrador:", show='*')
    if clave_admin != CLAVE_ADMIN:
        messagebox.showerror("Error", "Clave incorrecta. Solo el administrador puede eliminar usuarios.")
        return

    usuario_id = tabla_usuarios.item(seleccionado, "values")[0]
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cursor.fetchone()[0]

    if total_usuarios == 0:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='usuarios'")
        conn.commit()
        conn.close()
        actualizar_usuarios()
        messagebox.showinfo("Aplicación cerrada", "Se ha eliminado el último usuario. La aplicación se cerrará. Si quiere añadir otro usuario vuelva abrir la aplicación.")
        root.destroy()
        return
    
    conn.close()
    actualizar_usuarios()
    messagebox.showinfo("Éxito", "Usuario eliminado correctamente")

root = tk.Tk()
root.title("Inventory")
root.geometry("800x600")

notebook = ttk.Notebook(root)

style = ttk.Style()
style.configure("TNotebook", background="#AED6F1", borderwidth=0)
style.configure("TNotebook.Tab", padding=[10, 5], font=("Arial", 12, "bold"))
style.map("TNotebook.Tab", background=[("selected", "#D6EAF8")], foreground=[("selected", "black")])

frame_productos = ttk.Frame(notebook, style="TFrame")
frame_ventas = ttk.Frame(notebook, style="TFrame")
frame_registro = ttk.Frame(notebook, style="TFrame")
frame_configuracion = ttk.Frame(notebook, style="TFrame")

notebook.add(frame_productos, text="Inventario")
notebook.add(frame_ventas, text="Ventas")
notebook.pack(expand=True, fill="both")

frame_contenedor = tk.Frame(frame_productos, bg="#AED6F1")
frame_contenedor.pack(fill="both", expand=True, padx=20, pady=20)

frame_form = tk.Frame(frame_contenedor, bg="#AED6F1")
frame_form.pack(side="left", padx=20, pady=20)

tk.Label(frame_form, text="Nombre", font=("Arial", 10, "bold"), bg="#AED6F1").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_nombre = tk.Entry(frame_form, width=20)
entry_nombre.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_form, text="Categoría", font=("Arial", 10, "bold"), bg="#AED6F1").grid(row=0, column=2, padx=5, pady=5, sticky="e")
entry_categoria = tk.Entry(frame_form, width=20)
entry_categoria.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_form, text="Precio", font=("Arial", 10, "bold"), bg="#AED6F1").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_precio = tk.Entry(frame_form, width=20)
entry_precio.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_form, text="Proveedor", font=("Arial", 10, "bold"), bg="#AED6F1").grid(row=1, column=2, padx=5, pady=5, sticky="e")
entry_proveedor = tk.Entry(frame_form, width=20)
entry_proveedor.grid(row=1, column=3, padx=5, pady=5)

tk.Label(frame_form, text="Cantidad", font=("Arial", 10, "bold"), bg="#AED6F1").grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_cantidad = tk.Entry(frame_form, width=20)
entry_cantidad.grid(row=2, column=1, padx=5, pady=5)

entries = [entry_nombre, entry_categoria, entry_precio, entry_cantidad, entry_proveedor]

style.configure("TButton", font=("Arial", 10, "bold"), padding=5)
style.configure("Agregar.TButton", background="#2980B9", foreground="black")
style.configure("Eliminar.TButton", background="#2980B9", foreground="black")
style.configure("PDF.TButton", background="#2980B9", foreground="black")
style.configure("Excel.TButton", background="#2980B9", foreground="black")

frame_botones_form = tk.Frame(frame_form, bg="#AED6F1")
frame_botones_form.grid(row=3, column=0, columnspan=4, pady=15)

btn_agregar = ttk.Button(frame_botones_form, text="Agregar Producto", command=agregar_producto, style="Agregar.TButton")
btn_agregar.pack(side="left", padx=5)

btn_eliminar = ttk.Button(frame_botones_form, text="Eliminar Producto", command=eliminar_producto, style="Eliminar.TButton")
btn_eliminar.pack(side="left", padx=5)

frame_logo = tk.Frame(frame_contenedor, bg="#AED6F1")
frame_logo.pack(side="right", padx=20, pady=1)

imagen = Image.open("assets/splash.png")
imagen = imagen.resize((200, 200), Image.LANCZOS)
imagen_tk = ImageTk.PhotoImage(imagen)

label_imagen = tk.Label(frame_logo, image=imagen_tk, bg="#AED6F1")
label_imagen.pack()

frame_botones = tk.Frame(frame_productos)
frame_botones.pack(pady=0)

btn_generar_pdf_inventario = ttk.Button(frame_botones, text="Generar PDF", command=generar_pdf_inventario, style="PDF.TButton")
btn_generar_pdf_inventario.pack(side="left", padx=5)

btn_exportar_inventario_excel = ttk.Button(frame_botones, text="Exportar a Excel", command=exportar_inventario_excel, style="Excel.TButton")
btn_exportar_inventario_excel.pack(side="left", padx=5)

columns_productos = ("Ítem", "Nombre", "Categoría", "Precio", "Cantidad", "Proveedor")
tabla_productos = ttk.Treeview(frame_productos, columns=columns_productos, show="headings", height=10)
for col in columns_productos:
    tabla_productos.heading(col, text=col, anchor="center")
    tabla_productos.column(col, width=120, anchor="center")

tabla_productos.pack(expand=True, fill="both", padx=10, pady=10)
tabla_productos.configure(selectmode="extended")

frame_contenedor_venta = tk.Frame(frame_ventas, bg="#AED6F1")
frame_contenedor_venta.pack(fill="both", expand=True, padx=20, pady=20)

frame_venta_form = tk.Frame(frame_contenedor_venta, bg="#AED6F1")
frame_venta_form.pack(side="left", expand=True, padx=50, pady=50)

labels_venta = ["Nombre del Producto o Ítem", "Cantidad Vendida", "Nombre del Cliente", "Apellido del Cliente", "Celular (opcional)"]
entries_venta = []

for i, texto in enumerate(labels_venta):
    tk.Label(frame_venta_form, text=texto, font=("Arial", 10, "bold"), bg="#AED6F1").grid(row=i, column=0, padx=5, pady=8, sticky="e")
    entry = tk.Entry(frame_venta_form, width=30)
    entry.grid(row=i, column=1, padx=5, pady=8)
    entries_venta.append(entry)

entry_nombre_venta, entry_cantidad_venta, entry_nombre_cliente, entry_apellido_cliente, entry_celular_cliente = entries_venta

btn_vender = ttk.Button(frame_venta_form, text="Registrar Venta", command=registrar_venta, style="Agregar.TButton")
btn_vender.grid(row=len(labels_venta), column=0, columnspan=2, pady=20)

frame_imagen_venta = tk.Frame(frame_contenedor_venta, bg="#AED6F1")
frame_imagen_venta.pack(side="right", padx=20, pady=20)

img_venta = tk.PhotoImage(file="assets/venta.png")
label_imagen = tk.Label(frame_imagen_venta, image=img_venta, bg="#AED6F1")
label_imagen.pack()

frame_estadisticas = tk.Frame(notebook, bg='#AED6F1')
notebook.add(frame_estadisticas, text="Registro Diario")
frame_estadisticas.configure(bg='#AED6F1')

frame_etiquetas = tk.Frame(frame_estadisticas, bg='#AED6F1')
frame_etiquetas.pack(pady=10)

label_total_ventas = tk.Label(frame_etiquetas, text="Total Ventas: $ 0 COP", font=("Arial", 12), bg='#AED6F1')
label_total_ventas.pack(pady=2)

label_total_gastos = tk.Label(frame_etiquetas, text="Total Gastos: $ 0 COP", font=("Arial", 12), bg='#AED6F1')
label_total_gastos.pack(pady=2)

label_ganancias = tk.Label(frame_etiquetas, text="Ganancia Neta: $ 0 COP", font=("Arial", 12), bg='#AED6F1')
label_ganancias.pack(pady=2)

btn_calcular_totales = ttk.Button(frame_estadisticas, text="Actualizar Totales", command=calcular_ventas)
btn_calcular_totales.pack(pady=10)

frame_botones = tk.Frame(frame_estadisticas, bg='#AED6F1')
frame_botones.pack(pady=5)

btn_generar_pdf = ttk.Button(frame_botones, text="Generar PDF", command=generar_pdf)
btn_generar_pdf.grid(row=0, column=0, padx=10)

btn_exportar_ventas_excel = ttk.Button(frame_botones, text="Generar EXCEL", command=exportar_ventas_excel)
btn_exportar_ventas_excel.grid(row=0, column=1, padx=10)

btn_eliminar_ventas = ttk.Button(frame_botones, text="Eliminar Historial de Ventas", command=eliminar_historial_ventas)
btn_eliminar_ventas.grid(row=0, column=2, padx=10)

columns_ventas = ("Ítem", "Nombre", "Cantidad Vendida", "Total", "Fecha")
tabla_ventas = ttk.Treeview(frame_estadisticas, columns=columns_ventas, show="headings")
for col in columns_ventas:
    tabla_ventas.heading(col, text=col, anchor="center")
    tabla_ventas.column(col, width=150, anchor="center")

tabla_ventas.pack(expand=True, fill="both", padx=10, pady=10)

actualizar_lista()

frame_configuracion = tk.Frame(notebook, bg='#AED6F1')
notebook.add(frame_configuracion, text="Configuración")

tk.Label(frame_configuracion, text="Usuarios Registrados", font=("Arial", 14, "bold"), bg='#AED6F1').pack(pady=10)

tabla_usuarios = ttk.Treeview(frame_configuracion, columns=("ID", "Usuario"), show="headings")
tabla_usuarios.heading("ID", text="Ítem")
tabla_usuarios.heading("Usuario", text="Usuario")
tabla_usuarios.pack(padx=10, pady=10)

tabla_usuarios.column("ID", anchor="center")
tabla_usuarios.column("Usuario", anchor="center")

btn_eliminar_usuario = ttk.Button(frame_configuracion, text="Eliminar Usuario Seleccionado", command=eliminar_usuario)
btn_eliminar_usuario.pack(pady=10)

actualizar_usuarios()
root.mainloop()