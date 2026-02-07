import json
import os
import time
import requests
from flask import Flask, request
import threading
import logging

# --- Configuración de Logging ---
LOG_FILE = os.path.join(os.path.dirname(__file__), 'bot_w_ia.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler() # También envía logs a la consola
    ]
)
# Deshabilitar el logger de werkzeug (servidor Flask) si es demasiado ruidoso
logging.getLogger('werkzeug').setLevel(logging.WARNING)

from llama_cpp import Llama # Importar Llama

# --- Configuración del Modelo de IA ---
# Asegúrate de que esta ruta apunte al modelo descargado en proyecto_ia_local
# LLM_MODEL_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'proyecto_ia_local', 'models')
LLM_MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'proyecto_ia_local', 'models', 'tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf')


# --- Configuration ---
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config', 'settings.json')
TEST_MODE_RECIPIENT = "5493765245980" # Este es el destinatario de prueba para el CLI (ya no usado directamente)
STARTUP_NOTIFICATION_RECIPIENT = "5493765245980" # Nuevo destinatario para la notificación de inicio (tu número)

# --- Helper Functions ---
def load_config():
    """Loads configuration from settings.json and environment variables."""
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    else:
        logging.warning(f"El archivo de configuración no se encontró en {CONFIG_FILE}. Se usarán variables de entorno o valores predeterminados.")

    config['whatsapp_business_api_token'] = os.getenv('WHATSAPP_BUSINESS_API_TOKEN', config.get('whatsapp_business_api_token', ''))
    config['whatsapp_business_phone_id'] = os.getenv('WHATSAPP_BUSINESS_PHONE_ID', config.get('whatsapp_business_phone_id', ''))
    config['verify_token'] = os.getenv('VERIFY_TOKEN', config.get('verify_token', ''))

    if not all(config.get(k) for k in ['whatsapp_business_api_token', 'whatsapp_business_phone_id', 'verify_token']):
        logging.critical("Faltan variables de configuración cruciales (token, phone_id, o verify_token). El bot no puede funcionar sin ellas.")
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

    logging.info(f"Enviando mensaje a {recipient_id}...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logging.info(f"Mensaje enviado exitosamente a {recipient_id}.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al enviar mensaje a {recipient_id}: {e}")
        if e.response:
            logging.error(f"Respuesta de la API: {e.response.json().get('error', {}).get('message', 'Sin detalles')}")

# --- Flask Webhooks ---
@app.route('/api/webhook', methods=['GET'])
def verify_webhook():
    config = app.config['app_config']
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == config.get('verify_token'):
        logging.info("Webhook verificado exitosamente!")
        return challenge, 200
    else:
        logging.error("Error de verificación de webhook.")
        return "Verification token mismatch", 403

@app.route('/api/webhook', methods=['POST'])
def webhook_post():
    data = request.get_json()
    config = app.config['app_config']
    llm = app.config.get('llm_model') # Obtener la instancia del LLM

    try:
        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})

        if 'messages' in value:
            for message in value['messages']:
                display_incoming_message(message) # Mostrar mensaje entrante en consola
                sender_id = message.get("from")
                if message.get("type") == "text" and sender_id:
                    user_message = message.get("text", {}).get("body", "")
                    logging.info(f"Mensaje recibido de {sender_id}: {user_message}")
                    
                    if llm:
                        logging.info(f"Generando respuesta IA para {sender_id}...")
                        messages_for_llm = [
                            {"role": "system", "content": "Eres un asistente de IA amable y conciso que responde en español. Responde de forma útil y breve."},
                            {"role": "user", "content": user_message}
                        ]
                        
                        llm_response = ""
                        try:
                            output_stream = llm.create_chat_completion(
                                messages=messages_for_llm,
                                temperature=0.7,
                                max_tokens=200,
                                stop=["<|endoftext|>", "<|user|>", "<|assistant|>"],
                                stream=True
                            )
                            for chunk in output_stream:
                                delta = chunk['choices'][0]['delta']
                                if 'content' in delta:
                                    llm_response += delta['content']
                            logging.info(f"Respuesta IA generada para {sender_id}: {llm_response[:50]}...") # Loguear parte de la respuesta
                            send_message_to_api(config, sender_id, llm_response)
                        except Exception as e:
                            logging.error(f"Error al generar respuesta con LLM para {sender_id}: {e}", exc_info=True)
                            send_message_to_api(config, sender_id, "Lo siento, tengo problemas para responder en este momento.")
                    else:
                        logging.warning("LLM no cargado. No se puede responder automáticamente.")
                        send_message_to_api(config, sender_id, "Lo siento, el sistema de IA no está disponible en este momento.")


        if 'statuses' in value:
            for status_data in value['statuses']:
                display_status_update(status_data) # Mostrar actualización de estado

    except Exception as e:
        logging.error(f"Error procesando webhook: {e}", exc_info=True)

    return "OK", 200

# --- Application Runner ---
def run_flask_app(config, llm_model):
    log = logging.getLogger('werkzeug')
    log.disabled = True
    app.config['app_config'] = config
    app.config['llm_model'] = llm_model
    port = int(os.getenv("PORT", 3000))
    app.run(port=port, debug=False, use_reloader=False)

def main():
    config = load_config()
    if not config:
        return

    # --- Cargar el Modelo de IA ---
    llm_model = None
    if os.path.exists(LLM_MODEL_PATH):
        logging.info("Cargando el modelo de IA... Esto puede tardar unos segundos.")
        try:
            llm_model = Llama(
                model_path=LLM_MODEL_PATH,
                n_ctx=2048,       # Ajustado para que coincida con n_ctx_train del modelo (2048)
                                  # Esto elimina el mensaje de advertencia, pero podría aumentar ligeramente
                                  # el uso de RAM en comparación con n_ctx=1024.
                n_threads=os.cpu_count() or 4, # Usar todos los hilos de CPU disponibles o 4 por defecto
                n_gpu_layers=0,   # 0 para forzar CPU. Si tienes GPU y compilaste llama-cpp-python con soporte
                                  # para ella (ej. CUDA, CLBlast, Metal), podrías intentar un valor > 0.
                                  # Ejemplo: n_gpu_layers=99 para intentar usar todas las capas en GPU.
                verbose=False     # Reduce la verbosidad de llama_cpp
            )
            logging.info("Modelo de IA cargado exitosamente.")
        except Exception as e:
            logging.critical(f"Error al cargar el modelo de IA: {e}", exc_info=True)
            logging.critical("Asegúrate de que el modelo esté descargado y el archivo no esté corrupto.")
            return
    else:
        logging.critical(f"Error: No se encontró el modelo de IA en '{LLM_MODEL_PATH}'.")
        logging.critical("Asegúrate de haber descargado el modelo ejecutando el script './proyecto_ia_local/download_model.sh' y que la ruta sea correcta.")
        return

    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, args=(config, llm_model,))
    flask_thread.daemon = True
    flask_thread.start()
    logging.info("Servidor Flask iniciado en segundo plano para webhook.")
    logging.info("El bot de IA de WhatsApp está listo para recibir mensajes.")
    
    # Enviar notificación de inicio
    if STARTUP_NOTIFICATION_RECIPIENT:
        logging.info(f"Enviando notificación de inicio a {STARTUP_NOTIFICATION_RECIPIENT}...")
        send_message_to_api(config, STARTUP_NOTIFICATION_RECIPIENT, "✅ Bot de IA iniciado y funcionando correctamente.")

    logging.info("Para detener el bot, presiona Ctrl+C.")
    
    # Mantener el hilo principal vivo para que el hilo de Flask continúe
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Deteniendo el bot de IA de WhatsApp.")
    

if __name__ == "__main__":
    main()
