from ..state import set

def handle_submenu_entry(cfg, sender, send_msg, submenu_flows):
    set(sender, {"flow": "submenu"})
    
    menu_text = "🤖 *Submenú de Demos de Bots*\n\n"
    menu_text += "Por favor, elige una de las siguientes demos:\n\n"
    
    for key, value in submenu_flows.items():
        menu_text += f"{key}️⃣ {value['text']}\n"
        
    menu_text += "\n👉 Escribí el número de la opción que quieras explorar."
    
    send_msg(cfg, sender, menu_text)

