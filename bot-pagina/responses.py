def get_response(text):
    """
    Respuesta genérica para entradas que no coinciden con comandos o menús.
    """
    text = text.strip().lower()

    if text in ["gracias", "thank you", "ty"]:
        return "🙏 De nada, siempre a tu disposición."
    elif text in ["chau", "adios", "bye", "nos vemos"]:
        return "👋 ¡Hasta pronto!"
    elif text in ["ok", "vale", "listo"]:
        return "✅ Perfecto, continuemos."
    else:
        return (
            "🤔 No entendí tu mensaje.\n"
            "Escribí 'menu' para ver las opciones disponibles o 'lista' para otro menú."
        )
