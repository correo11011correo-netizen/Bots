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

# Run the client
echo "Ejecutando el cliente para enviar una petición..."
./run_client.sh

# Show the server log
echo "Mostrando el log del servidor:"
cat server.log

# Clean up
echo "Deteniendo el servidor..."
kill $SERVER_PID
