# Hook para flujos de tienda (si querés interceptar textos tipo 'comprar')
def handle_shop_flow(cfg, sender, text, send_msg):
    if text in ["comprar", "buy"]:
        send_msg(cfg, sender, "🛒 ¿Qué querés comprar? Escribe 'sorteo' para tickets.")
        return True
    return False
