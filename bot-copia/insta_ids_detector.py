import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("FACEBOOK_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")
GRAPH_URL = "https://graph.facebook.com/v19.0"

def list_conversations():
    url = f"{GRAPH_URL}/{PAGE_ID}/conversations"
    params = {"access_token": ACCESS_TOKEN}
    r = requests.get(url, params=params)

    if r.status_code == 200:
        conversations = r.json().get("data", [])
        print(f"📂 Se encontraron {len(conversations)} conversaciones")
        return [c["id"] for c in conversations]
    else:
        print("⚠️ Error al listar conversaciones:", r.status_code, r.text)
        return []

def inspect_conversation(conv_id):
    url = f"{GRAPH_URL}/{conv_id}?fields=participants"
    params = {"access_token": ACCESS_TOKEN}
    r = requests.get(url, params=params)

    instagram_ids = []

    if r.status_code == 200:
        participants = r.json().get("participants", {}).get("data", [])
        print(f"🔎 Conversación {conv_id} tiene {len(participants)} participantes")
        for p in participants:
            psid = p.get("id")
            platform = p.get("platform", "unknown")
            print(f"👤 Participant: {psid} (canal: {platform})")
            if platform == "instagram":
                instagram_ids.append(psid)
        if instagram_ids:
            print(f"✅ PSIDs de Instagram detectados: {instagram_ids}")
    else:
        print("⚠️ Error al inspeccionar conversación:", r.status_code, r.text)

    return instagram_ids

def main():
    convs = list_conversations()
    all_instagram_ids = []
    for conv_id in convs:
        ids = inspect_conversation(conv_id)
        all_instagram_ids.extend(ids)
    print("📌 Lista final de PSIDs de Instagram detectados:", all_instagram_ids)

if __name__ == "__main__":
    main()
