import os
import json
import importlib
import requests
import traceback
import logging
from utils import log_message, setup_logging
from responses import get_response
from welcome_sorteos import send_welcome_sorteos
from flows.whatsapp import handle_whatsapp
from flows.instagram import handle_instagram
from flows.messenger import handle_messenger
from flows.submenu import handle_submenu_entry
from flows.contact import handle_contact
from flows.shop import handle_shop_flow
from flows.gemini import gemini_flow
from flows.db_control import db_control_flow
import flows.state as state

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
                    logging.error(f"Error loading flow '{flow_name}': {e}")
    logging.info(f"Submenu flows loaded: {submenu_flows}")

def load_config():
    return {
        "token": os.getenv("WHATSAPP_BUSINESS_API_TOKEN"),
        "phone_id": os.getenv("WHATSAPP_BUSINESS_PHONE_ID"),
        "verify": os.getenv("VERIFY_TOKEN"),
        "facebook_token": os.getenv("FACEBOOK_TOKEN"),
        "page_id": os.getenv("PAGE_ID"),
        "page_name": os.getenv("PAGE_NAME"),
        "test_recipient_id": os.getenv("TEST_RECIPIENT_ID"),
        "meta_app_id": os.getenv("META_APP_ID"),
        "meta_app_secret": os.getenv("META_APP_SECRET"),
        "ngrok_public_url": os.getenv("NGROK_PUBLIC_URL"),
        "default_test_number": os.getenv("DEFAULT_TEST_NUMBER"),
        "mercadopago_access_token": os.getenv("MERCADOPAGO_ACCESS_TOKEN"),
        "mercadopago_public_key": os.getenv("MERCADOPAGO_PUBLIC_KEY"),
        "mercadopago_client_id": os.getenv("MERCADOPAGO_CLIENT_ID"),
        "mercadopago_client_secret": os.getenv("MERCADOPAGO_CLIENT_SECRET"),
        "mercadopago_webhook_secret": os.getenv("MERCADOPAGO_WEBHOOK_SECRET")
    }

def send_msg(cfg, to, body):
    url = f"https://graph.facebook.com/v19.0/{cfg['phone_id']}/messages"
    headers = {"Authorization": f"Bearer {cfg['token']}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}}
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        logging.info(f"✅ Enviado a {to}: {body}")
    except Exception as e:
        logging.error(f"❌ Error enviando: {e}")

def process_message(cfg, sender, text):
    if not text:
        send_msg(cfg, sender, "⚠️ No se recibió texto válido.")
        return

    # Check for "volver" command
    if text.lower() in ["0", "volver"]:
        # Pop the current state (which would be the one corresponding to the menu the user is currently in)
        # and then pop again to get the *previous* state, as the current state is what we are "volviendo from"
        state.pop_state(sender) # This pops the current state, so now state.get() would return the previous one
        
        # If there's a previous state, then state.get(sender) will return it
        previous_state = state.get(sender) 
        
        if previous_state:
            # Re-dispatch to the handler of the previous state
            if previous_state.get("flow") == "gemini":
                gemini_flow.handle_gemini_chat(cfg, sender, send_msg) # Re-enter gemini chat
            elif previous_state.get("flow") == "sorteos":
                from flows.sorteos.sorteos_flow import handle_sorteo
                handle_sorteo(cfg, sender, send_msg)
            elif previous_state.get("flow") == "prestamos":
                from flows.prestamos.prestamos_flow import handle_prestamo
                handle_prestamo(cfg, sender, send_msg)
            elif previous_state.get("flow") == "referidos":
                from flows.referidos.referidos_flow import handle_referidos
                handle_referidos(cfg, sender, send_msg)
            elif previous_state.get("flow") == "submenu":
                handle_submenu_entry(cfg, sender, send_msg, submenu_flows) # Pass submenu_flows
            elif previous_state.get("flow") == "contact":
                handle_contact(cfg, sender, send_msg)
            elif previous_state.get("flow") == "main_menu": # Explicit flow for main menu if needed
                send_welcome_sorteos(cfg, sender, send_msg)
            else: # Fallback to main menu if flow not recognized
                send_welcome_sorteos(cfg, sender, send_msg)
        else: # No previous state, go to main menu and clear any remaining state
            state.clear(sender) 
            send_welcome_sorteos(cfg, sender, send_msg)
        return

    # Existing state handling for gemini flow (should be before numerical menu dispatch)
    current_state = state.get(sender)
    if current_state and current_state.get("flow") == "gemini":
        gemini_flow.handle_input(cfg, sender, text, send_msg)
        return
    
    # Existing state handling for db_control flow
    if current_state and current_state.get("flow") == "db_control":
        db_control_flow.handle_input(cfg, sender, text, send_msg)
        return

    # Original numerical menu dispatch logic
    from flows.stock.stock_flow import handle_view_stock

    if text == "1":
        handle_view_stock(cfg, sender, send_msg)
    elif text == "2":
        from flows.sorteos.sorteos_flow import handle_sorteo
        state.set_state(sender, {"flow": "sorteos"})
        handle_sorteo(cfg, sender, send_msg)
    elif text == "3":
        from flows.prestamos.prestamos_flow import handle_prestamo
        state.set_state(sender, {"flow": "prestamos"})
        handle_prestamo(cfg, sender, send_msg)
    elif text == "4":
        from flows.referidos.referidos_flow import handle_referidos
        state.set_state(sender, {"flow": "referidos"})
        handle_referidos(cfg, sender, send_msg)
    elif text in ["5", "demo"]: # Changed from 4 to 5
        state.set_state(sender, {"flow": "submenu"})
        handle_submenu_entry(cfg, sender, send_msg, submenu_flows)
    elif text == "6": # Changed from 5 to 6
        state.set_state(sender, {"flow": "contact"})
        handle_contact(cfg, sender, send_msg)
    elif text == "7": # Changed from 6 to 7
        gemini_flow.handle_gemini_chat(cfg, sender, send_msg)
    elif text == "8":
        state.set_state(sender, {"flow": "db_control"})
        db_control_flow.handle_db_control(cfg, sender, send_msg)
    else:
        send_welcome_sorteos(cfg, sender, send_msg)
