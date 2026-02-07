#!/bin/bash

echo "🚀 Iniciando el bot..."

# --- Cargar variables de entorno desde .env ---
echo "🔑 Cargando variables de entorno desde .env..."
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Variables de entorno cargadas."
else
    echo "⚠️ Advertencia: No se encontró el archivo .env. Usando valores por defecto si no están definidos."
fi

# --- Verificar si jq está instalado ---
echo "🔍 Verificando dependencia: jq..."
if ! command -v jq &> /dev/null
then
    echo "❌ Error: 'jq' no está instalado."
    echo "Por favor, instala 'jq' para continuar. Ejemplo: sudo apt-get install jq (Debian/Ubuntu) o brew install jq (macOS)."
    exit 1
fi
echo "✅ 'jq' está instalado."

# --- 1. Activar el entorno virtual ---
echo "⚙️ Activando entorno virtual..."
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado."
else
    echo "❌ Error: No se encontró el entorno virtual 'venv'. Por favor, créalo con 'python3 -m venv venv' e instala las dependencias."
    exit 1
fi

# --- 2. Iniciar ngrok en segundo plano ---
# Usar el puerto definido en .env o 5000 por defecto
HTTP_PORT=${PORT:-5000}
echo "🌐 Iniciando ngrok en segundo plano (puerto $HTTP_PORT)..."
# Asegúrate de que ngrok no esté ya corriendo
killall ngrok > /dev/null 2>&1
# Ejecuta ngrok en segundo plano y redirige su salida a un archivo de log
ngrok http $HTTP_PORT --log "ngrok.log" &
NGROK_PID=$!
echo "✅ ngrok iniciado con PID: $NGROK_PID"

# Esperar un momento para que ngrok se inicialice
sleep 5

# --- 3. Obtener la URL pública de ngrok ---
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[] | select(.proto=="https") | .public_url')

if [ -z "$NGROK_URL" ]; then
    echo "❌ Error: No se pudo obtener la URL pública de ngrok. Asegúrate de que ngrok esté correctamente configurado y autenticado."
    echo "Contenido de ngrok.log:"
    cat ngrok.log
    kill $NGROK_PID
    deactivate
    exit 1
fi

echo "✅ URL pública de ngrok obtenida: $NGROK_URL"

# --- 4. Actualizar .env con la URL de ngrok ---
echo "📝 Actualizando NGROK_PUBLIC_URL en .env..."
# Crear .env si no existe
if [ ! -f .env ]; then
    touch .env
fi
# Reemplazar o añadir la línea NGROK_PUBLIC_URL
if grep -q "NGROK_PUBLIC_URL" .env; then
    sed -i "s|^NGROK_PUBLIC_URL=.*|NGROK_PUBLIC_URL=$NGROK_URL|" .env
else
    echo "NGROK_PUBLIC_URL=$NGROK_URL" >> .env
fi
echo "✅ .env actualizado."

# --- 5. Iniciar el servidor Flask ---
echo "💻 Iniciando el servidor Flask (server.py)..."
python3 server.py &
FLASK_PID=$!
echo "✅ Servidor Flask iniciado con PID: $FLASK_PID"

echo "🎉 ¡Bot iniciado y listo para usar!"
echo "Para detener el bot, puedes usar 'kill $NGROK_PID' y 'kill $FLASK_PID' o simplemente cerrar la terminal."
echo "También puedes ejecutar 'killall ngrok' y 'killall python3' para detener ambos procesos."
