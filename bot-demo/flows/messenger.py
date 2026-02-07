import requests

def handle_messenger(cfg, data, send_func=None):
    """
    Maneja eventos de Messenger: loguea mensajes y envía respuesta automática.
    Ignora eventos de tipo delivery/echo.
    """
    if "entry" not in data:
        return

    for entry in data["entry"]:
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]

            # Mensajes entrantes
            if "message" in event:
                text = event["message"].get("text", "")
                print(f"📩 Messenger mensaje de {sender_id}: {text}")

                reply_text = (
                    "👋 ¡Bienvenido al Bot de Messenger!\n"
                    "- Atención en Facebook Page\n"
                    "- Catálogos interactivos en chat\n"
                    "- Scripts de bienvenida y derivaciones\n\n"
                    "¿Querés una demo? Escribí 'demo'."
                )

                if send_func:
                    send_func(cfg, sender_id, reply_text)
                else:
                    token = cfg.get("facebook_token")
                    if token:
                        send_message(token, sender_id, reply_text, cfg)
                    else:
                        print("❌ No se encontró 'facebook_token' en cfg.")
            else:
                # Ignorar delivery/echo sin imprimir JSON completo
                print(f"⚠️ Evento Messenger sin 'message' (delivery/echo) de {sender_id}")

def send_message(token, recipient_id, text, cfg=None):
    """
    Envía respuesta automática a Messenger usando Graph API.
    Si el recipient_id es inválido (ej. page_id), usa test_recipient_id.
    """
    if cfg:
        if recipient_id == cfg.get("page_id") or not recipient_id:
            recipient_id = cfg.get("test_recipient_id")

    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": token}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }

    try:
        resp = requests.post(url, params=params, json=payload)
        print(f"➡️ Respuesta enviada a {recipient_id} | Status: {resp.status_code}")
    except Exception as e:
        print(f"❌ Error enviando mensaje a Messenger: {e}")
