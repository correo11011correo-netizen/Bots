import sqlite3
import os
import sys
from datetime import datetime
import requests # For sending messages via bot-pagina

# --- Database Path (replicated from bot-pagina/db_manager.py) ---
# Assuming bot-pagina and bot-dashboard are siblings in the /home/adrian directory
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bot-dashboard', 'backend')
DB_PATH = os.path.join(DB_DIR, 'bot_dashboard.db')
BOT_PAGINA_SEND_URL = "http://localhost:5000/api/send_message_from_dashboard"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_main_menu():
    """Displays the main menu of the CLI chat manager."""
    clear_screen()
    print("=== Terminal Chat Manager ===")
    print("1. Ver Chats")
    print("2. Salir")
    print("=============================")

def get_conversations():
    """Retrieves all conversations with last message and intervention status."""
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
    conversations = cursor.fetchall()
    conn.close()
    return conversations

def display_conversations(conversations):
    """Displays a list of conversations."""
    clear_screen()
    print("=== Chats Activos ===")
    if not conversations:
        print("No hay conversaciones activas.")
        print("---------------------")
        return

    for i, conv in enumerate(conversations):
        status = "HUMANO" if conv['is_human_intervening'] else "BOT"
        last_msg = conv['last_message_content'] if conv['last_message_content'] else "No hay mensajes"
        name = conv['name'] if conv['name'] else conv['phone_number']
        print(f"{i+1}. {name} ({status}) - Último: '{last_msg}'")
    print("---------------------")

def get_messages_for_contact(phone_number):
    """Retrieves messages for a specific phone number."""
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
    messages = cursor.fetchall()
    conn.close()
    return messages

def display_chat_history(contact_info, messages):
    """Displays the chat history for a selected contact."""
    clear_screen()
    print(f"=== Chat con {contact_info['name'] if contact_info['name'] else contact_info['phone_number']} ===")
    print(f"Estado de intervención: {'HUMANO' if contact_info['is_human_intervening'] else 'BOT'}")
    print("---------------------------------")
    for msg in messages:
        timestamp = datetime.strptime(msg['timestamp'], '%Y-%m-%d %H:%M:%S.%f').strftime('%H:%M:%S')
        sender_label = "Tú" if msg['sender'] == 'human' else msg['sender'].capitalize()
        print(f"[{timestamp}] {sender_label}: {msg['content']}")
    print("---------------------------------")

def send_message_via_bot(phone_number, message_content):
    """Sends a message using the bot-pagina's API."""
    try:
        response = requests.post(
            BOT_PAGINA_SEND_URL,
            json={"phone_number": phone_number, "message": message_content}
        )
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        print(f"✅ Mensaje enviado a {phone_number}.")
        # Optionally, update local DB copy of this message as 'human' via db_manager (if integrated)
        # However, bot-pagina's endpoint already records it, so no need to duplicate here.
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al enviar mensaje a {phone_number} a través del bot: {e}")

def set_human_intervention_status(phone_number, status):
    """Sets the human intervention status for a conversation."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE conversations
         SET is_human_intervening = ?, last_updated = ?
         WHERE contact_id = (SELECT id FROM contacts WHERE phone_number = ?)""",
        (1 if status else 0, datetime.now(), phone_number)
    )
    conn.commit()
    conn.close()
    print(f"Estado de intervención para {phone_number} cambiado a {'HUMANO' if status else 'BOT'}.")

def manage_chat(contact_info):
    """Allows managing a specific chat."""
    while True:
        messages = get_messages_for_contact(contact_info['phone_number'])
        display_chat_history(contact_info, messages)

        print("\nOpciones:")
        print("1. Responder")
        print("2. Cambiar estado de intervención")
        print("3. Actualizar Chat")
        print("4. Volver al menú principal")

        choice = input("Elige una opción: ")

        if choice == '1':
            message = input("Escribe tu mensaje: ")
            send_message_via_bot(contact_info['phone_number'], message)
            # Re-fetch messages to show the sent message
            # messages = get_messages_for_contact(contact_info['phone_number'])
            # display_chat_history(contact_info, messages)
            input("Presiona Enter para continuar...")
        elif choice == '2':
            current_status = contact_info['is_human_intervening']
            new_status = not bool(current_status)
            set_human_intervention_status(contact_info['phone_number'], new_status)
            contact_info['is_human_intervening'] = new_status # Update local copy
            input("Presiona Enter para continuar...")
        elif choice == '3':
            # Just re-loop to refresh
            pass
        elif choice == '4':
            break
        else:
            print("Opción inválida. Intenta de nuevo.")
            input("Presiona Enter para continuar...")

def main():
    """Main function to run the CLI chat manager."""
    while True:
        display_main_menu()
        choice = input("Elige una opción: ")

        if choice == '1':
            conversations = get_conversations()
            if not conversations:
                print("\nNo hay conversaciones activas. Presiona Enter para volver.")
                input()
                continue
            
            display_conversations(conversations)
            chat_choice = input("Elige el número del chat para gestionar (o 'q' para volver): ")
            if chat_choice.lower() == 'q':
                continue
            
            try:
                chat_index = int(chat_choice) - 1
                if 0 <= chat_index < len(conversations):
                    manage_chat(conversations[chat_index])
                else:
                    print("Número de chat inválido.")
                    input("Presiona Enter para continuar...")
            except ValueError:
                print("Entrada inválida.")
                input("Presiona Enter para continuar...")

        elif choice == '2':
            sys.exit("Saliendo del Chat Manager.")
        else:
            print("Opción inválida. Intenta de nuevo.")
            input("Presiona Enter para continuar...")

if __name__ == '__main__':
    main()
