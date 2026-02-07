import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

ACCESS_TOKEN = os.getenv("INSTAGRAM_PAGE_ACCESS_TOKEN")  # tu token IGAA...
PAGE_ID = os.getenv("PAGE_ID")  # ej: 17841480142090472
GRAPH_URL = "https://graph.facebook.com/v21.0"

def send_message(recipient_id, text):
    url = f"{GRAPH_URL}/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {"Content-Type": "application/json"}
    params = {"access_token": ACCESS_TOKEN}
    r = requests.post(url, json=payload, params=params, headers=headers)
    if r.status_code == 200:
        print(f"✅ Mensaje enviado al usuario IG: {recipient_id}")
    else:
        print(f"⚠️ Error al enviar mensaje al {recipient_id}: {r.status_code} - {r.text}")

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verificación inicial del webhook
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == os.getenv("VERIFY_TOKEN"):
            return challenge
        return "Token inválido", 403

    if request.method == "POST":
        data = request.json
        print("📩 Evento recibido:", data)

        if data.get("object") == "instagram":
            for entry in data.get("entry", []):
                for msg_event in entry.get("messaging", []):
                    sender_id = msg_event["sender"]["id"]
                    recipient_id = msg_event["recipient"]["id"]
                    text = msg_event.get("message", {}).get("text")

                    print(f"👤 Usuario IG: {sender_id}")
                    print(f"🤖 Bot/Página: {recipient_id} (no responder)")
                    print(f"💬 Mensaje: {text}")

                    # Responder solo al usuario IG
                    send_message(sender_id, f"👋 Hola! Recibí tu mensaje: {text}")

        return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
