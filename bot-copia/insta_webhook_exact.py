import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "BOT1234")
ACCESS_TOKEN = os.getenv("FACEBOOK_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")

GRAPH_URL = "https://graph.facebook.com/v19.0"

@app.route("/api/insta", methods=["GET", "POST"])
def insta_webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Error: token inválido", 403

    elif request.method == "POST":
        data = request.json
        print("📩 Evento recibido:", data)

        if data.get("object") != "instagram":
            print("⚠️ Evento ignorado (no es Instagram)")
            return "ignored", 200

        try:
            message = data["entry"][0]["messaging"][0]["message"]

            # Ignorar mensajes echo (enviados por la propia página/app)
            if message.get("is_echo"):
                print("⚠️ Mensaje echo detectado, no se responde")
                return "ok", 200

            user_message = message.get("text", "")
            print(f"💬 Mensaje recibido en Instagram: {user_message}")

            # Buscar conversación activa
            conv_id = get_last_conversation_id()
            if conv_id:
                psid = get_instagram_psid(conv_id)
                if psid:
                    send_message(psid, f"👋 Hola! Recibimos tu mensaje: {user_message}")
                else:
                    print("⚠️ No se encontró PSID de Instagram en la conversación")
            else:
                print("⚠️ No se encontró ninguna conversación activa")

        except Exception as e:
            print("⚠️ Error procesando evento:", e)

        return "ok", 200

def send_message(recipient_id, text, tag=None):
    url = f"{GRAPH_URL}/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    if tag:
        payload["tag"] = tag
    params = {"access_token": ACCESS_TOKEN}
    r = requests.post(url, json=payload, params=params)

    if r.status_code == 200:
        print(f"✅ Mensaje enviado correctamente al PSID Instagram: {recipient_id}")
        return True
    else:
        print(f"⚠️ Error al enviar mensaje al PSID {recipient_id}: {r.status_code} - {r.text}")
        return False

def get_last_conversation_id():
    url = f"{GRAPH_URL}/{PAGE_ID}/conversations"
    params = {"access_token": ACCESS_TOKEN}
    r = requests.get(url, params=params)

    if r.status_code == 200:
        conversations = r.json().get("data", [])
        if conversations:
            conv_id = conversations[0].get("id")
            print(f"📂 Última Conversation ID: {conv_id}")
            return conv_id
    else:
        print("⚠️ No se pudieron listar conversaciones:", r.status_code, r.text)
    return None

def get_instagram_psid(conversation_id):
    url = f"{GRAPH_URL}/{conversation_id}?fields=participants"
    params = {"access_token": ACCESS_TOKEN}
    r = requests.get(url, params=params)

    if r.status_code == 200:
        participants = r.json().get("participants", {}).get("data", [])
        for p in participants:
            psid = p.get("id")
            platform = p.get("platform", "unknown")
            print(f"👤 Participant: {psid} (canal: {platform})")
            if platform == "instagram":
                print(f"✅ PSID exacto de Instagram encontrado: {psid}")
                return psid
    else:
        print("⚠️ No se pudieron obtener participantes:", r.status_code, r.text)
    return None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
