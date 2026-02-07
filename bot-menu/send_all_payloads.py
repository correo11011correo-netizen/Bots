import os, json, requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("WHATSAPP_BUSINESS_API_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_BUSINESS_PHONE_ID")
TEST_NUMBER = os.getenv("DEFAULT_TEST_NUMBER", "5493765245980")

URL = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def send(payload, name=""):
    r = requests.post(URL, headers=HEADERS, json=payload)
    print(f"\n➡️ Enviando {name}:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")
    print(f"⬅️ Respuesta: {r.status_code} {r.text}\n")

# --- Payloads ---
def payload_text():
    return {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "text",
        "text": {"body": "👋 Hola, este es un mensaje de texto simple"}
    }

def payload_button():
    return {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "📌 Elige una opción:"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "1", "title": "🛒 Comercio"}},
                    {"type": "reply", "reply": {"id": "2", "title": "🍽️ Restaurantes"}},
                    {"type": "url", "url": "https://tuservicio.com/bots", "title": "🌐 Ver más en web"},
                    {"type": "call", "phone_number": "+5493765000000", "title": "📞 Llamar a ventas"}
                ]
            }
        }
    }

def payload_list():
    return {
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
                            {"id": "1", "title": "🛒 Comercio", "description": "Bots para ventas y atención"},
                            {"id": "2", "title": "🍽️ Restaurantes", "description": "Bots para reservas y delivery"},
                            {"id": "3", "title": "⚙️ Servicios", "description": "Bots para soporte y turnos"},
                            {"id": "4", "title": "📚 Educación", "description": "Bots para inscripciones y consultas"}
                        ]
                    }
                ]
            }
        }
    }

def payload_image():
    return {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "image",
        "image": {"link": "https://www.w3schools.com/w3images/lights.jpg"}
    }

def payload_document():
    return {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "document",
        "document": {
            "link": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "caption": "📄 Documento de prueba"
        }
    }

def payload_audio():
    return {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "audio",
        "audio": {"link": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"}
    }

def payload_video():
    return {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "video",
        "video": {
            "link": "https://www.w3schools.com/html/mov_bbb.mp4",
            "caption": "🎬 Video de prueba"
        }
    }

def payload_location():
    return {
        "messaging_product": "whatsapp",
        "to": TEST_NUMBER,
        "type": "location",
        "location": {
            "latitude": "-27.362",
            "longitude": "-55.900",
            "name": "Posadas",
            "address": "Misiones, Argentina"
        }
    }

# --- Main ---
def main():
    send(payload_text(), "Texto")
    send(payload_button(), "Botones")
    send(payload_list(), "Lista")
    send(payload_image(), "Imagen")
    send(payload_document(), "Documento")
    send(payload_audio(), "Audio")
    send(payload_video(), "Video")
    send(payload_location(), "Ubicación")

if __name__ == "__main__":
    main()
