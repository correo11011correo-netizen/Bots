#!/usr/bin/env python3
import os
from utils import init_db, add_product, get_products, update_product, format_stock, delete_product
from flows.gemini import chat_logic # For modo_chat
import json # For details

def add_product_cli():
    nombre = input("📦 Nombre del producto: ")
    precio_input = input("💲 Precio: ")
    precio_str = precio_input.replace("$", "").replace(",", "").strip()
    try:
        precio = float(precio_str)
    except ValueError:
        print("⚠️ Precio inválido, escribí solo números (ej: 1000 o 1000.50).")
        return
    stock_input = input("📦 Stock (default 1): ")
    stock = int(stock_input) if stock_input.strip() else 1
    
    # Optionally get details
    details_input = input("🔍 Detalles adicionales (JSON, ej: {'color': 'azul', 'ram': '8GB'}): ")
    details_dict = {}
    if details_input:
        try:
            details_dict = json.loads(details_input)
        except json.JSONDecodeError:
            print("⚠️ Formato JSON de detalles inválido. Ignorando detalles.")

    details_json_str = json.dumps(details_dict, ensure_ascii=False)
    
    if add_product(nombre, precio, stock, details_json_str):
        print(f"✅ Producto agregado: {nombre} - ${precio} - stock {stock}")
    else:
        print(f"❌ Error: El producto {nombre} ya existe o hubo un problema al agregarlo.")

def update_product_cli():
    products = get_products()
    if not products:
        print("📦 No hay productos cargados para editar.")
        return
    
    print("Productos disponibles para editar:")
    for id, nombre, precio, stock, details_json_str in products:
        details_str = json.loads(details_json_str) if details_json_str else {}
        print(f"{id}. {nombre} - ${precio} - stock {stock} - detalles: {details_str}")
        
    try:
        id_to_edit = int(input("ID del producto a editar: "))
        product_name_to_edit = None
        for pid, pnombre, _, _, _ in products:
            if pid == id_to_edit:
                product_name_to_edit = pnombre
                break
        
        if not product_name_to_edit:
            print("⚠️ ID de producto no encontrado.")
            return

        precio_input = input("Nuevo precio (enter para no cambiar): ")
        stock_input = input("Nuevo stock (enter para no cambiar): ")
        details_input = input("Nuevos detalles (JSON para fusionar, ej: {'color': 'rojo'}, o enter para no cambiar): ")

        precio = float(precio_input.replace("$", "").replace(",", "")) if precio_input else None
        stock = int(stock_input) if stock_input else None
        details_dict = json.loads(details_input) if details_input else None
        
        if update_product(product_name_to_edit, precio, stock, details_dict):
            print(f"✅ Producto {product_name_to_edit} actualizado.")
        else:
            print(f"❌ Error: No se pudo encontrar o actualizar el producto {product_name_to_edit}.")
            
    except ValueError:
        print("⚠️ Entrada inválida para ID, precio o stock.")

def modo_chat():
    print("💬 Modo chat activado. Escribí frases como:")
    print("- 'Quiero ver el stock'")
    print("- 'Agregá un Samsung Galaxy A55 con precio 450 y stock 30'")
    print("- 'Cambiá el precio del iPhone 15 a 1300'")
    print("- 'Mostrame los modelos Motorola'")
    print("Escribí 'salir' para terminar.\n")

    state = None
    while True:
        texto = input("👤 Tú: ")
        result = chat_logic.interpretar(texto, state)
        print("🤖 Bot:", result["respuesta"])
        state = result.get("state")
        if result["accion"] == "salir":
            break

def main():
    init_db()
    while True:
        print("\nOpciones:")
        print("1️⃣ Listar productos")
        print("2️⃣ Agregar producto")
        print("3️⃣ Editar producto")
        print("4️⃣ Eliminar producto")
        print("5️⃣ Chat con Gemini")
        print("6️⃣ Salir")

        opcion = input("👉 Elegí una opción: ")

        if opcion == "1":
            products = get_products()
            print(format_stock(products))
        elif opcion == "2":
            add_product_cli()
        elif opcion == "3":
            update_product_cli()
        elif opcion == "4":
            delete_product_cli()
        elif opcion == "5":
            modo_chat()
        elif opcion == "6":
            print("👋 Saliendo...")
            break
        else:
            print("⚠️ Opción inválida.")

if __name__ == "__main__":
    main()
