import flows.state as state

def send_welcome_sorteos(cfg, sender, send_msg):
    """
    Envía el mensaje de bienvenida inicial al usuario de WhatsApp.
    """
    mensaje = (
        "👋 Bienvenido al sistema!\n\n"
        "Opciones disponibles:\n"
        "1️⃣ Ver stock\n"
        "2️⃣ WhatsApp info\n"
        "3️⃣ Instagram info\n"
        "4️⃣ Messenger info\n"
        "5️⃣ Submenú de servicios\n"
        "6️⃣ Contacto\n"
        "7️⃣ Control Stock\n"
        "8️⃣ Control de Base de Datos Local\n\n"
        "Escribe el número de la opción que quieras."
    )
    
    if state.get_previous_state(sender):
        mensaje += "\n0️⃣ Volver" # Add "Volver" option
        
    send_msg(cfg, sender, mensaje)
