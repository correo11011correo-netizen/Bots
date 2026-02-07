import os
import json
import requests

# 📥 Cargar configuración desde config/settings.json
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config', 'settings.json')

with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)

TOKEN = config.get("whatsapp_business_api_token")
PHONE_ID = config.get("whatsapp_business_phone_id")
TEST_NUMBER = config.get("default_test_number", "5493765245980")

URL = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Bloques de botones para test
payloads = {
    "botones_reply": {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "📌 Elige una opción:"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "btn1", "title": "🛒 Comercio"}},
                    {"type": "reply", "reply": {"id": "btn2", "title": "🍽️ Restaurantes"}},
                    {"type": "reply", "reply": {"id": "btn3", "title": "⚙️ Servicios"}}
                ]
            }
        }
    },
    "boton_url_invalido": {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "🌐 Ver más en web"},
            "action": {
                "buttons": [
                    {"type": "url", "url": "https://tuservicio.com/bots", "title": "Abrir link"}
                ]
            }
        }
    },
    "boton_call_invalido": {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "📞 Llamar a ventas"},
            "action": {
                "buttons": [
                    {"type": "call", "phone_number": "+5493765000000", "title": "Llamar"}
                ]
            }
        }
    }
}

# Testear cada bloque
for nombre, payload in payloads.items():
    print(f"\n=== Probando: {nombre} ===")
    r = requests.post(URL, headers=HEADERS, json=payload)
    print("Status:", r.status_code)
    try:
        print("Respuesta:", json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception:
        print("Respuesta cruda:", r.text)
