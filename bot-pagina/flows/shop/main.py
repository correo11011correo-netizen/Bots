from ..state import get, set, clear, active

# Cada producto ahora tiene: (nombre, precio, link de pago)
PRODUCTS = {
    "1": ("Camiseta deportiva", "15000", "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=XXX-CAMISETA"),
    "2": ("Zapatillas urbanas", "45000", "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=XXX-ZAPATILLAS"),
    "3": ("Mochila impermeable", "25000", "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=XXX-MOCHILA"),
    "4": ("Notebook", "10000", "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=174114989-8d6d8a01-9254-4423-97a6-3496ecd4a51d")
}

def handle_shop_entry(cfg, sender, send_msg):
    set(sender, {"flow": "shop", "step": "choose_product", "product": None})
    send_msg(cfg, sender,
             "🛒 *Demo de compra*\n\n"
             "Productos disponibles:\n"
             "1️⃣ Camiseta deportiva - $15.000\n"
             "2️⃣ Zapatillas urbanas - $45.000\n"
             "3️⃣ Mochila impermeable - $25.000\n"
             "4️⃣ Notebook - $10.000\n\n"
             "👉 Escribí el número del producto que querés comprar.")

def handle_shop_flow(cfg, sender, text, send_msg) -> bool:
    if not active(sender):
        return False

    state = get(sender)
    if not state or state.get("flow") != "shop":
        return False

    step = state.get("step")

    if step == "choose_product":
        if text in PRODUCTS:
            name, price, link = PRODUCTS[text]
            state["product"] = (name, price, link)
            state["step"] = "choose_payment"
            set(sender, state)
            send_msg(cfg, sender,
                     f"✅ Seleccionaste *{name}* (${price}).\n"
                     "Elegí método de pago:\n"
                     "1️⃣ Transferencia/alias CVU\n"
                     "2️⃣ Link de pago MercadoPago")
            return True
        else:
            send_msg(cfg, sender, "Por favor respondé con 1, 2, 3 o 4 para elegir un producto.")
            return True

    if step == "choose_payment":
        if text in ["1", "2"]:
            product = state.get("product", ("Producto", "0", None))
            name, price, link = product
            if text == "1":
                send_msg(cfg, sender,
                         f"💳 Método: Transferencia/alias CVU\n"
                         f"Alias: *MIEMPRESA.CVU*\n"
                         f"Concepto: *{name}*\n\n"
                         "Enviá el comprobante para confirmar la compra.")
            else:
                # Enviar botón interactivo con link de pago
                send_msg(cfg, sender, {
                    "messaging_product": "whatsapp",
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {
                            "text": f"🔗 Pagar *{name}* (${price})"
                        },
                        "action": {
                            "buttons": [
                                {
                                    "type": "url",
                                    "url": link,
                                    "text": "Pagar ahora"
                                }
                            ]
                        }
                    }
                })
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
