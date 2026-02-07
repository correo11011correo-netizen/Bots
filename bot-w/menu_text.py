from botones_core import send_message_to_api

def opcion_texto(config, recipient):
    while True:
        print("\n--- Submenú Texto ---")
        print("  1. Enviar texto simple")
        print("  2. Enviar texto con emoji")
        print("  3. Enviar texto largo")
        print("  4. Volver al menú principal")

        choice = input("Elige una opción: ")

        if choice == '1':
            text = input("Ingresa tu mensaje: ")
            send_message_to_api(config, recipient, text)
        elif choice == '2':
            text = input("Ingresa tu mensaje con emoji: ") + " 😊"
            send_message_to_api(config, recipient, text)
        elif choice == '3':
            text = input("Ingresa tu mensaje largo: ")
            send_message_to_api(config, recipient, text * 3)  # repite para simular largo
        elif choice == '4':
            break
        else:
            print("Opción inválida.")
