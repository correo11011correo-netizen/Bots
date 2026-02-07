import os
import json
import importlib
import requests
from utils import log_message, setup_logging
from responses import get_response
from welcome import send_welcome
from menus.main_menu import send_menu_payload
from menus.services_menu import send_list_menu_payload
from flows.whatsapp import handle_whatsapp
from flows.instagram import handle_instagram
from flows.messenger import handle_messenger
from flows.submenu import handle_submenu_entry
from flows.contact import handle_contact
from flows.shop import handle_shop_flow
from flows.state import get, clear
import db_manager # Added import

processed_message_ids = set()
submenu_flows = {}

def load_submenu_flows():
    global submenu_flows
    submenu_flows = {}
    flows_dir = "flows"
    for flow_name in os.listdir(flows_dir):
        flow_path = os.path.join(flows_dir, flow_name)
        submenu_json_path = os.path.join(flow_path, "submenu.json")
        if os.path.isdir(flow_path) and os.path.exists(submenu_json_path):
            with open(submenu_json_path) as f:
                try:
                    flow_config = json.load(f)
                    module_name, func_name = flow_config["entry_point"].rsplit('.', 1)
                    module = importlib.import_module(f"flows.{flow_name}.{module_name}")
                    entry_func = getattr(module, func_name)
                    submenu_flows[str(len(submenu_flows) + 1)] = {
                        "text": flow_config["option_text"],
                        "handler": entry_func
                    }
                except Exception as e:
                    print(f"Error loading flow '{flow_name}': {e}")
    print("Submenu flows loaded:", submenu_flows)

def load_config():
    return {
        # WhatsApp
        "token": os.getenv("WHATSAPP_BUSINESS_API_TOKEN"),
        "phone_id": os.getenv("WHATSAPP_BUSINESS_PHONE_ID"),
        "verify": os.getenv("VERIFY_TOKEN"),
        # Messenger
        "facebook_token": os.getenv("FACEBOOK_TOKEN"),
        "page_id": os.getenv("PAGE_ID"),
        "page_name": os.getenv("PAGE_NAME"),
        "test_recipient_id": os.getenv("TEST_RECIPIENT_ID"),
        # Otros
        "meta_app_id": os.getenv("META_APP_ID"),
        "meta_app_secret": os.getenv("META_APP_SECRET"),
        "ngrok_public_url": os.getenv("NGROK_PUBLIC_URL"),
        "default_test_number": os.getenv("DEFAULT_TEST_NUMBER")
    }

def send_msg(cfg, to, body):
    url = f"https://graph.facebook.com/v19.0/{cfg['phone_id']}/messages"
    headers = {"Authorization": f"Bearer {cfg['token']}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}}
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        print(f"✅ Enviado a {to}: {body}")
        # Message sent by bot, record it
        db_manager.add_message(to, 'bot', body) # Added for outgoing messages
    except Exception as e:
        print(f"❌ Error enviando: {e}")

def process_message(cfg, data):
    for msg in data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", []):
        text_raw = msg.get("text", {}).get("body", "")
        text = text_raw.strip().lower()
        sender = msg.get("from")
        message_id = msg.get("id")
        if message_id in processed_message_ids:
            log_message(sender, f"Duplicate message_id {message_id} received, ignoring.")
            continue
        processed_message_ids.add(message_id)
        log_message(sender, text_raw)
        db_manager.add_message(sender, 'client', text_raw) # Added for incoming messages

        if db_manager.get_conversation_status(sender):
            print(f"Human is intervening in conversation with {sender}. Bot will not auto-respond.")
            continue # Skip all further bot auto-response logic for this message

        if text == "/reload":
            load_submenu_flows()
            db_manager.add_message(sender, 'bot', "✅ Flujos de submenú recargados.") # Added
            send_msg(cfg, sender, "✅ Flujos de submenú recargados."); continue

        if handle_shop_flow(cfg, sender, text, send_msg):
            continue

        state = get(sender)
        if state and state.get("flow") == "submenu":
            if text in submenu_flows:
                handler = submenu_flows[text]["handler"]
                clear(sender)
                handler(cfg, sender, send_msg)
                continue
            else:
                response_body = "Opción inválida. Por favor, elige un número del submenú."
                db_manager.add_message(sender, 'bot', response_body) # Added
                send_msg(cfg, sender, response_body); continue

        if text in ["/start", "hola", "buenas"]:
            clear(sender)
            response_body = send_welcome()
            db_manager.add_message(sender, 'bot', response_body) # Added
            send_msg(cfg, sender, response_body); continue
        if text in ["menu", "opciones"]:
            clear(sender)
            response_body = send_menu_payload()
            db_manager.add_message(sender, 'bot', response_body) # Added
            send_msg(cfg, sender, response_body); continue
        if text == "lista":
            clear(sender)
            response_body = send_list_menu_payload()
            db_manager.add_message(sender, 'bot', response_body) # Added
            send_msg(cfg, sender, response_body); continue

        if text == "1": handle_whatsapp(cfg, sender, send_msg); continue
        if text == "2": handle_instagram(cfg, sender, send_msg); continue
        if text == "3": handle_messenger(cfg, sender, send_msg); continue
        if text in ["4", "demo"]: handle_submenu_entry(cfg, sender, send_msg, submenu_flows); continue
        if text == "5": handle_contact(cfg, sender, send_msg); continue

        response_body = get_response(text)
        db_manager.add_message(sender, 'bot', response_body) # Added
        send_msg(cfg, sender, response_body)

