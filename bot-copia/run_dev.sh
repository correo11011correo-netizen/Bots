#!/bin/bash
echo "🚀 Iniciando servidor Flask en modo desarrollo..."
echo "📝 Logging configurado."

# Cargar variables de entorno desde .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "🔑 Variables de entorno cargadas desde .env:"
  echo "   - MERCADOPAGO_ACCESS_TOKEN=${MERCADOPAGO_ACCESS_TOKEN:+[OK]}"
  echo "   - MERCADOPAGO_WEBHOOK_SECRET=${MERCADOPAGO_WEBHOOK_SECRET:+[OK]}"
  echo "   - WHATSAPP_BUSINESS_API_TOKEN=${WHATSAPP_BUSINESS_API_TOKEN:+[OK]}"
else
  echo "⚠️ No se encontró archivo .env"
fi

# Mostrar qué script se está ejecutando
echo "📂 Ejecutando server.py con engine.py como backend"
echo "   - Archivo principal: server.py"
echo "   - Motor de flujos:  engine.py"

# Lanzar servidor Flask
source /home/adrian/venvs/aider/bin/activate
python3 server.py
