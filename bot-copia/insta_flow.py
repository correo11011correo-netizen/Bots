import os
import requests
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")  # tu token IGAA...
PAGE_ID = os.getenv("PAGE_ID")                 # ej: 17841480142090472
GRAPH_URL = "https://graph.facebook.com/v19.0"

def list_conversations():
    url = f"{GRAPH_URL}/{PAGE_ID}/conversations"
    params = {"access_token": ACCESS_TOKEN}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json().get("data", [])
    else:
        print("⚠️ Error al listar conversaciones:", r.status_code, r.text)
        return []

def inspect_conversation(conv_id):
    url = f"{GRAPH_URL}/{conv_id}?fields=participants"
    params = {"access_token": ACCESS_TOKEN}
    r = requests.get(url, params=params)
    if r.status_code == 200:
        return r.json().get("participants", {}).get("data", [])
    else:
        print("⚠️ Error al inspeccionar conversación:", r.status_code, r.text)
        return []

def send_message(recipient_id, text):
    url = f"{GRAPH_URL}/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    params = {"access_token": ACCESS_TOKEN}
    r = requests.post(url, json=payload, params=params)
    if r.status_code == 200:
        print(f"✅ Mensaje enviado al usuario IG: {recipient_id}")
    else:
        print(f"⚠️ Error al enviar mensaje al {recipient_id}: {r.status_code} - {r.text}")

def main():
    print("🌳 Árbol de IDs detectados:")
    conversations = list_conversations()
    for conv in conversations:
        conv_id = conv["id"]
        print(f"📂 Conversación {conv_id}:")
        participants = inspect_conversation(conv_id)
        for p in participants:
            psid = p["id"]
            if psid == PAGE_ID:
                print(f"   └── 📄 ID del Bot/Página: {psid} (no responder)")
            else:
                print(f"   └── 🙋‍♂️ PSID Usuario Instagram: {psid} (válido)")
                # Enviar mensaje de prueba solo al usuario IG
                send_message(psid, f"👋 Hola IG! Este mensaje va al PSID {psid}")

if __name__ == "__main__":
    main()
