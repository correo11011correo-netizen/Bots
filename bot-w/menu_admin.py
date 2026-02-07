from botones_core import incoming_messages, statuses

def opcion_admin():
    while True:
        print("\n--- Submenú Administración ---")
        print("  1. Limpiar mensajes")
        print("  2. Limpiar estados")
        print("  3. Volver al menú principal")

        choice = input("Elige una opción: ")

        if choice == '1':
            incoming_messages.clear()
            print("✅ Mensajes limpiados.")
        elif choice == '2':
            statuses.clear()
            print("✅ Estados limpiados.")
        elif choice == '3':
            break
        else:
            print("Opción inválida.")
