import os
from flask import Flask, request
from dotenv import load_dotenv
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Dummy config for now, will be loaded from minimal_engine
app.config["cfg"] = {
    "verify": os.getenv("VERIFY_TOKEN", "DEFAULT_VERIFY_TOKEN"),
    "phone_id": os.getenv("WHATSAPP_BUSINESS_PHONE_ID", "DEFAULT_PHONE_ID"),
    "token": os.getenv("WHATSAPP_BUSINESS_API_TOKEN", "DEFAULT_TOKEN"),
    "ngrok_public_url": os.getenv("NGROK_PUBLIC_URL", "http://localhost:3000"),
}

# Import minimal_engine after app is defined (to avoid circular imports if engine needs app)
import minimal_engine

@app.route("/api/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == app.config["cfg"]["verify"]:
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Verification token mismatch", 403
    return "Missing hub.mode or hub.verify_token", 400

@app.route("/api/webhook", methods=["POST"])
def webhook_post():
    data = request.get_json()
    logging.info(f"Received webhook data: {data}")

    # Simplified processing for minimal bot
    if "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    sender = msg.get("from")
                    text = msg.get("text", {}).get("body", "")
                    logging.info(f"📩 Message from {sender}: {text}")
                    minimal_engine.process_message(app.config["cfg"], sender, text)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    logging.info(f"🚀 Minimal Flask server running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True) # debug=True for development convenience