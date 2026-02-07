import logging
import flows.state as state
from flows.gemini import chat_logic

def handle_gemini_chat(cfg, sender, send_msg):
    # Activar modo chat Gemini
    state.set_state(sender, {"flow": "gemini", "step": "chat"})
    chat_logic.init_db()
    
    message_body = (
        "📦 *Control de Stock* 📊\n"
        "¡Hola! Soy tu asistente de stock para tareas complejas. Puedes:\n"
        "➕ *Agregar productos*\n"
        "✏️ *Editar productos*\n"
        "🔎 *Buscar productos*\n"
        "📈 *Actualizaciones masivas*\n"
        "👋 Escribe 'salir' para finalizar."
    )
    
    if state.get_previous_state(sender):
        message_body += "\n0️⃣ Volver" # Add "Volver" option
        
    send_msg(cfg, sender, message_body)

def handle_input(cfg, sender, text, send_msg):
    current_state = state.get(sender)
    result = chat_logic.interpretar(text, current_state)

    accion = result["accion"]
    respuesta = result["respuesta"]
    new_state = result.get("state")

    # Mantener siempre el flujo Gemini activo, salvo que el usuario diga "salir"
    if accion == "salir":
        state.clear(sender)
    else:
        state.set_state(sender, {"flow": "gemini", **(new_state or {})})

    send_msg(cfg, sender, respuesta)
    return True
