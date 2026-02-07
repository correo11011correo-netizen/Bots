import json
import os

def opcion_config():
    try:
        with open(os.path.join("config", "settings.json"), "r") as f:
            data = json.load(f)
        print("\n⚙️ Configuración actual:")
        for k, v in data.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
