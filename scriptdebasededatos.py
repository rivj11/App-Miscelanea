import sqlite3
import time

def agregar_producto(nombre, categoria, precio, cantidad, proveedor):
    conexion = sqlite3.connect("inventario.db")
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO productos (nombre, categoria, precio, cantidad, proveedor)
        VALUES (?, ?, ?, ?, ?)
    ''', (nombre, categoria, precio, cantidad, proveedor))
    conexion.commit()
    conexion.close()
    print(f"Producto '{nombre}' agregado correctamente.")

def agregar_productos_miscelanea():
    productos = [
        # Papelería
        ("Lapicero", "Papelería", 1500, 50, "Proveedor A"),
        ("Cuaderno", "Papelería", 3000, 30, "Proveedor B"),
        ("Borrador", "Papelería", 1000, 100, "Proveedor A"),
        ("Regla", "Papelería", 1200, 40, "Proveedor C"),
        ("Papel bond", "Papelería", 2500, 60, "Proveedor D"),

        # Alimentos
        ("Arroz", "Alimentos", 4000, 100, "Proveedor E"),
        ("Azúcar", "Alimentos", 3500, 80, "Proveedor F"),
        ("Galletas", "Alimentos", 2500, 200, "Proveedor G"),
        ("Cereal", "Alimentos", 5500, 150, "Proveedor H"),
        ("Café", "Alimentos", 7000, 120, "Proveedor I"),

        # Bebidas
        ("Coca-Cola", "Bebidas", 3000, 50, "Proveedor J"),
        ("Agua", "Bebidas", 1000, 200, "Proveedor K"),
        ("Jugo de naranja", "Bebidas", 3500, 80, "Proveedor L"),
        ("Cerveza", "Bebidas", 4000, 40, "Proveedor M"),
        ("Gaseosa de cola", "Bebidas", 2500, 100, "Proveedor N"),

        # Productos de limpieza
        ("Detergente", "Limpieza", 3000, 70, "Proveedor O"),
        ("Jabón líquido", "Limpieza", 2000, 100, "Proveedor P"),
        ("Papel higiénico", "Limpieza", 1500, 120, "Proveedor Q"),
        ("Desinfectante", "Limpieza", 4000, 50, "Proveedor R"),
        ("Esponjas", "Limpieza", 800, 150, "Proveedor S"),

        # Otros
        ("Chicles", "Otros", 1000, 200, "Proveedor T"),
        ("Lentes de sol", "Otros", 12000, 30, "Proveedor U"),
        ("Cepillo de dientes", "Otros", 1500, 80, "Proveedor V"),
        ("Pasta de dientes", "Otros", 2000, 60, "Proveedor W"),
        ("Baterías", "Otros", 2500, 40, "Proveedor X"),
    ]
    
    for i, producto in enumerate(productos, start=1):
        print(f"Agregando producto {i}: {producto[0]}...")
        agregar_producto(*producto)
        time.sleep(1)  # Pausa de 3 segundos antes de agregar el siguiente producto

if __name__ == "__main__":
    agregar_productos_miscelanea()
