import os
import requests
from flask import Flask, request
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__)
load_dotenv()

ACCESS_TOKEN = os.getenv("INSTAGRAM_PAGE_ACCESS_TOKEN")  # Token IGAA...
PAGE_ID = os.getenv("PAGE_ID")  # ej: 17841480142090472
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")  # BOT1234
GRAPH_URL = "https://graph.facebook.com/v21.0"

def log_event(event_type, sender_id, recipient_id, message_text=None):
    """Log simple con fecha/hora para trazabilidad"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] 📩 Evento {event_type} | Sender: {sender_id} | Recipient: {recipient_id} | Msg: {message_text}")

def send_message(recipient_id, text):
    """Enviar mensaje al usuario IG"""
    url = f"{GRAPH_URL}/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, json=payload, params=params, headers=headers)
    if r.status_code == 200:
        print(f"✅ Mensaje enviado al usuario IG {recipient_id}")
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

                    log_event("InstagramMessage", sender_id, recipient_id, text)

                    # Responder solo al usuario IG (no al PAGE_ID)
                    if sender_id != PAGE_ID:
                        send_message(sender_id, f"👋 Hola IG! Recibí tu mensaje: {text}")

        return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
