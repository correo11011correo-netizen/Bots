import os
import json
import requests

# Variables de entorno desde tu .env
TOKEN = os.getenv("WHATSAPP_BUSINESS_API_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_BUSINESS_PHONE_ID")
TEST_NUMBER = os.getenv("DEFAULT_TEST_NUMBER")

URL = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Bloques de prueba basados en lo que encontraste
payloads = {
    "texto_simple": {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "text": {"body": "Hola mundo desde la API"}
    },
    "botones_reply": {
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
    "lista": {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "📌 Selecciona una categoría de empresa:"},
            "action": {
                "button": "Ver categorías",
                "sections": [
                    {
                        "title": "Tipos de empresa",
                        "rows": [
                            {"id": "1", "title": "🛒 Comercio", "description": "Bots para ventas"},
                            {"id": "2", "title": "🍽️ Restaurantes", "description": "Bots para reservas"},
                            {"id": "3", "title": "⚙️ Servicios", "description": "Bots para soporte"},
                            {"id": "4", "title": "📚 Educación", "description": "Bots para inscripciones"}
                        ]
                    }
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
