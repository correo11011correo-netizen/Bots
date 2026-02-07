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

CONFIG_FILE = "config/settings.json"
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
    with open(CONFIG_FILE) as f:
        cfg = json.load(f)
    return {
        # WhatsApp
        "token": os.getenv("WHATSAPP_BUSINESS_API_TOKEN", cfg.get("whatsapp_business_api_token")),
        "phone_id": os.getenv("WHATSAPP_BUSINESS_PHONE_ID", cfg.get("whatsapp_business_phone_id")),
        "verify": os.getenv("VERIFY_TOKEN", cfg.get("verify_token")),
        # Messenger
        "facebook_token": os.getenv("FACEBOOK_TOKEN", cfg.get("facebook_token")),
        "page_id": cfg.get("page_id"),
        "page_name": cfg.get("page_name"),
        "test_recipient_id": cfg.get("test_recipient_id"),
        # Otros
        "meta_app_id": cfg.get("meta_app_id"),
        "meta_app_secret": cfg.get("meta_app_secret"),
        "ngrok_public_url": cfg.get("ngrok_public_url"),
        "default_test_number": cfg.get("default_test_number")
    }

def send_msg(cfg, to, body):
    url = f"https://graph.facebook.com/v19.0/{cfg['phone_id']}/messages"
    headers = {"Authorization": f"Bearer {cfg['token']}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}}
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        print(f"✅ Enviado a {to}: {body}")
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

        if text == "/reload":
            load_submenu_flows()
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
                send_msg(cfg, sender, "Opción inválida. Por favor, elige un número del submenú.")
                continue

        if text in ["/start", "hola", "buenas"]:
            clear(sender)
            send_msg(cfg, sender, send_welcome()); continue
        if text in ["menu", "opciones"]:
            clear(sender)
            send_msg(cfg, sender, send_menu_payload()); continue
        if text == "lista":
            clear(sender)
            send_msg(cfg, sender, send_list_menu_payload()); continue

        if text == "1": handle_whatsapp(cfg, sender, send_msg); continue
        if text == "2": handle_instagram(cfg, sender, send_msg); continue
        if text == "3": handle_messenger(cfg, sender, send_msg); continue
        if text in ["4", "demo"]: handle_submenu_entry(cfg, sender, send_msg, submenu_flows); continue
        if text == "5": handle_contact(cfg, sender, send_msg); continue

        send_msg(cfg, sender, get_response(text))
