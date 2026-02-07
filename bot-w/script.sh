#!/bin/bash

# Kill any existing ngrok processes to ensure a clean start
pkill ngrok

# Kill any existing Flask process on port 3000
fuser -k 3000/tcp

# Define the path to ngrok executable
NGROK_PATH="./config/ngrok"
CONFIG_DIR="./config"

# --- Step 1: Check for ngrok and instruct user if not found ---
if [ ! -f "$NGROK_PATH" ]; then
    echo "--------------------------------------------------------------------------------"
    echo "¡Advertencia! ngrok no se encuentra en el directorio './config/'."
    echo "Por favor, descarga ngrok desde https://ngrok.com/download"
    echo "Extrae el ejecutable 'ngrok' directamente en el directorio './config/'."
    echo "Asegúrate de que tiene permisos de ejecución: chmod +x $NGROK_PATH"
    echo "--------------------------------------------------------------------------------"
    exit 1
fi

# Ensure ngrok has execute permissions
chmod +x "$NGROK_PATH"

# --- Step 2: Start ngrok and capture the public URL ---
echo "Iniciando ngrok para exponer el puerto 3000..."
NGROK_LOG="/tmp/ngrok.log"
"$NGROK_PATH" http 3000 > "$NGROK_LOG" 2>&1 &
NGROK_PID=$!

sleep 5

MAX_ATTEMPTS=15
WAIT_INTERVAL=2
PUBLIC_URL=""

for i in $(seq 1 $MAX_ATTEMPTS); do
    TUNNELS_JSON=$(curl -s http://127.0.0.1:4040/api/tunnels)
    PUBLIC_URL=$(echo "$TUNNELS_JSON" | jq -r '.tunnels[0].public_url' 2>/dev/null)

    if [ -n "$PUBLIC_URL" ] && [ "$PUBLIC_URL" != "null" ]; then
        break
    fi
    sleep "$WAIT_INTERVAL"
done

if [ -z "$PUBLIC_URL" ] || [ "$PUBLIC_URL" = "null" ]; then
    echo "Error: No se pudo obtener la URL pública de ngrok."
    tail -n 10 "$NGROK_LOG" >&2
    kill "$NGROK_PID"
    exit 1
fi

echo "ngrok iniciado. URL pública: $PUBLIC_URL"
echo "--------------------------------------------------------------------------------"
echo "Por favor, configura esta URL ($PUBLIC_URL/api/webhook) en la configuración del Webhook de WhatsApp Business API."
echo "También, asegúrate de que tu VERIFY_TOKEN sea el mismo que estableciste."
echo "--------------------------------------------------------------------------------"

# --- Step 3: Load configuration from JSON and export as environment variables ---
echo "Cargando configuración desde config/settings.json..."
CONFIG_FILE="./config/settings.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: El archivo de configuración no se encuentra en $CONFIG_FILE"
    kill "$NGROK_PID"
    exit 1
fi

export WHATSAPP_BUSINESS_API_TOKEN=$(jq -r '.whatsapp_business_api_token' "$CONFIG_FILE")
export WHATSAPP_BUSINESS_PHONE_ID=$(jq -r '.whatsapp_business_phone_id' "$CONFIG_FILE")
export VERIFY_TOKEN=$(jq -r '.verify_token' "$CONFIG_FILE")
export DEFAULT_TEST_NUMBER="5493765245980"

if [ -z "$WHATSAPP_BUSINESS_API_TOKEN" ] || [ -z "$WHATSAPP_BUSINESS_PHONE_ID" ] || [ -z "$VERIFY_TOKEN" ]; then
    echo "Error: Variables requeridas faltantes en $CONFIG_FILE"
    kill "$NGROK_PID"
    exit 1
fi

echo "Configuración cargada y exportada como variables de entorno."
echo "--------------------------------------------------------------------------------"

# --- Step 4: Run main.py ---
echo "Iniciando la aplicación Python (main.py)..."
source venv/bin/activate
python main.py
APP_EXIT_CODE=$?

echo "Aplicación Python finalizada con código $APP_EXIT_CODE."

# Clean up ngrok process on exit
kill "$NGROK_PID"
echo "ngrok terminado."
