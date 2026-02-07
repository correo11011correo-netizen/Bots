def get_response(text):
    # Fallback simple
    if not text:
        return "No entendí tu mensaje. Escribe 'menu' para ver opciones."
    return (
        "🤖 Opciones:\n"
        "- Escribe 'menu' para ver el menú principal.\n"
        "- 'sorteo' para comprar tickets.\n"
        "- 'referidos' para tu enlace y progreso.\n"
        "- 'prestamo' para ver requisitos."
    )
