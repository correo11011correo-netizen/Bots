bot-menu/
├── engine.py            # Router principal que despacha a cada flujo
├── welcome.py           # Mensaje de bienvenida comercial
├── responses.py         # Respuestas genéricas
├── utils.py             # Logging y utilidades
├── config/
│   └── settings.json    # Configuración básica (token, phone_id, verify_token)
├── menus/
│   ├── main_menu.py     # Menú principal de soluciones
│   └── services_menu.py # Menú de servicios complementarios
└── flows/
    ├── whatsapp.py      # Opción 1: Bot para WhatsApp
    ├── instagram.py     # Opción 2: Bot para Instagram
    ├── messenger.py     # Opción 3: Bot para Messenger
    ├── contact.py       # Opción 5: Contactar asesor
    ├── demo.py          # Opción 4: Flujo de compra guiado
    └── state.py         # Estado por usuario para la demo
