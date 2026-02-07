import requests
import json

# Dirección del servidor de IA local
API_URL = "http://localhost:8000/v1/chat/completions"

def main():
    """
    Cliente de chat para interactuar con el servidor de IA local.
    """
    print("🤖 Cliente de Chat para IA Local")
    print("   Habla con la IA. Escribe 'salir' o 'exit' para terminar.")
    print("-" * 50)

    # Mantiene un historial de la conversación para darle contexto a la IA.
    conversation_history = [
        {"role": "system", "content": "Eres un asistente de IA útil y conciso."}
    ]

    while True:
        try:
            # Pide la entrada del usuario.
            user_input = input("Tú: ")

            # Permite al usuario salir.
            if user_input.lower() in ["salir", "exit"]:
                print("👋 ¡Hasta luego!")
                break
            
            # Agrega el mensaje del usuario al historial.
            conversation_history.append({"role": "user", "content": user_input})

            # Prepara los datos para la petición a la API.
            data = {
                "messages": conversation_history,
                "temperature": 0.7,  # Un valor entre 0 y 1 que controla la creatividad.
            }

            # Envía la petición al servidor.
            response = requests.post(API_URL, headers={"Content-Type": "application/json"}, data=json.dumps(data))
            response.raise_for_status()  # Lanza un error si la petición falla.

            # Procesa la respuesta.
            response_data = response.json()
            ai_message = response_data['choices'][0]['message']['content']

            print(f"IA: {ai_message}")

            # Agrega la respuesta de la IA al historial.
            conversation_history.append({"role": "assistant", "content": ai_message})

        except requests.exceptions.RequestException as e:
            print(f"\n❌ Error de conexión: No se pudo conectar al servidor de IA.")
            print(f"   Asegúrate de que el servidor se esté ejecutando con 'python3 main.py'")
            print(f"   Error: {e}")
            break
        except (KeyboardInterrupt, EOFError):
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\nHa ocurrido un error inesperado: {e}")
            break

if __name__ == "__main__":
    main()
