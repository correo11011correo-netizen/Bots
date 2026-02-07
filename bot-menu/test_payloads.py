import os
import requests
import json

# Variables de entorno (asegurate de exportarlas antes de correr)
TOKEN = os.getenv("WHATSAPP_BUSINESS_API_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_BUSINESS_PHONE_ID")
TEST_NUMBER = os.getenv("DEFAULT_TEST_NUMBER")

URL = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Payloads de prueba
payloads = {
    "texto_simple": {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "text": {"body": "Hola mundo desde la API"}
    },
    "menu_botones": {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "📌 Elige una categoría:"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "1", "title": "🛒 Comercio"}},
                    {"type": "reply", "reply": {"id": "2", "title": "🍽️ Restaurantes"}},
                    {"type": "reply", "reply": {"id": "3", "title": "⚙️ Servicios"}}
                ]
            }
        }
    },
    "promo_texto": {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "text": {
            "body": "🎉 Promo especial: 20% de descuento en bots para negocios locales."
        }
    },
    "contacto_texto": {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "text": {
            "body": "📞 Contacto de ventas: +54 9 3765 000000\n🌐 Web: https://tuservicio.com/bots"
        }
    }
}

# Testear cada payload
for nombre, payload in payloads.items():
    print(f"\n=== Probando: {nombre} ===")
    r = requests.post(URL, headers=HEADERS, json=payload)
    print("Status:", r.status_code)
    try:
        print("Respuesta:", json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception:
        print("Respuesta cruda:", r.text)
