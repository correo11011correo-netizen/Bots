#!/usr/bin/env python3
import json
import requests

# Cargar configuración desde config/settings.json
with open("config/settings.json") as f:
    cfg = json.load(f)

ACCESS_TOKEN = cfg.get("whatsapp_token")
WABA_ID = cfg.get("waba_id")  # WhatsApp Business Account ID

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
