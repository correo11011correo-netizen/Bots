from flask import Flask, request
import logging
import os
import threading

# Estas listas actuarán como un 'almacén' en memoria para los mensajes y estados.
# En una aplicación más robusta, esto sería reemplazado por una base de datos o un sistema de colas.
incoming_messages = []
statuses = []
messages_lock = threading.Lock()
statuses_lock = threading.Lock()

app = Flask(__name__)

def setup_webhook_routes(config):
    """
    Configura las rutas del webhook en la aplicación Flask.

    Esta función anida las definiciones de las rutas dentro de sí misma para que
    puedan acceder a la variable 'config' que se les pasa.

    Args:
        config (dict): El diccionario de configuración que contiene el 'verify_token'.
    """

    @app.route('/api/webhook', methods=['GET'])
    def verify_webhook():
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
        print("\n>> ¡Webhook POST recibido! Procesando...")
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

def get_new_messages():
    """
    Obtiene y limpia la lista de mensajes entrantes de forma segura.

    Returns:
        list: Una copia de la lista de mensajes recibidos desde la última llamada.
    """
    with messages_lock:
        messages_to_return = list(incoming_messages)
        incoming_messages.clear()
    return messages_to_return

def get_new_statuses():
    """
    Obtiene y limpia la lista de actualizaciones de estado de forma segura.

    Returns:
        list: Una copia de la lista de estados recibidos desde la última llamada.
    """
    with statuses_lock:
        statuses_to_return = list(statuses)
        statuses.clear()
    return statuses_to_return

def run_flask_app(config, port=3000):
    """
    Inicia el servidor Flask en un hilo separado para no bloquear la ejecución.

    Args:
        config (dict): El diccionario de configuración para la app Flask.
        port (int, optional): El puerto en el que correrá el servidor. Defaults to 3000.
    """
    # Deshabilitar logging de Werkzeug para una consola más limpia
    log = logging.getLogger('werkzeug')
    log.disabled = True
    
    app.config['app_config'] = config
    
    # Iniciar Flask en un hilo para no bloquear el programa principal
    flask_thread = threading.Thread(target=lambda: app.run(port=port, debug=False, use_reloader=False))
    flask_thread.daemon = True
    flask_thread.start()
    print(f"🚀 Servidor Flask iniciado en segundo plano en el puerto {port}.")

