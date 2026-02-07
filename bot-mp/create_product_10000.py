#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

# Colores ANSI
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

# Cargar token desde archivo .env
load_dotenv(dotenv_path="./.env")

ACCESS_TOKEN = os.getenv("acces_token")
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def create_payment_link():
    url = "https://api.mercadopago.com/checkout/preferences"

    body = {
        "items": [
            {
                "title": "Producto de ejemplo - Notebook",
                "quantity": 1,
                "unit_price": 10000.0,
                "currency_id": "ARS"
            }
        ]
    }

    resp = requests.post(url, headers=HEADERS, json=body).json()

    # Extraer datos clave
    item = resp.get("items", [{}])[0]
    title = item.get("title", "N/A")
    qty = item.get("quantity", "N/A")
    price = item.get("unit_price", "N/A")
    currency = item.get("currency_id", "N/A")
    link = resp.get("init_point")
    sandbox_link = resp.get("sandbox_init_point")
    pref_id = resp.get("id")
    date_created = resp.get("date_created")

    # Mostrar resumen visual
    print(CYAN + "\n🎯 Producto:" + RESET)
    print(f"   📝 Título: {title}")
    print(f"   📦 Cantidad: {qty}")
    print(f"   💲 Precio: {price} {currency}")

    print(MAGENTA + "\n🆔 Preferencia:" + RESET)
    print(f"   ID: {pref_id}")
    print(f"   Fecha creación: {date_created}")

    print(GREEN + "\n✅ Link de pago generado:" + RESET)
    print(f"   🔗 {link}")
    print(YELLOW + f"   🧪 Sandbox: {sandbox_link}" + RESET)

    # Guardar link en archivo
    with open("links.txt", "a") as f:
        f.write(f"{pref_id} | {title} | {qty} | {price} {currency} | {link}\n")

    print(GREEN + "\n📂 Link guardado en links.txt" + RESET)

if __name__ == "__main__":
    create_payment_link()
