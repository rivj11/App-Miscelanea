# 📦 Inventory App

Una aplicación de escritorio para gestionar inventario, registrar ventas, generar facturas en PDF y hacer seguimiento de ganancias y gastos. Desarrollada en Python con interfaz gráfica usando Tkinter y base de datos SQLite.

---

## 🧩 Características

- 📋 Gestión de productos en inventario (agregar, editar, eliminar)
- 💵 Registro de ventas y cálculo de ganancias
- 🧾 Generación automática de facturas en PDF
- 📊 Reporte de ventas diarias
- 🔐 Autenticación de usuarios con control de acceso
- 🛠️ Panel de configuración con opciones administrativas
- 💬 Interfaz amigable y fácil de usar

---

## 🚀 Cómo iniciar

### 1. Clonar el repositorio
```bash
git clone https://github.com/tuusuario/inventory-app.git
cd inventory-app

2. Instalar dependencias
Asegúrate de tener Python 3.11+ instalado, luego ejecuta:
pip install -r requirements.txt

Si no tienes un archivo requirements.txt, las principales dependencias son:
pip install pillow reportlab

3. Crear la base de datos
python database/setup_db.py

4. Iniciar la aplicación
python main.py

🧑‍💻 Tecnologías utilizadas
Python 3.11

Tkinter (GUI)

SQLite (base de datos local)

Pillow (para manejo de imágenes)

ReportLab (generación de PDF)

🔐 Clave de Administrador
Algunas funciones sensibles como eliminar usuarios, borrar historial de ventas o eliminar productos requieren autenticación del administrador mediante clave.

Clave predeterminada: clave123
(Se puede cambiar fácilmente desde el código fuente
