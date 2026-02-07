import os
import google.generativeai as genai

# Cargar la API Key desde variable de entorno
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ No se encontró GEMINI_API_KEY en las variables de entorno.")
    exit(1)

# Configurar cliente
genai.configure(api_key=api_key)

# Listar modelos disponibles
print("🔎 Modelos disponibles con tu API Key:\n")
try:
    models = genai.list_models()
    for m in models:
        print(f"- {m.name} | Métodos soportados: {m.supported_generation_methods}")
except Exception as e:
    print(f"❌ Error al listar modelos: {e}")
