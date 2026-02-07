import re
import google.generativeai as genai
import json
import logging
import os
from utils import db_connect, init_db, add_product, update_product, search_product, get_products, limpiar_texto, format_stock, _format_details, _execute_dynamic_db_operation

# Configuración del logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración de Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    logging.error("GEMINI_API_KEY no encontrada en las variables de entorno.")
    raise ValueError("GEMINI_API_KEY no configurada.")

# Instrucción del sistema para el modelo
DEFAULT_SYSTEM_INSTRUCTION = """
Eres un asistente de gestión de stock. Tu tarea es interpretar las solicitudes del usuario para agregar, actualizar o buscar productos en una base de datos.
Siempre debes responder con un objeto JSON que contenga las siguientes claves:
- "action": "agregar", "editar", "buscar", "dynamic_db_op", "desconocido".
- "product": (string) El nombre del producto.
- "price": (float, opcional) El precio del producto.
- "stock": (int, opcional) La cantidad en stock del producto.
- "details": (object, opcional) Un objeto JSON con atributos dinámicos (ej: {"ram": "8GB", "memoria_gb": 256, "color": "azul"}).
- "operation": (string, opcional) Para "dynamic_db_op", la operación a realizar (ej: "change_price_percentage").
- "value": (float, opcional) Para "dynamic_db_op", el valor de la operación (ej: 10 para 10%).
- "criteria": (string, opcional) Para "dynamic_db_op", el criterio de selección (ej: "all", "category_smartphones").

Ejemplos de interacción:
- Usuario: "Agregar iPhone 15 por 1200$ con 50 unidades, 8GB RAM, 256GB de memoria y color azul"
  Respuesta JSON: `{"action": "agregar", "product": "iPhone 15", "price": 1200.0, "stock": 50, "details": {"ram": "8GB", "memoria_gb": 256, "color": "azul"}}`
- Usuario: "Agrega Samsung S22 10000$, con 12GB de RAM"
  Respuesta JSON: `{"action": "agregar", "product": "Samsung S22", "price": 10000.0, "stock": 1, "details": {"ram": "12GB"}}`
- Usuario: "Actualizar precio de Samsung S24 a 950 y color a negro"
  Respuesta JSON: `{"action": "editar", "product": "Samsung S24", "price": 950.0, "details": {"color": "negro"}}`
- Usuario: "Cambiar stock de MacBook Air a 25"
  Respuesta JSON: `{"action": "editar", "product": "MacBook Air", "stock": 25}`
- Usuario: "Buscar todos los Motorola"
  Respuesta JSON: `{"action": "buscar", "product": "Motorola"}`
- Usuario: "Quiero cambiar el precio de todos los productos un 10%"
  Respuesta JSON: `{"action": "dynamic_db_op", "operation": "change_price_percentage", "criteria": "all", "value": 10}`
- Usuario: "Agrega 1% a todo el stock"
  Respuesta JSON: `{"action": "dynamic_db_op", "operation": "change_stock_percentage", "criteria": "all", "value": 1}`
- Usuario: "Que hay de nuevo"
  Respuesta JSON: `{"action": "desconocido"}`

Si la acción es "editar", el campo "product" es obligatorio. Los campos "price", "stock" o "details" son opcionales, pero al menos uno debe estar presente.
Si la acción es "agregar", los campos "product" y "price" son obligatorios. Si el "stock" no se especifica, asume un valor de 1. El campo "details" es opcional.
Si la acción es "buscar", el campo "product" es obligatorio.
Si la acción es "dynamic_db_op", los campos "operation", "criteria" y "value" son obligatorios.

Asegúrate de que el nombre del producto siempre esté capitalizado correctamente (primera letra de cada palabra en mayúscula).
Extrae los números con decimales como floats para el precio y como enteros para el stock.
Ignora cualquier información irrelevante y céntrate solo en los datos del producto y la acción.
"""

genai.configure(api_key=API_KEY)
# Usando gemini-1.5-flash como se sugirió
generation_config = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
}
model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config, system_instruction=DEFAULT_SYSTEM_INSTRUCTION)

def interpretar(text, state=None):
    # Comandos simples que no requieren IA
    text_limpio = limpiar_texto(text)

    if text_limpio in ["menu", "menú"]:
        return {"accion": "menu", "respuesta": "📋 Menú principal:\n1️⃣ Sorteos\n2️⃣ Préstamos\n3️⃣ Referidos\n4️⃣ Más servicios\n5️⃣ Contacto\n6️⃣ Chat Gemini", "state": None}

    if text_limpio in ["editar", "edit"]:
        return {"accion": "ayuda_editar", "respuesta": "✏️ Para editar usa frases como:\n- 'Cambiar precio iPhone 15 a 1300'\n- 'Actualizar stock Samsung S24 a 20'", "state": state}

    if text_limpio in ["agrega stock", "agregar stock"]:
        productos = get_products()
        respuesta = format_stock(productos)
        return {"accion": "consultar", "respuesta": "📦 Elige producto para editar stock:\n" + respuesta, "state": state}

    if any(palabra in text_limpio for palabra in ["salir", "chau", "adios", "terminar", "cerrar"]):
        return {"accion": "salir", "respuesta": "👋 Terminamos el chat de base de datos.", "state": None}

    if any(palabra in text_limpio for palabra in ["hola", "buenas", "que tal", "hi", "saludos"]):
        return {"accion": "saludo", "respuesta": "✨ Bienvenido al 📦 *StockBot* ✨\nAhora puedes usar lenguaje natural para:\n🔍 'Ver stock'\n➕ 'Agregar Samsung A55 con precio 450 y 30 unidades'\n✏️ 'Actualizar el precio del iPhone 15 a 1300'\n📱 'Buscar Motorola'\n❌ 'salir' para terminar.", "state": state}

    try:
        logging.info(f"Enviando a Gemini: {text}")
        response = model.generate_content(
            contents=[{
                "role": "user",
                "parts": [{"text": text}]
            }]
        )
        
        logging.info(f"Respuesta cruda de Gemini: {response.text}")
        
        # Intentar cargar la respuesta como JSON
        try:
            # First, try to extract JSON from markdown code block
            match = re.search(r"```json\n(.*?)```", response.text, re.DOTALL)
            if match:
                json_string = match.group(1)
            else:
                json_string = response.text # Assume pure JSON if no markdown block

            gemini_output = json.loads(json_string)
        except json.JSONDecodeError:
            logging.error(f"Gemini no devolvió un JSON válido: {response.text}")
            return {"accion": "desconocido", "respuesta": "⚠️ No pude entender tu solicitud. Intenta ser más claro.", "state": state}

        action = gemini_output.get("action")
        product_name = gemini_output.get("product")
        price = gemini_output.get("price")
        stock = gemini_output.get("stock")
        details = gemini_output.get("details") # New: Extract details

        if action == "agregar":
            if product_name and price is not None and stock is not None:
                details_json_str = json.dumps(details, ensure_ascii=False) if details else '{}'
                if add_product(product_name, price, stock, details_json_str):
                    details_display = _format_details(details)
                    return {"accion": "agregar", "respuesta": f"✅ Agregado: *{product_name}*\n💲{price} | 📦{stock}{details_display}", "state": None}
                else:
                    return {"accion": "error", "respuesta": f"❌ Error: El producto *{product_name}* ya existe o hubo un problema al agregarlo.", "state": state}
            else:
                return {"accion": "error", "respuesta": "⚠️ Para agregar un producto, necesito el nombre, precio y stock. Ejemplo: 'Agregar iPhone 15 por 1200 con 50 unidades, 8GB RAM, 256GB de memoria y color azul'", "state": state}

        elif action == "editar":
            if product_name and (price is not None or stock is not None or details is not None):
                if update_product(product_name, price, stock, details):
                    details_display = _format_details(details)
                    return {"accion": "editar", "respuesta": f"✅ Actualizado: *{product_name}* (Precio: {price if price is not None else 'sin cambio'}, Stock: {stock if stock is not None else 'sin cambio'}){details_display}", "state": None}
                else:
                    return {"accion": "error", "respuesta": f"❌ Error: No se pudo encontrar o actualizar el producto *{product_name}*.", "state": state}
            else:
                return {"accion": "error", "respuesta": "⚠️ Para editar, necesito el nombre del producto y al menos un cambio (precio, stock o detalles). Ejemplo: 'Cambiar precio iPhone 15 a 1300'", "state": state}

        elif action == "buscar":
            if product_name:
                productos = search_product(product_name)
                respuesta_formateada = format_stock(productos)
                if productos:
                    return {"accion": "consultar", "respuesta": f"🔎 Resultados para '{product_name}':\n{respuesta_formateada}", "state": state}
                else:
                    return {"accion": "consultar", "respuesta": f"🤷 No se encontraron productos que coincidan con '{product_name}'.", "state": state}
            else:
                return {"accion": "error", "respuesta": "⚠️ Para buscar, necesito un nombre de producto. Ejemplo: 'Buscar Samsung'", "state": state}
        
        elif action == "dynamic_db_op":
            operation = gemini_output.get("operation")
            criteria = gemini_output.get("criteria")
            value = gemini_output.get("value")

            if operation == "change_price_percentage" and criteria == "all" and value is not None:
                if _execute_dynamic_db_operation(operation, criteria, value):
                    return {"accion": "dynamic_db_op", "respuesta": f"✅ Precios actualizados en un {value}% para todos los productos.", "state": None}
                else:
                    return {"accion": "error", "respuesta": "❌ Error al actualizar los precios.", "state": state}
            elif operation == "change_stock_percentage" and criteria == "all" and value is not None:
                if _execute_dynamic_db_operation(operation, criteria, value):
                    return {"accion": "dynamic_db_op", "respuesta": f"✅ Stock actualizado en un {value}% para todos los productos.", "state": None}
                else:
                    return {"accion": "error", "respuesta": "❌ Error al actualizar el stock.", "state": state}
            else:
                return {"accion": "error", "respuesta": "⚠️ Operación dinámica no reconocida o parámetros incompletos.", "state": state}

        else:
            return {"accion": "desconocido", "respuesta": "⚠️ No entendí tu intención. Intenta con 'agregar', 'editar', 'buscar' o 'ver stock'.", "state": state}

    except Exception as e:
        logging.error(f"Error al interactuar con Gemini o procesar la respuesta: {e}")
        return {"accion": "error", "respuesta": "❌ Ocurrió un error inesperado al procesar tu solicitud. Intenta de nuevo.", "state": state}