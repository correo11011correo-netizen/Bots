#!/bin/bash

# Make scripts executable
chmod +x run_server.sh
chmod +x run_client.sh

# Start the server in the background
echo "Iniciando el servidor en segundo plano..."
./run_server.sh &
SERVER_PID=$!

echo "Servidor iniciado con PID: $SERVER_PID"
echo "Esperando 10 segundos para que el servidor se inicialice..."
sleep 10

# Retry loop
MAX_RETRIES=5
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "Intento de conexión #$((RETRY_COUNT + 1))..."
    OUTPUT=$(./run_client.sh)
    echo "Respuesta del servidor: $OUTPUT"
    if echo "$OUTPUT" | grep -q '"choices"'; then
        SUCCESS=true
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "No se pudo obtener una respuesta válida. Reintentando en 5 segundos..."
    sleep 5
done

# Show the server log
echo "Mostrando el log del servidor:"
cat server.log

# Clean up
echo "Deteniendo el servidor..."
kill $SERVER_PID

if [ "$SUCCESS" = true ]; then
    echo "Prueba exitosa: Se recibió una respuesta válida del servidor."
    exit 0
else
    echo "Prueba fallida: No se pudo obtener una respuesta válida del servidor después de $MAX_RETRIES intentos."
    exit 1
fi
