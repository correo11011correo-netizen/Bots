import os
import json
import requests
from flask import Flask, request
from engine import setup_logging, load_submenu_flows, load_config, process_message
from flows.messenger import handle_messenger

app = Flask(__name__)

# --- WhatsApp & Instagram ---
@app.route("/api/webhook", methods=["GET"])
def verify_whatsapp_instagram():
    cfg = app.config["cfg"]
    if request.args.get("hub.verify_token") == cfg["verify"]:
        return request.args.get("hub.challenge")
    return ("Token mismatch WhatsApp/Instagram", 403)

@app.route("/api/webhook", methods=["POST"])
def webhook_whatsapp_instagram():
    cfg = app.config["cfg"]
    data = request.get_json()

    # Log más limpio
    if "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                # Mensajes entrantes
                for msg in value.get("messages", []):
                    sender = msg.get("from")
                    text = msg.get("text", {}).get("body", "")
                    print(f"📩 WhatsApp mensaje de {sender}: {text}")
                # Estados de entrega
                for status in value.get("statuses", []):
                    print(f"📊 Estado: {status.get('status')} para {status.get('recipient_id')}")

    # delega a engine.py (maneja WhatsApp e Instagram)
    process_message(cfg, data)
    return "OK", 200

# --- Messenger ---
@app.route("/api/webhook_messenger", methods=["GET"])
def verify_messenger():
    cfg = app.config["cfg"]
    if request.args.get("hub.verify_token") == cfg["verify"]:
        return request.args.get("hub.challenge")
    return ("Token mismatch Messenger", 403)

@app.route("/api/webhook_messenger", methods=["POST"])
def webhook_messenger():
    cfg = app.config["cfg"]
    data = request.get_json()

    # Log más limpio
    if "entry" in data:
        for entry in data["entry"]:
            for event in entry.get("messaging", []):
                sender_id = event["sender"]["id"]
                if "message" in event:
                    text = event["message"].get("text", "")
                    print(f"📩 Messenger mensaje de {sender_id}: {text}")

    # delega a flows/messenger.py con función real de envío
    handle_messenger(cfg, data)
    return "OK", 200

if __name__ == "__main__":
    setup_logging()
    load_submenu_flows()
    app.config["cfg"] = load_config()
    port = int(os.getenv("PORT", 3000))
    print(f"🚀 Servidor Flask en puerto {port}")
    app.run(port=port, debug=False)
