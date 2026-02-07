from botones_core import load_config, run_flask_app, TEST_MODE_RECIPIENT
from menu_text import opcion_texto
from menu_buttons import opcion_botones
from menu_links import opcion_link
from menu_status import opcion_status
from menu_help import opcion_help
from menu_exit import opcion_salir
from menu_system import opcion_system
from menu_admin import opcion_admin
import threading

def main():
    config = load_config()
    if not config:
        return

    flask_thread = threading.Thread(target=run_flask_app, args=(config,))
    flask_thread.daemon = True
    flask_thread.start()

    print("🚀 Servidor Flask iniciado en segundo plano.")
    print("\n--- Gemini CLI - WhatsApp Business API ---")

    while True:
        print("\nOpciones:")
        print("  1. Ver mensajes nuevos")
        print("  2. Submenú Texto")
        print("  3. Submenú Botones")
        print("  4. Submenú Links")
        print("  5. Submenú Sistema")
        print("  6. Submenú Administración")
        print("  7. Ayuda")
        print("  8. Salir")

        choice = input("Elige una opción: ")

        if choice == '1':
            opcion_status()
        elif choice == '2':
            opcion_texto(config, TEST_MODE_RECIPIENT)
        elif choice == '3':
            opcion_botones(config, TEST_MODE_RECIPIENT)
        elif choice == '4':
            opcion_link(config, TEST_MODE_RECIPIENT)
        elif choice == '5':
            opcion_system()
        elif choice == '6':
            opcion_admin()
        elif choice == '7':
            opcion_help()
        elif choice == '8':
            opcion_salir()
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()
