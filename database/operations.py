import sqlite3
from datetime import datetime

DB_PATH = 'inventario.db'

def conectar():
    return sqlite3.connect(DB_PATH)

def obtener_productos():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos ORDER BY id")
        return cursor.fetchall()

def agregar_producto(nombre, categoria, precio, cantidad, proveedor):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO productos (nombre, categoria, precio, cantidad, proveedor) VALUES (?, ?, ?, ?, ?)",
                       (nombre, categoria, precio, cantidad, proveedor))
        conn.commit()

def eliminar_producto(id):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (id,))
        conn.commit()

def registrar_venta(producto_id, cantidad, total, fecha=None):
    fecha = fecha or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ventas (producto_id, cantidad_vendida, fecha, total) VALUES (?, ?, ?, ?)",
                       (producto_id, cantidad, fecha, total))
        conn.commit()

def obtener_usuarios():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, usuario FROM usuarios")
        return cursor.fetchall()

def eliminar_usuario(id):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
        conn.commit()