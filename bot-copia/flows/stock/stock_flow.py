import logging
import flows.state as state
from utils import get_products, format_stock

def handle_view_stock(cfg, sender, send_msg):
    # Guardar estado actual del flujo
    state.set_state(sender, {"flow": "stock", "step": "view"})

    # Obtener productos y formatear stock usando utils
    productos = get_products()
    respuesta_formateada = format_stock(productos)

    # Construir mensaje
    message_body = f"📦 *Stock Actual* 📊\n\n{respuesta_formateada}"

    # Si había un estado previo, agregar opción de volver
    if state.get_previous_state(sender):
        message_body += "\n\n0  Volver"

    # Enviar mensaje al cliente
    send_msg(cfg, sender, message_body)
    return True

def handle_input(cfg, sender, text, send_msg):
    # Manejo básico de input en este flujo
    send_msg(cfg, sender, "Por favor, selecciona una opción válida o escribe '0' para volver.")
    return True
