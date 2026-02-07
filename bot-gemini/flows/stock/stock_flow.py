import logging
import flows.state as state
from utils import get_products, format_stock

def handle_view_stock(cfg, sender, send_msg):
    state.set_state(sender, {"flow": "stock", "step": "view"})
    
    productos = chat_logic.get_products()
    respuesta_formateada = chat_logic.format_stock(productos)
    
    message_body = f"📦 *Stock Actual* 📊\n\n{respuesta_formateada}"
    
    if state.get_previous_state(sender):
        message_body += "\n\n0️⃣ Volver" # Add "Volver" option
        
    send_msg(cfg, sender, message_body)
    return True

def handle_input(cfg, sender, text, send_msg):
    # This flow might not need complex input handling beyond "volver"
    # which is handled by engine.py
    send_msg(cfg, sender, "Por favor, selecciona una opción válida o escribe '0' para volver.")
    return True
