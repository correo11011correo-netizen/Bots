import json
import os
import time
import requests
from flask import Flask, request
import threading
import logging

# --- Configuration ---
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config', 'settings.json')
TEST_MODE_RECIPIENT = "5493765245980"

# --- Helper Functions ---
def load_config():
    """Loads configuration from settings.json and environment variables."""
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    else:
        print(f"⚠️ Advertencia: El archivo de configuración no se encontró en {CONFIG_FILE}.")

    config['whatsapp_business_api_token'] = os.getenv('WHATSAPP_BUSINESS_API_TOKEN', config.get('whatsapp_business_api_token', ''))
    config['whatsapp_business_phone_id'] = os.getenv('WHATSAPP_BUSINESS_PHONE_ID', config.get('whatsapp_business_phone_id', ''))
    config['verify_token'] = os.getenv('VERIFY_TOKEN', config.get('verify_token', ''))

    if not all(config.get(k) for k in ['whatsapp_business_api_token', 'whatsapp_business_phone_id', 'verify_token']):
        print("❌ Error: Faltan variables de configuración cruciales (token, phone_id, o verify_token).")
        return None
    return config

def format_timestamp(ts):
    try:
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ts)))
    except Exception:
        return time.strftime('%Y-%m-%d %H:%M:%S')

# --- Display Functions ---
def display_incoming_message(msg):
    """Displays a formatted summary of a new incoming message."""
    sender = msg.get("from", "Desconocido")
    text_body = "Mensaje sin contenido"
    if msg.get("type") == "text":
        text_body = msg.get("text", {}).get("body", text_body)

    timestamp = format_timestamp(msg.get("timestamp", time.time()))

    print("\n--- 📩 Nuevo Mensaje Recibido ---")
    print(f"  ✅ De: {sender}")
    print(f"  💬 Mensaje: {text_body}")
    print(f"  ⏰ Hora: {timestamp}")
    print("---------------------------------")

def display_status_update(status_data):
    """Displays a formatted summary of a message status update."""
    recipient = status_data.get("recipient_id", "Desconocido")
    status = status_data.get("status", "desconocido").capitalize()
    timestamp = format_timestamp(status_data.get("timestamp", time.time()))

    status_icons = {
        'Sent': '📤',
        'Delivered': '📥',
        'Read': '👀',
        'Failed': '❌'
    }
    icon = status_icons.get(status, '❓')

    print(f"\n--- {icon} Actualización de Estado ---")
    print(f"  [{timestamp}] Para: {recipient}")
    print(f"  Estado: {status}")
    print("---------------------------------")

# --- Core Logic ---
app = Flask(__name__)
incoming_messages = []
statuses = []
messages_lock = threading.Lock()
statuses_lock = threading.Lock()

def send_message_to_api(config, recipient_id, message_body):
    """Sends a message and displays a visual confirmation."""
    url = f"https://graph.facebook.com/v19.0/{config['whatsapp_business_phone_id']}/messages"
    headers = {
        "Authorization": f"Bearer {config['whatsapp_business_api_token']}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message_body},
    }

    print(f"Enviando mensaje a {recipient_id}...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"✅ Mensaje enviado exitosamente a {recipient_id}.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al enviar mensaje: {e}")
        if e.response:
            print(f"   Respuesta de la API: {e.response.json().get('error', {}).get('message', 'Sin detalles')}")

# --- Flask Webhooks ---
@app.route('/api/webhook', methods=['GET'])
def verify_webhook():
    config = app.config['app_config']
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == config.get('verify_token'):
        print("✅ Webhook verificado exitosamente!")
        return challenge, 200
    else:
        print("❌ Error de verificación de webhook.")
        return "Verification token mismatch", 403

@app.route('/api/webhook', methods=['POST'])
def webhook_post():
    data = request.get_json()
    try:
        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})

        if 'messages' in value:
            for message in value['messages']:
                with messages_lock:
                    incoming_messages.append(message)

        if 'statuses' in value:
            for status_data in value['statuses']:
                with statuses_lock:
                    statuses.append(status_data)

    except Exception as e:
        print(f"❌ Error procesando webhook: {e}")

    return "OK", 200

# --- Application Runner ---
def run_flask_app(config):
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.config['app_config'] = config
    port = int(os.getenv("PORT", 3000))
    app.run(port=port, debug=False, use_reloader=False)

def main():
    config = load_config()
    if not config:
        return

    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, args=(config,))
    flask_thread.daemon = True
    flask_thread.start()
    print("🚀 Servidor Flask iniciado en segundo plano.")

    print("\n--- Gemini CLI - WhatsApp Business API ---")
    while True:
        print("\nOpciones:")
        print("  1. Ver mensajes nuevos")
        print("  2. Enviar un mensaje (Modo Test)")
        print("  3. Salir")

        choice = input("Elige una opción: ")

        if choice == '1':
            with messages_lock:
                messages_to_display = list(incoming_messages)
                incoming_messages.clear()
            with statuses_lock:
                statuses_to_display = list(statuses)
                statuses.clear()

            if not messages_to_display and not statuses_to_display:
                print("\nNo hay mensajes nuevos.")
            else:
                for msg in messages_to_display:
                    display_incoming_message(msg)
                for st in statuses_to_display:
                    display_status_update(st)

        elif choice == '2':
            recipient = TEST_MODE_RECIPIENT
            print(f"Enviando mensaje a: {recipient} (Modo Test)")
            text = input("Ingresa tu mensaje: ")
            send_message_to_api(config, recipient, text)

        elif choice == '3':
            print("Saliendo del sistema.")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()
