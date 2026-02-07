from flows.state import get, set_state, get_previous_state
from flows.referidos.referidos_flow import ref_db

def _referidos_activos(user_id):
    return len(ref_db.get(user_id, {"refs": set()})["refs"])

def handle_prestamo(cfg, sender, send_msg):
    set_state(sender, {"flow": "prestamos", "step": "menu"})
    refs = _referidos_activos(sender)

    bloqueado = refs == 0
    msg = (
        "💵 Opciones de préstamos:\n\n"
        "1️⃣ $10.000\n"
        "2️⃣ $15.000\n"
        "3️⃣ $20.000\n\n"
        f"{'🔒 Bloqueado: usa el sistema de referidos para desbloquear.' if bloqueado else '✅ Elegible según tus referidos.'}"
    )
    
    if get_previous_state(sender): # Check if there's a previous state
        msg += "\n0️⃣ Volver" # Add "Volver" option
        
    send_msg(cfg, sender, msg)

def handle_input(cfg, sender, text, send_msg):
    st = get(sender) or {}
    if st.get("flow") != "prestamos":
        return False

    refs = _referidos_activos(sender)
    if refs == 0:
        send_msg(cfg, sender, "⚠️ Aún no tenés referidos, las opciones están bloqueadas.")
        return True

    if text == "1":
        send_msg(cfg, sender, "✅ Solicitud aceptada para $10.000. Nuestro equipo te contactará.")
        return True
    if text == "2":
        send_msg(cfg, sender, "✅ Solicitud aceptada para $15.000. Nuestro equipo te contactará.")
        return True
    if text == "3":
        send_msg(cfg, sender, "✅ Solicitud aceptada para $20.000. Nuestro equipo te contactará.")
        return True

    return False
