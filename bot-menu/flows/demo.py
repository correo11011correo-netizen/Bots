from .state import get, set, clear, active

PRODUCTS = {
    "1": ("Camiseta deportiva", "15000"),
    "2": ("Zapatillas urbanas", "45000"),
    "3": ("Mochila impermeable", "25000")
}

def handle_demo_entry(cfg, sender, send_msg):
    set(sender, {"step": "choose_product", "product": None})
    send_msg(cfg, sender,
             "🛒 *Demo de compra*\n\n"
             "Productos disponibles:\n"
             "1️⃣ Camiseta deportiva - $15.000\n"
             "2️⃣ Zapatillas urbanas - $45.000\n"
             "3️⃣ Mochila impermeable - $25.000\n\n"
             "👉 Escribí el número del producto que querés comprar.")

def handle_demo_flow(cfg, sender, text, send_msg) -> bool:
    # Devuelve True si la demo procesó el mensaje
    if not active(sender):
        return False

    state = get(sender)
    step = state.get("step")

    if step == "choose_product":
        if text in PRODUCTS:
            name, price = PRODUCTS[text]
            state["product"] = name
            state["step"] = "choose_payment"
            set(sender, state)
            send_msg(cfg, sender,
                     f"✅ Seleccionaste *{name}* (${price}).\n"
                     "Elegí método de pago:\n"
                     "1️⃣ Transferencia/alias CVU\n"
                     "2️⃣ Link de pago MercadoPago")
            return True
        else:
            send_msg(cfg, sender, "Por favor respondé con 1, 2 o 3 para elegir un producto.")
            return True

    if step == "choose_payment":
        if text in ["1", "2"]:
            product = state.get("product", "Producto")
            if text == "1":
                send_msg(cfg, sender,
                         f"💳 Método: Transferencia/alias CVU\n"
                         f"Alias: *MIEMPRESA.CVU*\n"
                         f"Concepto: *{product}*\n\n"
                         "Enviá el comprobante para confirmar la compra.")
            else:
                send_msg(cfg, sender,
                         f"🔗 Link de pago: https://mpago.la/ejemplo\n"
                         f"Concepto: *{product}*\n"
                         "Podés pagar con tarjeta o saldo de MercadoPago.")
            send_msg(cfg, sender,
                     "✅ Pedido registrado.\n"
                     "¿Querés volver al menú? Escribí 'menu'.\n"
                     "Para reiniciar la demo: 'demo'.")
            clear(sender)
            return True
        else:
            send_msg(cfg, sender, "Por favor respondé con 1 (Transferencia) o 2 (Link de pago).")
            return True

    clear(sender)
    send_msg(cfg, sender, "Se reinició la demo. Escribí 'demo' para empezar de nuevo.")
    return True
