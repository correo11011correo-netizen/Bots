from botones_core import send_test_buttons

def opcion_botones(config, recipient):
    while True:
        print("\n--- Submenú Botones ---")
        print("  1. Enviar menú")
        print("  2. Enviar promoción")
        print("  3. Enviar contacto")
        print("  4. Volver al menú principal")

        choice = input("Elige una opción: ")

        if choice in ['1','2','3']:
            send_test_buttons(config, recipient)
        elif choice == '4':
            break
        else:
            print("Opción inválida.")
