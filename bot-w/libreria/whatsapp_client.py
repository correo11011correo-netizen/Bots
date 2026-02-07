import requests
import json
import logging

# --- Configuración del Logger ---
# Esto ayuda a tener un registro más claro, especialmente para errores.
logger = logging.getLogger(__name__)

def _send_whatsapp_request(config, payload):
    """
    Función interna genérica para enviar peticiones a la API de WhatsApp.
    Maneja la autenticación y la comunicación base.
    """
    token = config.get('whatsapp_business_api_token')
    phone_id = config.get('whatsapp_business_phone_id')
    
    if not token or not phone_id:
        logger.error("❌ Error: 'whatsapp_business_api_token' o 'whatsapp_business_phone_id' no encontrados en la configuración.")
        return False, {"error": "Token o ID de teléfono no configurados."}

    url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    recipient_id = payload.get("to", "desconocido")
    logger.info(f"Enviando mensaje de tipo '{payload.get('type')}' a {recipient_id}...")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Si la petición no fue exitosa (ej: 400, 401, 403, 404, 500), lanza una excepción.
        response.raise_for_status()
        
        logger.info(f"✅ Mensaje enviado exitosamente a {recipient_id}.")
        return True, response.json()

    except requests.exceptions.HTTPError as e:
        # Aquí está la clave: intentamos decodificar el JSON del error.
        error_details = "Sin detalles en la respuesta."
        try:
            error_response_json = e.response.json()
            error_details = error_response_json.get("error", {})
            logger.error(f"❌ Error HTTP al enviar mensaje: {e.response.status_code} {e.response.reason}")
            logger.error(f"   Detalles de la API: {error_details}")
        except json.JSONDecodeError:
            error_details = e.response.text
            logger.error(f"❌ Error HTTP al enviar mensaje: {e.response.status_code} {e.response.reason}")
            logger.error(f"   Respuesta de la API (no es JSON): {error_details}")
            
        return False, {"error": str(e), "details": error_details}
        
    except requests.exceptions.RequestException as e:
        # Para otros errores (ej: problemas de red)
        logger.error(f"❌ Error de conexión al enviar mensaje: {e}")
        return False, {"error": str(e), "details": "Error de red o conexión."}

def send_text_message(config, recipient_id, message_body):
    """
    Envía un mensaje de texto simple.
    """
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message_body},
    }
    return _send_whatsapp_request(config, payload)

def send_interactive_message(config, recipient_id, interactive_data):
    """
    Envía un mensaje interactivo (con botones, listas, etc.).
    """
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_id,
        "type": "interactive",
        "interactive": interactive_data,
    }
    return _send_whatsapp_request(config, payload)

# Por retrocompatibilidad con bot_refactorizado.py
send_message_to_api = send_text_message
