import sqlite3
from datetime import datetime

def crear_base_datos():
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

    conexion2 = sqlite3.connect("inventario.db")
    cursor = conexion2.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL,
            proveedor TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad_vendida INTEGER NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL
        )
    ''')
    conexion2.commit()
    conexion2.close()
    print("Base de datos creada correctamente.")

def agregar_producto(nombre, categoria, precio, cantidad, proveedor):
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO productos (nombre, categoria, precio, cantidad, proveedor)
        VALUES (?, ?, ?, ?, ?)
    ''', (nombre, categoria, precio, cantidad, proveedor))
    conexion.commit()
    conexion.close()
    print("Producto agregado correctamente.")

def editar_producto(id_producto, nombre, categoria, precio, cantidad, proveedor):
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()
    cursor.execute('''
        UPDATE productos
        SET nombre = ?, categoria = ?, precio = ?, cantidad = ?, proveedor = ?
        WHERE id = ?
    ''', (nombre, categoria, precio, cantidad, proveedor, id_producto))
    conexion.commit()
    conexion.close()
    print("Producto editado correctamente.")

def eliminar_producto(id_producto):
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()
    cursor.execute('''
        DELETE FROM productos WHERE id = ?
    ''', (id_producto,))
    conexion.commit()
    conexion.close()
    print("Producto eliminado correctamente.")

def listar_productos():
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conexion.close()
    return productos

def registrar_venta(producto_id, cantidad_vendida):
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()
    
    cursor.execute("SELECT precio, cantidad FROM productos WHERE id = ?", (producto_id,))
    producto = cursor.fetchone()
    if not producto or producto[1] < cantidad_vendida:
        print("Error: Producto no disponible o cantidad insuficiente.")
        return
    
    precio_unitario = producto[0]
    total = precio_unitario * cantidad_vendida
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO ventas (fecha, producto_id, cantidad_vendida, total)
        VALUES (?, ?, ?, ?)
    ''', (fecha, producto_id, cantidad_vendida, total))
    
    cursor.execute('''
        UPDATE productos
        SET cantidad = cantidad - ?
        WHERE id = ?
    ''', (cantidad_vendida, producto_id))
    
    conexion.commit()
    conexion.close()
    print("Venta registrada correctamente.")

def registrar_gasto(descripcion, monto):
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO gastos (fecha, descripcion, monto)
        VALUES (?, ?, ?)
    ''', (fecha, descripcion, monto))
    conexion.commit()
    conexion.close()
    print("Gasto registrado correctamente.")

def calcular_ganancias():
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()
    
    cursor.execute("SELECT SUM(total) FROM ventas")
    ingresos = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(monto) FROM gastos")
    egresos = cursor.fetchone()[0] or 0
    
    ganancias = ingresos - egresos
    conexion.close()
    return ganancias

def resumen_diario():
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("SELECT SUM(total) FROM ventas WHERE fecha LIKE ?", (fecha_actual + "%",))
    ingresos = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(monto) FROM gastos WHERE fecha LIKE ?", (fecha_actual + "%",))
    egresos = cursor.fetchone()[0] or 0
    
    ganancias = ingresos - egresos
    conexion.close()
    
    print(f"Resumen del día {fecha_actual}:")
    print(f"Total ganado: {ingresos}")
    print(f"Total gastado: {egresos}")
    print(f"Ganancia neta: {ganancias}")

if __name__ == "__main__":
    crear_base_datos()