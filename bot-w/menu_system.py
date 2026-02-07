import psutil

def opcion_system():
    while True:
        print("\n--- Submenú Sistema ---")
        print("  1. Ver CPU")
        print("  2. Ver RAM")
        print("  3. Ver procesos activos")
        print("  4. Volver al menú principal")

        choice = input("Elige una opción: ")

        if choice == '1':
            print(f"CPU: {psutil.cpu_percent()}%")
        elif choice == '2':
            print(f"RAM: {psutil.virtual_memory().percent}% usada")
        elif choice == '3':
            print(f"Procesos activos: {len(psutil.pids())}")
        elif choice == '4':
            break
        else:
            print("Opción inválida.")
