import os
import uvicorn
from llama_cpp.server.app import create_app
from llama_cpp.server.settings import ServerSettings, ModelSettings

# --- Configuración ---
MODEL_FILE = "phi-2.Q4_K_M.gguf"
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILE)
HOST = "0.0.0.0"
PORT = 8000

def main():
    # Verifica si el modelo existe antes de continuar.
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Error: El archivo del modelo no se encuentra en la ruta: {MODEL_PATH}")
        print("Por favor, asegúrate de que el modelo se haya descargado completamente.")
        exit()

    print(f"✅ Modelo '{MODEL_FILE}' encontrado.")
    print("Iniciando el servidor de IA...")

    # Configuración del modelo que se va a servir.
    model_settings = ModelSettings(
        model=MODEL_PATH,
        n_gpu_layers=0,  # Importante: Usar solo CPU.
        n_ctx=1024,
    )

    # Configuración del servidor web.
    server_settings = ServerSettings(
        host=HOST,
        port=PORT,
    )

    # Crea la aplicación del servidor con la configuración definida.
    app = create_app(
        model_settings=[model_settings],
        server_settings=server_settings,
    )

    # Inicia el servidor.
    print(f"\n✅ Servidor de IA local iniciado.")
    print(f"   Escuchando en: http://{HOST}:{PORT}")
    print("   Para interactuar, envía peticiones POST a: http://localhost:8000/v1/chat/completions")
    print("\nPresiona CTRL+C para detener el servidor.")
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
    )

if __name__ == "__main__":
    main()