import logging
import requests
import os

def send_msg(cfg, to, body):
    # In a minimal setup, we'll just log the message
    logging.info(f"MINIMAL_ENGINE: Sending message to {to}: {body}")
    
    # If you want to integrate with WhatsApp API, you would uncomment and configure this:
    # url = f"https://graph.facebook.com/v19.0/{cfg['phone_id']}/messages"
    # headers = {"Authorization": f"Bearer {cfg['token']}", "Content-Type": "application/json"}
    # payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}}
    # try:
    #     r = requests.post(url, headers=headers, json=payload)
    #     r.raise_for_status()
    #     logging.info(f"✅ Sent to {to}: {body}")
    # except Exception as e:
    #     logging.error(f"❌ Error sending: {e}")

def process_message(cfg, sender, text):
    welcome_message = (
        "👋 ¡Hola! Este es tu bot mínimo.\n"
        "Estoy funcionando y listo para recibir mensajes.\n"
        "Mi principal objetivo es enviarte este mensaje de bienvenida."
    )
    send_msg(cfg, sender, welcome_message)

def load_config():
    # This is a dummy config loader for the minimal engine
    # In a real scenario, this would load from .env or a config file
    return {
        "token": os.getenv("WHATSAPP_BUSINESS_API_TOKEN"),
        "phone_id": os.getenv("WHATSAPP_BUSINESS_PHONE_ID"),
        "verify": os.getenv("VERIFY_TOKEN"),
        "ngrok_public_url": os.getenv("NGROK_PUBLIC_URL"),
    }
