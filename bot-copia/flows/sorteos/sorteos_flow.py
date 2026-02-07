from flows.state import get, set_state, get_previous_state
from create_payment_link import create_payment_link

def handle_sorteo(cfg, sender, send_msg):
    # Store the state for this flow. The new set_state pushes onto the stack.
    set_state(sender, {"flow": "sorteos", "step": "menu"}) 

    msg = (
        "🎟️ Sorteos activos:\n\n"
        "1️⃣ Ticket $500\n"
        "2️⃣ Ticket $1000\n"
        "3️⃣ Ticket $2000\n"
        "4️⃣ Ver bote acumulado\n"
    )
    
    if get_previous_state(sender): # Check if there's a previous state
        msg += "\n0️⃣ Volver" # Add "Volver" option
        
    send_msg(cfg, sender, msg)
    return True

def handle_input(cfg, sender, text, send_msg):
    st = get(sender) or {}
    if st.get("flow") != "sorteos":
        return False

    if text == "1":
        link, sandbox = create_payment_link(500, sender)
        send_msg(cfg, sender, f"✅ Link de pago Ticket $500:\n{link}")
        return True
    if text == "2":
        link, sandbox = create_payment_link(1000, sender)
        send_msg(cfg, sender, f"✅ Link de pago Ticket $1000:\n{link}")
        return True
    if text == "3":
        link, sandbox = create_payment_link(2000, sender)
        send_msg(cfg, sender, f"✅ Link de pago Ticket $2000:\n{link}")
        return True
    if text == "4":
        send_msg(cfg, sender, "📊 El bote acumulado se calcula como 70% de lo recaudado.")
        return True

    return False
