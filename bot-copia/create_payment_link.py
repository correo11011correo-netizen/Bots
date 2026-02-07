#!/usr/bin/env python3
import os
import requests
import logging
from dotenv import load_dotenv

# Mapeo in-memory de preference_id a sender_id
pref_id_to_sender = {}

# Cargar token desde archivo .env
load_dotenv(dotenv_path="./.env")
ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    logging.error("❌ [create_payment_link.py] No se encontró MERCADOPAGO_ACCESS_TOKEN en .env")

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}" if ACCESS_TOKEN else "",
    "Content-Type": "application/json"
}

def create_payment_link(amount: float, sender: str):
    if not ACCESS_TOKEN:
        return None, None

    url = "https://api.mercadopago.com/checkout/preferences"
    body = {
        "items": [
            {
                "title": f"Sorteo Ticket ${int(amount)}",
                "quantity": 1,
                "unit_price": amount,
                "currency_id": "ARS"
            }
        ],
        "notification_url": os.getenv("NGROK_PUBLIC_URL") + "/api/mp" # Usar NGROK_PUBLIC_URL para el webhook
    }

    resp = requests.post(url, headers=HEADERS, json=body)
    data = resp.json()

    link = data.get("init_point")
    pref_id = data.get("id")

    if link and pref_id:
        pref_id_to_sender[pref_id] = sender # Almacenar el mapeo
        logging.info(f"✅ [create_payment_link.py] Link generado para ${amount} (sender: {sender}, pref_id: {pref_id}): {link}")
    else:
        logging.error(f"⚠️ [create_payment_link.py] No se generó link para ${amount}. Respuesta: {data}")

    return link, pref_id
