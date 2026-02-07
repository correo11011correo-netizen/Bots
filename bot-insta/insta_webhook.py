import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

VERIFY_TOKEN = "BOT1234"
ACCESS_TOKEN = os.getenv("TOKEN_INSTA")  # tu IGAA... desde .env

@app.route("/api/insta", methods=["GET", "POST"])
def insta_webhook():
    if request.method == "GET":
        # Validación inicial de Meta
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Error: token inválido", 403

    elif request.method == "POST":
        data = request.json
        print("📩 Evento recibido:", data)

        # Extraer el ID del remitente y el mensaje
        try:
            sender_id = data["entry"][0]["messaging"][0]["sender"]["id"]
            # Responder automáticamente con mensaje de bienvenida
            send_welcome_message(sender_id)
        except Exception as e:
            print("Error procesando evento:", e)

        return "ok", 200

def send_welcome_message(sender_id):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": sender_id},
        "message": {"text": "👋 ¡Bienvenido! Gracias por escribirnos en Instagram 🙌"}
    }
    r = requests.post(url, json=payload)
    print("➡️ Respuesta enviada:", r.status_code, r.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
