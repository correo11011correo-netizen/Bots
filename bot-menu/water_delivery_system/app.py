from flask import Flask, request, jsonify
from flask_cors import CORS
import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import random

app = Flask(__name__)
CORS(app) # Habilita CORS para permitir peticiones desde el frontend en localhost

# Configuración de Nominatim (reutiliza el user_agent del script anterior)
geolocator = Nominatim(user_agent="water_delivery_optimizer_flask")

# Configuración de OSMnx (solo se carga el grafo una vez)
# Esto puede tardar la primera vez
print("Cargando red de calles de Ezeiza con OSMnx. Esto puede tardar...")
try:
    G = ox.graph_from_place("Ezeiza, Buenos Aires, Argentina", network_type="drive")
    print("Red de calles de Ezeiza cargada exitosamente.")
except Exception as e:
    print(f"ERROR al cargar el grafo de OSMnx: {e}")
    print("Asegúrate de tener conexión a internet o que la ubicación sea válida.")
    G = None # Si falla la carga, G será None y las rutas fallarán

@app.route('/optimize_route', methods=['POST'])
def optimize_route():
    if G is None:
        return jsonify({"error": "No se pudo cargar la red de calles. Verifique la conexión a internet."}), 500

    data = request.json
    customer_addresses = data.get('addresses')
    depot_address = data.get('depot_address', "Av. Gral. J. M. de Rosas 1300, Ezeiza, Buenos Aires, Argentina")

    if not customer_addresses:
        return jsonify({"error": "No se proporcionaron direcciones de clientes."}), 400

    # 1. Geocodificación
    locations = []
    depot_point = None

    try:
        depot_location = geolocator.geocode(depot_address)
        if depot_location:
            depot_point = (depot_location.latitude, depot_location.longitude)
        else:
            return jsonify({"error": f"No se pudo geocodificar el depósito: {depot_address}"}), 400
    except Exception as e:
        return jsonify({"error": f"Error al geocodificar el depósito {depot_address}: {e}"}), 500

    for address_str in customer_addresses:
        try:
            location = geolocator.geocode(address_str)
            if location:
                locations.append({"address": address_str, "coord": (location.latitude, location.longitude)})
            else:
                print(f"ADVERTENCIA: No se pudo geocodificar: {address_str}")
        except Exception as e:
            print(f"ADVERTENCIA: Error al geocodificar {address_str}: {e}")
    
    if not locations:
        return jsonify({"error": "No se pudo geocodificar ninguna dirección de cliente válida."}), 400

    # 2. Encontrar nodos más cercanos en el grafo
    try:
        depot_node = ox.distance.nearest_nodes(G, depot_point[1], depot_point[0])
        customer_nodes = []
        for loc in locations:
            customer_nodes.append({
                "address": loc["address"],
                "coord": loc["coord"],
                "node": ox.distance.nearest_nodes(G, loc["coord"][1], loc["coord"][0])
            })
    except Exception as e:
        return jsonify({"error": f"Error al encontrar nodos cercanos en la red: {e}"}), 500


    # 3. Calcular distancias de recorrido desde el depósito a cada cliente
    distances_from_depot = []
    for cust_info in customer_nodes:
        try:
            # Calcula la longitud de la ruta más corta en metros
            route_length_meters = nx.shortest_path_length(G, source=depot_node, target=cust_info["node"], weight='length')
            distances_from_depot.append({
                "name": cust_info["address"], # Usar la dirección como nombre
                "coord": cust_info["coord"],
                "distance_meters": route_length_meters
            })
        except nx.NetworkXNoPath:
            print(f"ADVERTENCIA: No se encontró ruta del depósito a {cust_info['address']}. Ignorando.")
        except Exception as e:
            print(f"ERROR al calcular ruta a {cust_info['address']}: {e}. Ignorando.")

    if not distances_from_depot:
        return jsonify({"error": "No se pudieron calcular rutas válidas para ningún cliente."}), 500

    # 4. Ordenar clientes del más cerca al más lejos del depósito
    distances_from_depot.sort(key=lambda x: x["distance_meters"])

    optimized_route = []
    # Añadir el depósito como primer punto para la visualización
    optimized_route.append({
        "order": 0, # Opcional: indicar que es el inicio
        "name": "Depósito",
        "address": depot_address,
        "lat": depot_point[0],
        "lon": depot_point[1],
        "distance_from_depot_km": 0 # Distancia 0 desde el depósito
    })

    for i, customer_info in enumerate(distances_from_depot):
        optimized_route.append({
            "order": i + 1,
            "name": f"Cliente {i+1}", # Podríamos usar el nombre del cliente si estuviera en la appData
            "address": customer_info["name"], # La dirección completa
            "lat": customer_info["coord"][0],
            "lon": customer_info["coord"][1],
            "distance_from_depot_km": customer_info["distance_meters"] / 1000
        })
    
    return jsonify(optimized_route)

if __name__ == '__main__':
    # Ejecuta el servidor Flask en el puerto 8002
    app.run(debug=True, port=8002)
