import sqlite3
import os
import requests
from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime

# --- Configuration ---
try:
    DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bot-dashboard', 'backend')
    DB_PATH = os.path.join(DB_DIR, 'bot_dashboard.db')
    BOT_PAGINA_SEND_URL = "http://localhost:5000/api/send_message_from_dashboard"
except NameError:
    DB_DIR = os.path.join(os.getcwd(), '..', 'bot-dashboard', 'backend')
    DB_PATH = os.path.join(DB_DIR, 'bot_dashboard.db')
    BOT_PAGINA_SEND_URL = "http://localhost:5000/api/send_message_from_dashboard"

# Initialize Flask to serve static files from the current directory ('bot-whapp-pagina')
app = Flask(__name__, static_folder='.', static_url_path='')

# --- Database Utilities ---
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Make sure the 'bot-dashboard' project is in the correct location.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Frontend Route ---
@app.route('/')
def index():
    """Serves the main index.html file."""
    return send_from_directory('.', 'index.html')

# --- API Endpoints ---
@app.route("/api/conversations", methods=["GET"])
def get_conversations():
    """API endpoint to retrieve all conversations."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT
                c.id AS contact_id,
                c.phone_number,
                c.name,
                conv.is_human_intervening,
                MAX(m.timestamp) AS last_message_timestamp,
                (SELECT content FROM messages WHERE contact_id = c.id ORDER BY timestamp DESC LIMIT 1) AS last_message_content
            FROM contacts c
            LEFT JOIN conversations conv ON c.id = conv.contact_id
            LEFT JOIN messages m ON c.id = m.contact_id
            GROUP BY c.id
            ORDER BY last_message_timestamp DESC;
        """
        cursor.execute(query)
        conversations_raw = cursor.fetchall()
        conn.close()
        conversations = [dict(row) for row in conversations_raw]
        return jsonify(conversations)
    except Exception as e:
        print(f"Error getting conversations: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/messages/<string:phone_number>", methods=["GET"])
def get_messages(phone_number):
    """API endpoint to retrieve messages for a specific phone number."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT
                m.sender,
                m.content,
                m.timestamp
            FROM messages m
            JOIN contacts c ON m.contact_id = c.id
            WHERE c.phone_number = ?
            ORDER BY m.timestamp ASC;
        """
        cursor.execute(query, (phone_number,))
        messages_raw = cursor.fetchall()
        conn.close()
        messages = [dict(row) for row in messages_raw]
        return jsonify(messages)
    except Exception as e:
        print(f"Error getting messages for {phone_number}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/send", methods=["POST"])
def send_manual_message():
    """API endpoint to send a manual message."""
    data = request.get_json()
    phone_number = data.get("phone_number")
    message = data.get("message")

    if not phone_number or not message:
        return jsonify({"error": "phone_number and message are required"}), 400

    try:
        response = requests.post(
            BOT_PAGINA_SEND_URL,
            json={"phone_number": phone_number, "message": message}
        )
        response.raise_for_status()
        return jsonify({"status": "success", "detail": response.json()}), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error forwarding message to bot-pagina: {e}")
        return jsonify({"error": f"Failed to connect to bot-pagina server: {e}"}), 503

if __name__ == "__main__":
    dashboard_port = 5002
    print(f"🚀 Dashboard running on http://localhost:{dashboard_port}")
    print("   Access the dashboard by visiting that URL in your browser.")
    print(f"   Ensure the main bot server ('bot-pagina/server.py') is also running (likely on port 5000).")
    app.run(host='0.0.0.0', port=dashboard_port, debug=True)