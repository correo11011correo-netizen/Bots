import os
import json
import requests
from flask import Flask, request, jsonify
from engine import setup_logging, load_submenu_flows, load_config, process_message
from flows.messenger import handle_messenger
from dotenv import load_dotenv
from create_payment_link import pref_id_to_sender
import logging

app = Flask(__name__)

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
    if "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    sender = msg.get("from")
                    text = msg.get("text", {}).get("body", "")
                    logging.info(f"📩 WhatsApp mensaje de {sender}: {text}")
                    process_message(cfg, sender, text)  # <-- ahora pasamos sender y text

                for status in value.get("statuses", []):
                    logging.info(f"📊 Estado: {status.get('status')} para {status.get('recipient_id')}")
    return "OK", 200

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
    if "entry" in data:
        for entry in data["entry"]:
            for event in entry.get("messaging", []):
                sender_id = event["sender"]["id"]
                if "message" in event:
                    text = event["message"].get("text", "")
                    logging.info(f"📩 Messenger mensaje de {sender_id}: {text}")
                    handle_messenger(cfg, data)
    return "OK", 200

@app.route("/api/mp", methods=["POST"])
def webhook_mp():
    cfg = app.config["cfg"]
    data = request.get_json()
    received_secret = request.headers.get("X-MP-Signature")
    if received_secret:
        if received_secret != cfg["mercadopago_webhook_secret"]:
            logging.error("❌ [server.py] Webhook rechazado: clave inválida")
            return jsonify({"error": "unauthorized"}), 401
    else:
        logging.warning("⚠️ [server.py] Webhook recibido sin firma (aceptado por compatibilidad)")

    logging.info(f"📥 [server.py] Notificación Mercado Pago válida: {data}")

    event_type = data.get("type")
    root_id = data.get("id")
    status = data.get("data", {}).get("status")

    if event_type == "payment":
        payment_id = data.get("data", {}).get("id")
        logging.info(f"💳 [server.py] Evento PAYMENT recibido. ID: {payment_id}")

        if cfg["mercadopago_access_token"] and payment_id:
            resp = requests.get(
                f"https://api.mercadopago.com/v1/payments/{payment_id}",
                headers={"Authorization": f"Bearer {cfg['mercadopago_access_token']}"}
            )
            if resp.status_code == 200:
                payment_info = resp.json()
                status = payment_info.get("status")
                amount = payment_info.get("transaction_amount")
                payer_email = payment_info.get("payer", {}).get("email")

                logging.info(f"💳 [server.py] Detalle pago: Status={status} | Amount={amount} | Payer={payer_email}")

                if status == "approved":
                    recipient = pref_id_to_sender.get(str(root_id), cfg.get("default_test_number"))
                    logging.info(f"✅ [server.py] Pago aprobado! ID: {payment_id} | Cliente: {recipient}")

                    process_message(app.config["cfg"], recipient, "payment_success")

    elif event_type == "topic_merchant_order_wh":
        logging.info(f"📦 [server.py] Evento MERCHANT_ORDER recibido. ID: {root_id} | Estado: {status}")
    elif event_type == "subscription":
        logging.info(f"🔔 [server.py] Evento SUBSCRIPTION recibido. ID: {root_id} | Estado: {status}")
    else:
        logging.info(f"ℹ️ [server.py] Evento desconocido: {event_type} | ID: {root_id} | Estado: {status}")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    setup_logging()
    load_submenu_flows()
    app.config["cfg"] = load_config()
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor Flask en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
