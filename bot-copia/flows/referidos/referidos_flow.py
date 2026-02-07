from flows.state import get, set_state, get_previous_state

# Base de datos simple en memoria
ref_db = {}  # {user_id: {"code": str, "refs": set()}}

def _code_for(user_id):
    return f"REF-{user_id}"

def handle_referidos(cfg, sender, send_msg):
    set_state(sender, {"flow": "referidos", "step": "menu"})
    # Inicializar si no existe
    if sender not in ref_db:
        ref_db[sender] = {"code": _code_for(sender), "refs": set()}
    code = ref_db[sender]["code"]
    msg = (
        "👥 Sistema de referidos\n\n"
        f"Tu código de invitación: {code}\n"
        "Comparte este código. Cuando tu referido lo envíe, se te suma.\n\n"
        "Opciones:\n"
        "1️⃣ Ver progreso\n"
        "2️⃣ Enviar código (soy referido)\n"
        "3️⃣ Reglas\n"
    )
    
    if get_previous_state(sender): # Check if there's a previous state
        msg += "\n0️⃣ Volver" # Add "Volver" option
        
    send_msg(cfg, sender, msg)

def handle_input(cfg, sender, text, send_msg):
    st = get(sender) or {}
    if st.get("flow") != "referidos":
        return False

    if text == "1":
        refs = len(ref_db.get(sender, {"refs": set()})["refs"])
        send_msg(cfg, sender, f"📈 Tenés {refs} referidos validados.")
        return True

    if text == "2":
        set_state(sender, {"flow": "referidos", "step": "enter_code"})
        send_msg(cfg, sender, "Escribe el código del usuario que te invitó (ej: REF-<id>).")
        return True

    if st.get("step") == "enter_code" and text.startswith("REF-"):
        inviter = text.replace("REF-", "")
        if inviter == sender:
            send_msg(cfg, sender, "⚠️ No podés referirte a vos mismo.")
            return True
        rc = ref_db.setdefault(inviter, {"code": _code_for(inviter), "refs": set()})
        rc["refs"].add(sender)
        send_msg(cfg, sender, f"✅ Referencia registrada para {inviter}. ¡Gracias!")
        set_state(sender, {"flow": "referidos", "step": "menu"})
        return True

    if text == "3":
        send_msg(cfg, sender, "📜 Reglas: Cada referido válido cuenta si es único. Evitamos autoref y duplicados.")
        return True

    return False
