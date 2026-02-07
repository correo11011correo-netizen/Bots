import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)
load_dotenv()

# Tokens y configuración desde .env
ACCESS_TOKEN = os.getenv("INSTAGRAM_PAGE_ACCESS_TOKEN")  # Page Access Token válido
PAGE_ID = os.getenv("PAGE_ID")  # ej: 17841480142090472
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")  # BOT1234
GRAPH_URL = "https://graph.facebook.com/v21.0"

def log_chat(event_type, sender_id, recipient_id, message_text=None):
    """Log con fecha/hora mostrando IDs de ambos lados"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] 🔎 {event_type} | Sender: {sender_id} | Recipient: {recipient_id} | Msg: {message_text}")

def send_message(recipient_id, text):
    """Enviar mensaje al usuario IG usando el Page Access Token"""
    url = f"{GRAPH_URL}/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, json=payload, params=params, headers=headers)
    if r.status_code == 200:
        log_chat("BotResponse", PAGE_ID, recipient_id, text)
    else:
        print(f"⚠️ Error al enviar mensaje: {r.status_code} - {r.text}")

@app.route("/api/insta", methods=["GET", "POST"])
def insta_webhook():
    if request.method == "GET":
        # Verificación inicial del webhook
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge
        return "Token inválido", 403

    if request.method == "POST":
        data = request.json
        print("📩 Payload recibido:", data)

        if data.get("object") == "instagram":
            for entry in data.get("entry", []):
                for msg_event in entry.get("messaging", []):
                    sender_id = msg_event["sender"]["id"]
                    recipient_id = msg_event["recipient"]["id"]
                    text = msg_event.get("message", {}).get("text")

                    log_chat("UserMessage", sender_id, recipient_id, text)

                    # Responder solo si el sender es un usuario IG (no la página)
                    if sender_id != PAGE_ID:
                        send_message(sender_id, f"👋 Hola IG! Recibí tu mensaje: {text}")

        return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
