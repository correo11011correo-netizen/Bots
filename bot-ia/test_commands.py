import requests
import json
import time

BASE_URL = "http://localhost:8000"

def run_test(name, method, endpoint, data=None, stream=False):
    """Función para ejecutar una prueba individual."""
    print(f"--- INICIANDO PRUEBA: {name} ---")
    url = f"{BASE_URL}{endpoint}"
    print(f"URL: {method.upper()} {url}")
    
    try:
        start_time = time.time()
        if method == 'get':
            response = requests.get(url, timeout=10)
        elif method == 'post':
            response = requests.post(url, json=data, timeout=30, stream=stream)
        else:
            print("Método no soportado.")
            return

        end_time = time.time()
        print(f"Estado: {response.status_code}")
        print(f"Tiempo de respuesta: {end_time - start_time:.2f} segundos")

        if response.status_code == 200:
            if stream:
                print("Respuesta (stream):")
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        print(chunk.decode('utf-8'))
            else:
                print("Respuesta (JSON):")
                print(json.dumps(response.json(), indent=2))
        else:
            print("Cuerpo de la respuesta (error):")
            print(response.text)

    except requests.exceptions.Timeout:
        print("Resultado: La petición ha expirado (Timeout). El servidor no respondió a tiempo.")
    except requests.exceptions.RequestException as e:
        print(f"Resultado: Error en la petición: {e}")
    finally:
        print(f"--- PRUEBA FINALIZADA: {name} ---\n")


def main():
    print("🚀 Iniciando suite de pruebas para el servidor de IA local...\n")

    # Prueba 1: Endpoint de Modelos (simple, para ver si el servidor está vivo)
    run_test("Obtener Modelos", "get", "/v1/models")

    # Prueba 2: Endpoint de Tokenización (simple, para probar POST con cuerpo)
    tokenize_data = {"input": "hola mundo"}
    run_test("Tokenizar Texto", "post", "/extras/tokenize", data=tokenize_data)

    # Prueba 3: Endpoint de Chat (el que estaba fallando)
    chat_data = {
        "messages": [{"role": "user", "content": "Explica la gravedad en una frase."}],
        "temperature": 0.7,
    }
    run_test("Completar Chat", "post", "/v1/chat/completions", data=chat_data)
    
    # Prueba 4: Endpoint de Chat con streaming
    # stream_chat_data = {
    #     "messages": [{"role": "user", "content": "Cuenta hasta 3."}
    #     "temperature": 0.7,
    #     "stream": True
    # }
    # run_test("Completar Chat (Streaming)", "post", "/v1/chat/completions", data=stream_chat_data, stream=True)

    print("🏁 Suite de pruebas finalizada.")


if __name__ == "__main__":
    main()
