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

def gget(path, params=None):
    if params is None:
        params = {}
    params["access_token"] = ACCESS_TOKEN
    url = f"{GRAPH_URL}/{path}"
    r = requests.get(url, params=params)
    return r.status_code, r.json() if r.headers.get("Content-Type","").startswith("application/json") else {"_raw": r.text}

@app.route("/api/insta", methods=["GET", "POST"])
def insta_webhook():
    if request.method == "GET":
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        return (challenge, 200) if token == VERIFY_TOKEN else ("Error: token inválido", 403)

    data = request.json
    print("📩 Evento recibido:", data)

    if data.get("object") != "instagram":
        print("⚠️ Evento ignorado (no es Instagram)")
        return "ignored", 200

    try:
        msg = data["entry"][0]["messaging"][0]["message"]
        if msg.get("is_echo"):
            print("⚠️ Mensaje echo detectado, no se procesa")
            return "ok", 200

        user_message = msg.get("text", "")
        print(f"💬 Mensaje recibido en Instagram: {user_message}")

        # Construir árbol y clasificar IDs. Solo responder al que sea IG.
        build_id_tree_and_probe(user_message)

    except Exception as e:
        print("⚠️ Error procesando evento:", e)

    return "ok", 200

def list_conversations():
    code, data = gget(f"{PAGE_ID}/conversations")
    if code == 200:
        conversations = data.get("data", [])
        return [c["id"] for c in conversations]
    print("⚠️ Error al listar conversaciones:", code, data)
    return []

def classify_participant_id(psid):
    """
    Clasifica el ID con varias comprobaciones:
    - Si coincide con PAGE_ID => es la Página.
    - Si /{psid}?fields=username devuelve 'username' => Instagram.
    - Si /{psid}?fields=name devuelve 'name' sin 'username' => probablemente Messenger.
    - Además consulta /{PAGE_ID}?fields=instagram_business_account para validar vínculo IG.
    """
    if str(psid) == str(PAGE_ID):
        return {"id": psid, "channel": "page", "label": "📄 ID de la Página (no responder)"}

    # Intento IG: algunos PSIDs de IG exponen 'username' del perfil IG en contexto de la página vinculada
    code_u, data_u = gget(f"{psid}", params={"fields": "username,name,profile_pic"})
    username = data_u.get("username")
    name = data_u.get("name")
    profile_pic = data_u.get("profile_pic")

    # Comprobación del vínculo IG de la página
    code_ig, data_ig = gget(f"{PAGE_ID}", params={"fields": "instagram_business_account"})
    ig_linked = bool(data_ig.get("instagram_business_account", {}).get("id"))

    # Heurística robusta:
    # - Si hay username y la página tiene IG vinculado => Instagram.
    # - Si no hay username pero hay name => Messenger.
    # - Si no hay nada claro => unknown.
    if username and ig_linked:
        return {"id": psid, "channel": "instagram", "label": f"🙋‍♂️ Usuario Instagram (username: {username})"}
    elif name and not username:
        return {"id": psid, "channel": "messenger", "label": f"💬 Usuario Messenger (name: {name})"}
    else:
        return {"id": psid, "channel": "unknown", "label": "❔ Participante sin metadata clara (revisar)"}

def inspect_conversation(conv_id, user_message, send_tests=True):
    code, data = gget(f"{conv_id}", params={"fields": "participants"})
    if code != 200:
        print("⚠️ Error al inspeccionar conversación:", code, data)
        return []

    participants = data.get("participants", {}).get("data", [])
    print(f"📂 Conversación {conv_id}:")
    classified = []

    for p in participants:
        psid = p.get("id")
        info = classify_participant_id(psid)
        print(f"   └── {info['label']}: {psid} (canal: {info['channel']})")
        classified.append(info)

    # Opcional: enviar pruebas solo al ID detectado como Instagram
    if send_tests:
        for info in classified:
            if info["channel"] == "instagram":
                send_message(info["id"], f"🔎 Test IG al PSID {info['id']}.\nEcho: {user_message}")
            elif info["channel"] == "page":
                print(f"⏭️ Saltando envío al ID de página {info['id']}")
            else:
                print(f"⏭️ Saltando envío a canal {info['channel']} ({info['id']})")

    return classified

def build_id_tree_and_probe(user_message):
    convs = list_conversations()
    print("🌳 Árbol de IDs detectados:")
    for conv_id in convs:
        inspect_conversation(conv_id, user_message, send_tests=True)

def send_message(recipient_id, text):
    url = f"{GRAPH_URL}/me/messages"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    params = {"access_token": ACCESS_TOKEN}
    r = requests.post(url, json=payload, params=params)
    if r.status_code == 200:
        print(f"✅ Mensaje enviado correctamente al ID: {recipient_id}")
    else:
        print(f"⚠️ Error al enviar mensaje al ID {recipient_id}: {r.status_code} - {r.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
