import os
import json
import requests
import sqlite3
from flask import Flask, request, jsonify, render_template, send_from_directory
from dotenv import load_dotenv
from engine import setup_logging, load_submenu_flows, load_config, process_message, send_msg
from flows.messenger import handle_messenger
import db_manager

# --- Paths Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_UI_PATH = os.path.join(os.path.dirname(BASE_DIR), 'bot-whapp-pagina')
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), 'bot-dashboard', 'backend', 'bot_dashboard.db')

# Initialize Flask to serve the dashboard UI from the specified template and static folder
app = Flask(__name__, template_folder=DASHBOARD_UI_PATH, static_folder=DASHBOARD_UI_PATH)

# --- Database Utilities for Dashboard ---
def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Bot Webhook Endpoints (Original) ---
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
                    print(f"📩 WhatsApp de: {msg.get('from')}, Mensaje: {msg.get('text', {}).get('body', '')}")
    process_message(cfg, data)
    return "OK", 200

# (Other original webhook endpoints can remain here...)

# --- Dashboard Frontend & API Endpoints (Merged) ---

# Route to serve the dynamic index.html with the Ngrok URL injected
@app.route('/')
def serve_dashboard():
    ngrok_url = app.config.get("cfg", {}).get("ngrok_public_url", "")
    return render_template('index.html', NGROK_URL=ngrok_url)

# Route to serve other static files for the dashboard (CSS, JS)
@app.route('/<path:path>')
def serve_dashboard_static_files(path):
    return send_from_directory(DASHBOARD_UI_PATH, path)
    
@app.route("/api/conversations", methods=["GET"])
def get_conversations():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT c.id AS contact_id, c.phone_number, c.name, conv.is_human_intervening,
                   MAX(m.timestamp) AS last_message_timestamp,
                   (SELECT content FROM messages WHERE contact_id = c.id ORDER BY timestamp DESC LIMIT 1) AS last_message_content
            FROM contacts c
            LEFT JOIN conversations conv ON c.id = conv.contact_id
            LEFT JOIN messages m ON c.id = m.contact_id
            GROUP BY c.id ORDER BY last_message_timestamp DESC;
        """
        cursor.execute(query)
        conversations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(conversations)
    except Exception as e:
        print(f"Error getting conversations: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/messages/<string:phone_number>", methods=["GET"])
def get_messages(phone_number):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT sender, content, timestamp FROM messages m JOIN contacts c ON m.contact_id = c.id WHERE c.phone_number = ? ORDER BY m.timestamp ASC;"
        cursor.execute(query, (phone_number,))
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(messages)
    except Exception as e:
        print(f"Error getting messages for {phone_number}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/send_message_from_dashboard", methods=["POST"])
def send_message_from_dashboard():
    cfg = app.config["cfg"]
    data = request.get_json()
    phone_number = data.get("phone_number")
    message = data.get("message")
    if not phone_number or not message:
        return jsonify({"error": "Phone number and message are required."}), 400
    try:
        send_msg(cfg, phone_number, message)
        db_manager.add_message(phone_number, 'human', message)
        return jsonify({"status": "success", "message": "Message sent and recorded."}), 200
    except Exception as e:
        print(f"Error sending message from dashboard: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    load_dotenv()
    setup_logging()
    load_submenu_flows()
    app.config["cfg"] = load_config()
    port = int(os.getenv("PORT", 5000))
    ngrok_url = app.config.get("cfg", {}).get("ngrok_public_url", "URL_NO_ENCONTRADA")
    print(f"🚀 Servidor unificado en puerto {port}")
    print(f"   - Webhooks de Bot: {ngrok_url}/api/webhook")
    print(f"   - Panel de Control: {ngrok_url}")
    app.run(host='0.0.0.0', port=port, debug=False)
