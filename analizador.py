# =================================================================
# PROYECTO: Localizador de Vivienda en Orgiano (Vicenza)
# OBJETIVO: Analizar el área de alcance en coche (15 min)
# =================================================================

import sys
import subprocess

# 1. AUTO-INSTALACIÓN (Para que funcione en cualquier computadora)
def instalar_librerias():
    librerias = ['osmnx', 'folium', 'networkx', 'shapely']
    for lib in librerias:
        try:
            __import__(lib)
        except ImportError:
            print(f"Instalando {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

instalar_librerias()

import osmnx as ox
import networkx as nx
import folium
from shapely.geometry import Point, MultiPoint

def crear_analisis_geografico(lat, lon, minutos, velocidad_kmh):
    print(f"Calculando área de {minutos} min desde Orgiano...")

    # 2. Crear el mapa base centrado en Orgiano
    mapa = folium.Map(location=[lat, lon], zoom_start=12, tiles="cartodbpositron")

    # 3. Descargar la red de carreteras (radio de 15km para no quedarse corto)
    # Usamos 'drive' porque nos interesa el acceso en coche
    graph = ox.graph_from_point((lat, lon), dist=15000, network_type='drive')
    
    # 4. Cálculo matemático de la distancia
    # Distancia (metros) = (Velocidad km/h * 1000 / 60 minutos) * Tiempo deseado
    distancia_metros = (velocidad_kmh * 1000 / 60) * minutos

    # 5. Encontrar el punto de carretera más cercano a las coordenadas
    center_node = ox.distance.nearest_nodes(graph, lon, lat)

    # 6. Algoritmo de Grafo: Ego Graph (encuentra todos los nodos al alcance)
    subgraph = nx.ego_graph(graph, center_node, radius=distancia_metros, distance='length')

    # 7. Convertir los puntos técnicos en una "Mancha" visual (Polígono)
    puntos_geograficos = [Point((data['x'], data['y'])) for node, data in subgraph.nodes(data=True)]
    zona_alcance = MultiPoint(puntos_geograficos).convex_hull

    # 8. Añadir la zona al mapa
    folium.GeoJson(
        zona_alcance,
        name=f"Área de {minutos} min en coche",
        style_function=lambda x: {
            'fillColor': '#2ecc71', # Verde esperanza para tu nueva casa
            'color': '#27ae60',
            'weight': 2,
            'fillOpacity': 0.3
        }
    ).add_to(mapa)

    # 9. Añadir marcador de destino ideal
    folium.Marker(
        [lat, lon],
        popup="Orgiano: Mi futuro hogar",
        icon=folium.Icon(color='red', icon='home')
    ).add_to(mapa)

    return mapa

# --- EJECUCIÓN ---
# Coordenadas de Orgiano, Vicenza
LAT_ORGIANO = 45.35047
LON_ORGIANO = 11.46637

# Generamos el mapa: 15 minutos a una velocidad media de 45 km/h
mi_mapa_final = crear_analisis_geografico(LAT_ORGIANO, LON_ORGIANO, 15, 45)

# Guardar el resultado en un archivo HTML para ver en el navegador
mi_mapa_final.save("analisis_orgiano.html")
print("¡Hecho! Abre el archivo 'analisis_orgiano.html' para ver el resultado.")

# Si estás en un notebook (Colab), esto lo muestra aquí:
mi_mapa_final
