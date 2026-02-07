import flows.state as state
from utils import add_product, get_products, update_product, format_stock, delete_product, _format_details
import json
import logging
import re

def handle_db_control(cfg, sender, send_msg):
    state.set_state(sender, {"flow": "db_control", "step": "menu"})
    message_body = (
        "🗄️ *Control de Base de Datos Local* 📊\n"
        "Puedes administrar tus productos con los siguientes comandos:\n"
        "➕ *agregar*: Para añadir un nuevo producto. Ejemplo: 'agregar nombre=Producto1 precio=100 stock=10 detalles={'color':'red'}'\n"
        "✏️ *editar*: Para modificar un producto existente. Ejemplo: 'editar id=1 precio=120 stock=15 detalles={'size':'M'}'\n"
        "🗑️ *eliminar*: Para quitar un producto. Ejemplo: 'eliminar id=1'\n"
        "🔎 *buscar*: Para encontrar productos por nombre. Ejemplo: 'buscar nombre=Producto'\n"
        "📜 *listar*: Para ver todos los productos.\n"
        "0️⃣ *volver*: Para regresar al menú anterior."
    )
    send_msg(cfg, sender, message_body)

def handle_input(cfg, sender, text, send_msg):
    current_state = state.get(sender)
    if current_state and current_state.get("flow") != "db_control":
        return False

    text_lower = text.lower().strip()

    if text_lower == "listar":
        productos = get_products()
        respuesta_formateada = format_stock(productos)
        send_msg(cfg, sender, f"📜 *Listado de Productos*:\n{respuesta_formateada}")
        return True
    
    elif text_lower.startswith("agregar"):
        try:
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                raise ValueError("Faltan parámetros para agregar.")
            
            args_str = parts[1]
            args = parse_arguments(args_str)
            
            nombre = args.get("nombre")
            precio = float(args["precio"]) if "precio" in args else None
            stock = int(args["stock"]) if "stock" in args else 1
            details_str = args.get("detalles", '{}')
            details_dict = json.loads(details_str)

            if not nombre or precio is None:
                raise ValueError("Nombre y precio son obligatorios para agregar.")

            if add_product(nombre, precio, stock, json.dumps(details_dict, ensure_ascii=False)):
                details_display = _format_details(details_dict)
                send_msg(cfg, sender, f"✅ Agregado: *{nombre}*\n💲{precio} | 📦{stock}{details_display}")
            else:
                send_msg(cfg, sender, f"❌ Error: El producto *{nombre}* ya existe o hubo un problema al agregarlo.")
        except (ValueError, json.JSONDecodeError) as e:
            send_msg(cfg, sender, f"⚠️ Error al agregar producto: {e}. Formato: 'agregar nombre=Producto1 precio=100 stock=10 detalles={{'color':'red'}}'")
        return True

    elif text_lower.startswith("editar"):
        try:
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                raise ValueError("Faltan parámetros para editar.")
            
            args_str = parts[1]
            args = parse_arguments(args_str)

            product_id = int(args["id"]) if "id" in args else None
            nombre_to_find = None
            if product_id:
                productos = get_products()
                for pid, pnombre, _, _, _ in productos:
                    if pid == product_id:
                        nombre_to_find = pnombre
                        break
                if not nombre_to_find:
                    raise ValueError(f"No se encontró producto con ID {product_id}")
            else:
                send_msg(cfg, sender, "⚠️ Para editar necesito el ID del producto. Ejemplo: 'editar id=1 precio=120'")
                return True

            precio = float(args["precio"]) if "precio" in args else None
            stock = int(args["stock"]) if "stock" in args else None
            details_str = args.get("detalles")
            details_dict = json.loads(details_str) if details_str else None

            if precio is None and stock is None and details_dict is None:
                raise ValueError("Al menos un campo (precio, stock o detalles) debe ser proporcionado para editar.")

            if update_product(nombre_to_find, precio, stock, details_dict):
                details_display = _format_details(details_dict if details_dict else {})
                send_msg(cfg, sender, f"✅ Actualizado: *{nombre_to_find}* (Precio: {precio if precio is not None else 'sin cambio'}, Stock: {stock if stock is not None else 'sin cambio'}){details_display}")
            else:
                send_msg(cfg, sender, f"❌ Error: No se pudo encontrar o actualizar el producto *{nombre_to_find}*.")
        except (ValueError, json.JSONDecodeError) as e:
            send_msg(cfg, sender, f"⚠️ Error al editar producto: {e}. Formato: 'editar id=1 precio=120 stock=15 detalles={{'size':'M'}}'")
        return True

    elif text_lower.startswith("eliminar"):
        try:
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                raise ValueError("Falta el ID del producto a eliminar.")
            
            args_str = parts[1]
            args = parse_arguments(args_str)
            product_id = int(args["id"]) if "id" in args else None

            if not product_id:
                raise ValueError("ID del producto es obligatorio para eliminar.")

            if delete_product(product_id):
                send_msg(cfg, sender, f"🗑️ Producto con ID {product_id} eliminado.")
            else:
                send_msg(cfg, sender, f"❌ Error: No se encontró el producto con ID {product_id}.")
        except ValueError as e:
            send_msg(cfg, sender, f"⚠️ Error al eliminar producto: {e}. Formato: 'eliminar id=1'")
        return True

    elif text_lower.startswith("buscar"):
        try:
            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                raise ValueError("Falta el nombre para buscar.")
            
            args_str = parts[1]
            args = parse_arguments(args_str)
            nombre = args.get("nombre")

            if not nombre:
                raise ValueError("Nombre del producto es obligatorio para buscar.")

            productos = search_product(nombre)
            respuesta_formateada = format_stock(productos)
            if productos:
                send_msg(cfg, sender, f"🔎 Resultados para '{nombre}':\n{respuesta_formateada}")
            else:
                send_msg(cfg, sender, f"🤷 No se encontraron productos que coincidan con '{nombre}'.")
        except ValueError as e:
            send_msg(cfg, sender, f"⚠️ Error al buscar producto: {e}. Formato: 'buscar nombre=Producto'")
        return True

    else:
        send_msg(cfg, sender, "⚠️ Comando no reconocido. Intenta con 'agregar', 'editar', 'eliminar', 'buscar', 'listar' o '0' para volver.")
        return True

def parse_arguments(arg_string):
    args = {}
    # Regex to capture key=value pairs, handling quoted strings for values
    # It also handles key='{"json":"string"}'
    pattern = re.compile(r'(\w+)=(?:\"(.*?)\"|\'(.*?)\'|(\S+))')
    
    for match in pattern.finditer(arg_string):
        key = match.group(1)
        # Prioritize double-quoted, then single-quoted, then unquoted
        value = match.group(2) or match.group(3) or match.group(4)
        args[key] = value
    return args
