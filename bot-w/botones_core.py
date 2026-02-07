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
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    else:
        print(f"⚠️ Advertencia: El archivo de configuración no se encontró en {CONFIG_FILE}.")
    config['whatsapp_business_api_token'] = os.getenv('WHATSAPP_BUSINESS_API_TOKEN', config.get('whatsapp_business_api_token', ''))
    config['whatsapp_business_phone_id'] = os.getenv('WHATSAPP_BUSINESS_PHONE_ID', config.get('whatsapp_business_phone_id', ''))
    config['verify_token'] = os.getenv('VERIFY_TOKEN', config.get('verify_token', ''))
    if not all(config.get(k) for k in ['whatsapp_business_api_token','whatsapp_business_phone_id','verify_token']):
        print("❌ Error: Faltan variables de configuración cruciales.")
        return None
    return config

def format_timestamp(ts):
    try:
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ts)))
    except Exception:
        return time.strftime('%Y-%m-%d %H:%M:%S')

def display_incoming_message(msg):
    sender = msg.get("from", "Desconocido")
    text_body = msg.get("text", {}).get("body", "Mensaje sin contenido")
    timestamp = format_timestamp(msg.get("timestamp", time.time()))
    print("\n--- 📩 Nuevo Mensaje Recibido ---")
    print(f"  ✅ De: {sender}")
    print(f"  💬 Mensaje: {text_body}")
    print(f"  ⏰ Hora: {timestamp}")
    print("---------------------------------")

def display_status_update(status_data):
    recipient = status_data.get("recipient_id", "Desconocido")
    status = status_data.get("status", "desconocido").capitalize()
    timestamp = format_timestamp(status_data.get("timestamp", time.time()))
    status_icons = {'Sent':'📤','Delivered':'📥','Read':'👀','Failed':'❌'}
    icon = status_icons.get(status, '❓')
    print(f"\n--- {icon} Actualización de Estado ---")
    print(f"  [{timestamp}] Para: {recipient}")
    print(f"  Estado: {status}")
    print("---------------------------------")

# --- Flask App ---
app = Flask(__name__)
incoming_messages = []
statuses = []
messages_lock = threading.Lock()
statuses_lock = threading.Lock()

def send_message_to_api(config, recipient_id, message_body):
    url = f"https://graph.facebook.com/v19.0/{config['whatsapp_business_phone_id']}/messages"
    headers = {"Authorization": f"Bearer {config['whatsapp_business_api_token']}", "Content-Type": "application/json"}
    payload = {"messaging_product":"whatsapp","to":recipient_id,"type":"text","text":{"body":message_body}}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"✅ Mensaje enviado a {recipient_id}.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al enviar mensaje: {e}")

def send_test_buttons(config, recipient_id):
    url = f"https://graph.facebook.com/v19.0/{config['whatsapp_business_phone_id']}/messages"
    headers = {"Authorization": f"Bearer {config['whatsapp_business_api_token']}", "Content-Type": "application/json"}
    payload = {
        "messaging_product":"whatsapp","to":recipient_id,"type":"interactive",
        "interactive":{"type":"button","body":{"text":"Elige una opción:"},
        "action":{"buttons":[
            {"type":"reply","reply":{"id":"btn1","title":"Ver menú"}},
            {"type":"reply","reply":{"id":"btn2","title":"Promoción"}},
            {"type":"reply","reply":{"id":"btn3","title":"Contacto"}}
        ]}}}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("✅ Botones enviados.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al enviar botones: {e}")

def send_test_link(config, recipient_id):
    url = f"https://graph.facebook.com/v19.0/{config['whatsapp_business_phone_id']}/messages"
    headers = {"Authorization": f"Bearer {config['whatsapp_business_api_token']}", "Content-Type": "application/json"}
    payload = {"messaging_product":"whatsapp","to":recipient_id,"type":"text","text":{"body":"Visita nuestro sitio web: https://tusitio.com"}}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print("✅ Link enviado.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al enviar link: {e}")

@app.route('/api/webhook', methods=['GET'])
def verify_webhook():
    config = app.config['app_config']
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == config.get('verify_token'):
        print("✅ Webhook verificado!")
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

def run_flask_app(config):
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.config['app_config'] = config
    port = int(os.getenv("PORT", 3000))
    app.run(port=port, debug=False, use_reloader=False)
