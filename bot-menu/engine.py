import os, json, requests
from flask import Flask, request
from utils import log_message, setup_logging
from responses import get_response
from welcome import send_welcome
from menus.main_menu import send_menu_payload
from menus.services_menu import send_list_menu_payload
from flows.whatsapp import handle_whatsapp
from flows.instagram import handle_instagram
from flows.messenger import handle_messenger
from flows.demo import handle_demo_entry, handle_demo_flow
from flows.contact import handle_contact

CONFIG_FILE = "config/settings.json"
app = Flask(__name__)

def load_config():
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
    return {
        "token": os.getenv("WHATSAPP_BUSINESS_API_TOKEN", cfg.get("whatsapp_business_api_token")),
        "phone_id": os.getenv("WHATSAPP_BUSINESS_PHONE_ID", cfg.get("whatsapp_business_phone_id")),
        "verify": os.getenv("VERIFY_TOKEN", cfg.get("verify_token"))
    }

def send_msg(cfg, to, body):
    url = f"https://graph.facebook.com/v19.0/{cfg['phone_id']}/messages"
    headers = {"Authorization": f"Bearer {cfg['token']}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}}
    try:
        import requests
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        print(f"✅ Enviado a {to}: {body}")
    except Exception as e:
        print(f"❌ Error enviando: {e}")

@app.route("/api/webhook", methods=["GET"])
def verify():
    cfg = app.config["cfg"]
    if request.args.get("hub.verify_token") == cfg["verify"]:
        return request.args.get("hub.challenge")
    return ("Token mismatch", 403)

@app.route("/api/webhook", methods=["POST"])
def webhook():
    cfg = app.config["cfg"]
    data = request.get_json()
    for msg in data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", []):
        text_raw = msg.get("text", {}).get("body", "")
        text = text_raw.strip().lower()
        sender = msg.get("from")
        log_message(sender, text_raw)

        # Flujo demo tiene prioridad si hay estado
        if handle_demo_flow(cfg, sender, text, send_msg):
            continue

        # Comandos básicos
        if text in ["/start", "hola", "buenas"]:
            send_msg(cfg, sender, send_welcome()); continue
        if text in ["menu", "opciones"]:
            send_msg(cfg, sender, send_menu_payload()); continue
        if text == "lista":
            send_msg(cfg, sender, send_list_menu_payload()); continue

        # Menú principal (modular)
        if text == "1": handle_whatsapp(cfg, sender, send_msg); continue
        if text == "2": handle_instagram(cfg, sender, send_msg); continue
        if text == "3": handle_messenger(cfg, sender, send_msg); continue
        if text in ["4", "demo"]: handle_demo_entry(cfg, sender, send_msg); continue
        if text == "5": handle_contact(cfg, sender, send_msg); continue

        # Fallback genérico
        send_msg(cfg, sender, get_response(text))
    return "OK", 200

if __name__ == "__main__":
    setup_logging()
    app.config["cfg"] = load_config()
    port = int(os.getenv("PORT", 3000))
    print(f"🚀 Servidor Flask en puerto {port}")
    app.run(port=port, debug=False)
