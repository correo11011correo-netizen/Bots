import time

def format_timestamp(ts):
    """
    Formatea un timestamp de Unix a una cadena de texto legible.

    Args:
        ts (int or str): El timestamp de Unix.

    Returns:
        str: El timestamp formateado como 'YYYY-MM-DD HH:MM:SS'.
    """
    try:
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(ts)))
    except (ValueError, TypeError):
        # Si el timestamp no es válido o está ausente, devuelve la hora actual.
        return time.strftime('%Y-%m-%d %H:%M:%S')
