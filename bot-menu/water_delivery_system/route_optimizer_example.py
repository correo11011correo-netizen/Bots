import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import random

# --- 1. Configuración ---
place_name = "Ezeiza, Buenos Aires, Argentina"
depot_address = "Av. Gral. J. M. de Rosas 1300, Ezeiza, Buenos Aires, Argentina" # Un punto central aproximado en Ezeiza

# Clientes de ejemplo en Ezeiza (se pueden agregar más o modificar)
# Para el ejemplo, usaremos direcciones cercanas o ficticias dentro de Ezeiza
customer_addresses = [
    "Calle El Ceibo 1500, Ezeiza, Buenos Aires",
    "Av. Sarmiento 100, Ezeiza, Buenos Aires",
    "Calle French 300, Canning, Buenos Aires", # Canning está cerca de Ezeiza
    "Calle La Merced 50, Tristán Suárez, Buenos Aires", # Tristán Suárez está en Ezeiza
    "Av. Pedro Dreyer 4000, Canning, Buenos Aires",
    "Calle Chile 80, Ezeiza, Buenos Aires",
    "Calle Las Hortensias 20, Carlos Spegazzini, Buenos Aires", # Carlos Spegazzini está en Ezeiza
    "Calle Buenos Aires 1000, Ezeiza, Buenos Aires",
    "Ruta 205 Km 45, Ezeiza, Buenos Aires",
    "Calle Velez Sarsfield 500, Ezeiza, Buenos Aires"
]

# --- 2. Geocodificación de Direcciones ---
print("Geocodificando direcciones...")
geolocator = Nominatim(user_agent="water_delivery_optimizer")
locations = {}
errors = []

# Geocodificar depósito
try:
    depot_location = geolocator.geocode(depot_address)
    if depot_location:
        depot_point = (depot_location.latitude, depot_location.longitude)
        print(f"Depósito: {depot_address} -> {depot_point}")
    else:
        print(f"ERROR: No se pudo geocodificar el depósito: {depot_address}")
        exit()
except Exception as e:
    print(f"ERROR al geocodificar el depósito {depot_address}: {e}")
    exit()


# Geocodificar clientes
for i, address in enumerate(customer_addresses):
    try:
        location = geolocator.geocode(address)
        if location:
            locations[f"Cliente {i+1} ({address})"] = (location.latitude, location.longitude)
            print(f"Cliente {i+1}: {address} -> {(location.latitude, location.longitude)}")
        else:
            errors.append(f"No se pudo geocodificar: {address}")
    except Exception as e:
        errors.append(f"Error al geocodificar {address}: {e}")

if errors:
    print("\nErrores de geocodificación:")
    for error in errors:
        print(f"- {error}")
    # Podemos continuar con los clientes que sí se geocodificaron
    customer_locations = {name: coord for name, coord in locations.items() if name.startswith("Cliente")}
else:
    customer_locations = locations

if not customer_locations:
    print("No hay clientes válidos para calcular la ruta. Saliendo.")
    exit()

# --- 3. Descargar la Red de Calles con OSMnx ---
print("\nDescargando red de calles para Ezeiza con OSMnx. Esto puede tardar unos segundos...")
try:
    # Intenta obtener el grafo de la ubicación general de Ezeiza
    G = ox.graph_from_place(place_name, network_type="drive")
    # G = ox.graph_from_point(depot_point, dist=5000, network_type="drive") # Alternativa: grafo alrededor del depósito
    print("Red de calles descargada exitosamente.")
except Exception as e:
    print(f"ERROR al descargar la red de calles con OSMnx: {e}")
    print("Asegúrate de que 'Ezeiza, Buenos Aires, Argentina' sea un lugar válido para OSMnx.")
    exit()

# Proyectar el grafo a un sistema de coordenadas métricas (opcional, pero útil para distancias)
# G_proj = ox.project_graph(G)

# --- 4. Encontrar los nodos más cercanos en el grafo para cada punto ---
print("\nEncontrando nodos más cercanos en la red para el depósito y los clientes...")
depot_node = ox.distance.nearest_nodes(G, depot_point[1], depot_point[0]) # (lon, lat)
customer_nodes = {}
for name, coord in customer_locations.items():
    customer_nodes[name] = ox.distance.nearest_nodes(G, coord[1], coord[0])

# --- 5. Calcular distancias de recorrido desde el depósito a cada cliente ---
print("\nCalculando distancias de recorrido desde el depósito a cada cliente...")
distances_from_depot = []
for name, node in customer_nodes.items():
    try:
        # Calcula la longitud de la ruta más corta en metros
        route = nx.shortest_path(G, source=depot_node, target=node, weight='length')
        route_length_meters = nx.shortest_path_length(G, source=depot_node, target=node, weight='length')
        distances_from_depot.append({"name": name, "coord": customer_locations[name], "distance_meters": route_length_meters})
        print(f"- {name}: {route_length_meters / 1000:.2f} km")
    except nx.NetworkXNoPath:
        print(f"ADVERTENCIA: No se encontró ruta del depósito a {name}. Ignorando.")
    except Exception as e:
        print(f"ERROR al calcular ruta a {name}: {e}. Ignorando.")

if not distances_from_depot:
    print("No se pudieron calcular rutas válidas para ningún cliente. Saliendo.")
    exit()

# --- 6. Ordenar clientes del más cerca al más lejos del depósito ---
distances_from_depot.sort(key=lambda x: x["distance_meters"])

print("\n--- Ruta Optimizada (del más cerca al más lejos del depósito) ---")
optimized_route = []
for i, customer_info in enumerate(distances_from_depot):
    optimized_route.append({
        "order": i + 1,
        "name": customer_info["name"],
        "address": customer_info["name"].split('(', 1)[1][:-1], # Extrae la dirección de la cadena
        "lat": customer_info["coord"][0],
        "lon": customer_info["coord"][1],
        "distance_from_depot_km": customer_info["distance_meters"] / 1000
    })
    print(f"{i+1}. {customer_info['name']} - {customer_info['distance_meters'] / 1000:.2f} km")

print("\n--- Detalles de la Ruta Optimizada (JSON) ---")
import json
print(json.dumps(optimized_route, indent=2, ensure_ascii=False))

print("\n--- Cómo usar esto en la web ---")
print("1. Copia el JSON de arriba.")
print("2. Pega el JSON en la consola JavaScript de tu navegador (en la página de rutas o planificación de ruta) o en un campo de texto dedicado.")
print("3. La interfaz web (que aún necesita ser actualizada) podría dibujar estos puntos en un mapa Leaflet.")
print("\nNota: La interacción en tiempo real desde el navegador a este script Python requeriría un backend.")
