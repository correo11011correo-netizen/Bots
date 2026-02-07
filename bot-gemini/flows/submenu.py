from flows.state import set_state, get_previous_state

def handle_submenu_entry(cfg, sender, send_msg, submenu_flows):
    if not submenu_flows:
        send_msg(cfg, sender, "No hay flujos de submenú cargados.")
        return
    msg_lines = ["🧩 Servicios disponibles:"]
    for key, data in submenu_flows.items():
        msg_lines.append(f"{key}. {data['text']}")
    
    msg_lines.append("\nResponde con el número de la opción.")
    
    if get_previous_state(sender): # Check if there's a previous state
        msg_lines.append("0. Volver") # Add "Volver" option
        
    send_msg(cfg, sender, "\n".join(msg_lines))
    set_state(sender, {"flow": "submenu"})
