def opcion_logs():
    try:
        with open("conversations.log", "r") as f:
            lines = f.readlines()[-5:]  # últimas 5 líneas
        print("\n📜 Últimos registros:")
        for line in lines:
            print("  " + line.strip())
    except FileNotFoundError:
        print("⚠️ No se encontró conversations.log")
