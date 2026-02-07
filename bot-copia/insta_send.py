import os
import requests
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

ACCESS_TOKEN = os.getenv("INSTAGRAM_PAGE_ACCESS_TOKEN")  # Page Access Token válido
PAGE_ID = os.getenv("PAGE_ID")  # ej: 17841480142090472
RECIPIENT_ID = os.getenv("TEST_RECIPIENT_ID")  # PSID del cliente IG

GRAPH_URL = "https://graph.facebook.com/v21.0/me/messages"

def send_message(recipient_id, text):
    """Enviar mensaje al cliente IG usando el Page Access Token"""
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}

    r = requests.post(GRAPH_URL, json=payload, params=params, headers=headers)
    if r.status_code == 200:
        print(f"✅ Mensaje enviado desde BOT {PAGE_ID} → Cliente {recipient_id}: {text}")
    else:
        print(f"⚠️ Error al enviar mensaje: {r.status_code} - {r.text}")

if __name__ == "__main__":
    # Mensaje de prueba
    send_message(RECIPIENT_ID, "👋 Hola IG! Este mensaje viene directo desde el bot.")
