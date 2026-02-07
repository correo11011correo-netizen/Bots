import datetime
import logging
import sys
import sqlite3
import os
import json
import re
import unicodedata

# Path to the SQLite database
DB_PATH = os.path.join("data", "stock.db")

def setup_logging():
    # Obtener el logger raíz
    logger = logging.getLogger()
    logger.setLevel(logging.INFO) # O el nivel que prefieras (DEBUG, WARNING, ERROR, CRITICAL)

    # Crear un handler para la consola (stdout)
    handler = logging.StreamHandler(sys.stdout)

    # Definir el formato del log
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    # Añadir el handler al logger, solo si no ha sido añadido ya
    if not logger.handlers:
        logger.addHandler(handler)
    
    logging.info("📝 Logging configurado.")

def log_message(sender, text):
    # Usar el logger para registrar mensajes
    logging.info(f"{sender} -> {text}")

def db_connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE,
        precio REAL,
        stock INTEGER,
        details TEXT DEFAULT '{}'
    )
    """)
    # Add new 'details' column if it doesn't exist (for existing databases)
    try:
        cur.execute("ALTER TABLE productos ADD COLUMN details TEXT DEFAULT '{}'")
    except sqlite3.OperationalError:
        pass # Column already exists
    conn.commit()
    conn.close()

def add_product(nombre, precio, stock, details_json_str='{}'):
    conn = db_connect()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO productos (nombre, precio, stock, details) VALUES (?, ?, ?, ?)", (nombre, precio, stock, details_json_str))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        logging.warning(f"Intento de agregar producto duplicado: {nombre}")
        return False
    finally:
        conn.close()

def update_product(nombre, precio=None, stock=None, details_dict=None):
    conn = db_connect()
    cur = conn.cursor()
    product_id = None
    cur.execute("SELECT id, details FROM productos WHERE nombre = ?", (nombre,))
    result = cur.fetchone()
    if result:
        product_id, current_details_str = result
        current_details = json.loads(current_details_str or '{}')

        updates = []
        params = []
        if precio is not None:
            updates.append("precio=?")
            params.append(precio)
        if stock is not None:
            updates.append("stock=?")
            params.append(stock)
        
        if details_dict is not None:
            # Merge new details with existing ones
            for key, value in details_dict.items():
                if value is None: # Allow removing a detail by setting its value to None
                    if key in current_details:
                        del current_details[key]
                else:
                    current_details[key] = value
            updates.append("details=?")
            params.append(json.dumps(current_details, ensure_ascii=False))
        
        if updates:
            params.append(product_id)
            cur.execute(f"UPDATE productos SET {', '.join(updates)} WHERE id=?", tuple(params))
            conn.commit()
            return True
    conn.close()
    return False

def search_product(nombre):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, precio, stock, details FROM productos WHERE nombre LIKE ?", (f"%{nombre}%",))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_products():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, precio, stock, details FROM productos")
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_product(product_id):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE id=?", (product_id,))
    conn.commit()
    return cur.rowcount > 0 # Returns True if a row was deleted, False otherwise
    conn.close()

def limpiar_texto(text):
    text = text.lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = text.replace("estok", "stock")
    return text

def format_stock(productos):
    if not productos:
        return "📦 No hay productos cargados."

    grouped_products = {}
    phone_brands = ["Iphone", "Samsung", "Motorola"] # Example phone brands

    for id, nombre, precio, stock, details_json_str in productos:
        # Infer brand from the first word of the product name
        brand = nombre.split(" ")[0].title()
        if brand not in grouped_products:
            grouped_products[brand] = []
        
        # Format price as requested (1.000,00 format)
        formatted_precio = f"{precio:,.2f}".replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
        
        # Construct the product line with aligned price and '$' symbol
        # Target width for name + " $ " + price is approximately 32 characters (34 total minus leading "  - ")
        # Ensure 'nombre' itself doesn't exceed a reasonable length for alignment.
        # Max length of the full line including "  - " will be approximately 34 characters.
        # Let's target a total length of 32 characters for the content after "  - "
        content_len_needed = len(formatted_precio) + len("$ ") # Length of "$ " + formatted_precio
        
        # Max length for the name portion
        max_name_len_for_alignment = 32 - content_len_needed
        
        display_name = nombre
        if len(display_name) > max_name_len_for_alignment:
            display_name = display_name[:max_name_len_for_alignment - 3] + "..." # Truncate if too long

        # Calculate padding needed to push price to the right
        padding_needed = max_name_len_for_alignment - len(display_name)
        
        grouped_products[brand].append(f"  - {display_name}{' ' * padding_needed}$ {formatted_precio}")

    salida = []
    for brand, prods in grouped_products.items():
        if brand in phone_brands:
            salida.append(f"─── 📱 {brand} ───")
        else:
            salida.append(f"─── {brand} ───")
        salida.extend(prods)
    
    return "\n".join(salida)

def _format_details(details_dict):
    if not details_dict:
        return ""
    formatted_parts = []
    for key, value in details_dict.items():
        formatted_parts.append(f"{key.replace('_', ' ').title()}: {value}")
    return " | " + ", ".join(formatted_parts)

def _execute_dynamic_db_operation(operation, criteria, value):
    conn = db_connect()
    cur = conn.cursor()
    try:
        if operation == "change_price_percentage" and criteria == "all" and value is not None:
            multiplier = 1 + (float(value) / 100.0)
            cur.execute("UPDATE productos SET precio = precio * ?", (multiplier,))
            conn.commit()
            return True
        elif operation == "change_stock_percentage" and criteria == "all" and value is not None:
            multiplier = 1 + (float(value) / 100.0)
            cur.execute("UPDATE productos SET stock = stock * ?", (multiplier,))
            conn.commit()
            return True
        return False
    except Exception as e:
        logging.error(f"Error executing dynamic DB operation: {e}")
        return False
    finally:
        conn.close()
