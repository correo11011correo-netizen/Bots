import logging
from datetime import datetime

def setup_logging():
    """
    Configura el sistema de logging para registrar eventos en consola y archivo.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("conversations.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def log_message(sender, text):
    """
    Registra cada mensaje recibido en el log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"[{timestamp}] 📩 {sender}: {text}")
