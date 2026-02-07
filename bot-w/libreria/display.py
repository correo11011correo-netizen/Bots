from .utils import format_timestamp
import time

def display_incoming_message(msg):
    """
    Muestra un resumen formateado de un nuevo mensaje entrante.

    Args:
        msg (dict): El diccionario del mensaje recibido de la API de WhatsApp.
    """
    sender = msg.get("from", "Desconocido")
    text_body = "Mensaje sin contenido"
    if msg.get("type") == "text":
        text_body = msg.get("text", {}).get("body", text_body)

    timestamp = format_timestamp(msg.get("timestamp", time.time()))

    print("\n--- 📩 Nuevo Mensaje Recibido ---")
    print(f"  ✅ De: {sender}")
    print(f"  💬 Mensaje: {text_body}")
    print(f"  ⏰ Hora: {timestamp}")
    print("---------------------------------")

def display_status_update(status_data):
    """
    Muestra un resumen formateado de una actualización de estado del mensaje.

    Args:
        status_data (dict): El diccionario de estado recibido de la API de WhatsApp.
    """
    recipient = status_data.get("recipient_id", "Desconocido")
    status = status_data.get("status", "desconocido").capitalize()
    timestamp = format_timestamp(status_data.get("timestamp", time.time()))

    status_icons = {
        'Sent': '📤',
        'Delivered': '📥',
        'Read': '👀',
        'Failed': '❌'
    }
    icon = status_icons.get(status, '❓')

    print(f"\n--- {icon} Actualización de Estado ---")
    print(f"  [{timestamp}] Para: {recipient}")
    print(f"  Estado: {status}")
    print("---------------------------------")
