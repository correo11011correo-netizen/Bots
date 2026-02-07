import logging
import os
from datetime import datetime

def get_user_data_path(sender):
    """
    Returns the path to the user's data directory, creating it if it doesn't exist.
    """
    path = os.path.join("chats", sender)
    os.makedirs(path, exist_ok=True)
    return path

def setup_logging():
    """
    Configura el sistema de logging para registrar eventos en consola y archivo.
    """
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(os.path.join("logs", "conversations.log"), encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def log_message(sender, text):
    """
    Registra cada mensaje recibido en el log general y en el log del usuario.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    general_log_message = f"[{timestamp}] 📩 {sender}: {text}"
    logging.info(general_log_message)

    user_chat_path = os.path.join(get_user_data_path(sender), "chat.log")
    with open(user_chat_path, "a", encoding="utf-8") as f:
        f.write(general_log_message + "\n")
