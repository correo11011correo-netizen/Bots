import json
from responses import get_response
from welcome import send_welcome
from menu import send_menu_payload, send_list_menu_payload
from utils import log_message

# Simulación de mensajes entrantes
def simulate_message(sender, text):
    log_message(sender, text)
    if text in ["/start", "hola", "buenas"]:
        return send_welcome()
    elif text in ["menu", "opciones"]:
        return send_menu_payload()
    elif text == "lista":
        return send_list_menu_payload()
    else:
        return get_response(text)

def main():
    sender = "5493765245980"
    pruebas = ["/start", "menu", "1", "2", "3", "4", "lista", "xyz"]

    for msg in pruebas:
        print("\n--- Simulación ---")
        print(f"📩 Usuario: {msg}")
        respuesta = simulate_message(sender, msg)
        if isinstance(respuesta, str):
            print(f"🤖 Bot: {respuesta}")
        else:
            print("🤖 Bot (payload interactivo):")
            print(json.dumps(respuesta, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
