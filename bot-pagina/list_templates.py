#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("WHATSAPP_BUSINESS_API_TOKEN")
WABA_ID = os.getenv("WHATSAPP_BUSINESS_PHONE_ID")

url = f"https://graph.facebook.com/v19.0/{WABA_ID}/message_templates"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

resp = requests.get(url, headers=headers)
data = resp.json()

# Mostrar solo las plantillas aprobadas en formato tabla simple
print("📋 Plantillas disponibles:")
for tpl in data.get("data", []):
    name = tpl.get("name")
    lang = tpl.get("language")
    status = tpl.get("status")
    print(f"- {name} ({lang}) → {status}")
