import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'settings.json')
TEST_MODE_RECIPIENT = "5493765245980"

def load_config():
    """
    Carga la configuración desde settings.json y variables de entorno.
    """
    config = {}
    # Intentar cargar desde el archivo de configuración
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Error: El archivo de configuración {CONFIG_FILE} no es un JSON válido.")
            return None
    else:
        print(f"⚠️ Advertencia: El archivo de configuración no se encontró en {CONFIG_FILE}. Se intentará usar variables de entorno.")

    # Sobreescribir/establecer con variables de entorno si están presentes
    config['whatsapp_business_api_token'] = os.getenv('WHATSAPP_BUSINESS_API_TOKEN', config.get('whatsapp_business_api_token', ''))
    config['whatsapp_business_phone_id'] = os.getenv('WHATSAPP_BUSINESS_PHONE_ID', config.get('whatsapp_business_phone_id', ''))
    config['verify_token'] = os.getenv('VERIFY_TOKEN', config.get('verify_token', ''))

    # Verificar que las configuraciones críticas existan
    if not all(config.get(k) for k in ['whatsapp_business_api_token', 'whatsapp_business_phone_id', 'verify_token']):
        print("❌ Error: Faltan variables de configuración cruciales (whatsapp_business_api_token, whatsapp_business_phone_id, o verify_token).")
        return None
    return config
