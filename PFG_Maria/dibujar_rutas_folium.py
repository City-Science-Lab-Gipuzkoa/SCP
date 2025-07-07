import folium
import pandas as pd
import os
import random
import osmnx as ox
import networkx as nx
from geopy.distance import geodesic  

def buscar_nombre_mas_cercano(lat, lon, df_stops, tolerancia_m=20):
    coord_punto = (lat, lon)
    for _, row in df_stops.iterrows():
        coord_stop = (row["stop_lat"], row["stop_lon"])
        if geodesic(coord_punto, coord_stop).meters <= tolerancia_m:
            return row["stop_name"]
    return f"({lat:.5f}, {lon:.5f})"

def eliminar_puntos_repetidos(puntos):
    nueva_lista = []
    for p in puntos:
        if not nueva_lista or p != nueva_lista[-1]:
            nueva_lista.append(p)
    return nueva_lista


def mapa_combinaciones(graph, network, df_stops, carpeta_base, id_combinacion):
    colores = [
        'blue', 'green', 'red', 'purple', 'orange', 'darkred', 'lightred',
        'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple',
        'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black'
    ]

    carpeta = id_combinacion
    ruta_archivo = os.path.join(carpeta_base, carpeta, "rutas_coords.csv")

    if not os.path.exists(ruta_archivo):
        print(f"Archivo no encontrado: {ruta_archivo}")
        return

    rutas_df = pd.read_csv(ruta_archivo)

    # Obtener el centro del mapa
    coordenadas = rutas_df.filter(like='parada_').values.flatten()
    coordenadas = [coord for coord in coordenadas if isinstance(coord, str) and "," in coord]
    if not coordenadas:
        print(f"No hay coordenadas válidas en {ruta_archivo}")
        return
    lat_centro, lon_centro = map(float, coordenadas[0].split(","))
    mapa = folium.Map(location=[lat_centro, lon_centro], zoom_start=13)

    for idx, fila in rutas_df.iterrows():
        puntos = []
        for col in rutas_df.columns:
            if col.startswith("parada_"):
                valor = fila[col]
                if isinstance(valor, str) and "," in valor:
                    try:
                        lat, lon = map(float, valor.split(","))
                        puntos.append((lat, lon))  
                    except:
                        continue

        if len(puntos) == 0:
            continue

        ruta_color = colores[idx % len(colores)]
        ruta_real = []

        if len(puntos) > 1:
            for i in range(len(puntos) - 1):
                try:
                    origen = ox.distance.nearest_nodes(graph, puntos[i][1], puntos[i][0])
                    destino = ox.distance.nearest_nodes(graph, puntos[i+1][1], puntos[i+1][0])
                    path = nx.shortest_path(graph, origen, destino, weight="length")
                    coords = [(graph.nodes[n]['y'], graph.nodes[n]['x']) for n in path]
                    ruta_real.extend(coords)
                except Exception:
                    # Fallback a Pandana
                    try:
                        nodo_origen = network.get_node_ids([puntos[i][1]], [puntos[i][0]])[0]
                        nodo_destino = network.get_node_ids([puntos[i+1][1]], [puntos[i+1][0]])[0]
                        path = network.shortest_path(nodo_origen, nodo_destino)
                        if path is not None and len(path) > 0:
                            coords = [(network.nodes_df.loc[node, 'y'], network.nodes_df.loc[node, 'x']) for node in path if node in network.nodes_df.index]
                            ruta_real.extend(coords)
                    except Exception as e2:
                        print(f"Error calculando ruta con Pandana: {e2}")

        if ruta_real:
            ruta_real = eliminar_puntos_repetidos(ruta_real)
            folium.PolyLine(ruta_real, color=ruta_color, weight=5, opacity=0.8).add_to(mapa)

        for idx_p, (lat, lon) in enumerate(puntos):
            nombre = buscar_nombre_mas_cercano(lat, lon, df_stops)
            if "MUBIL" in nombre.upper():
                folium.CircleMarker(location=[lat, lon], radius=8, color="black", fill=True, fill_color="black", fill_opacity=1).add_to(mapa)
                folium.map.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(html=f"""
                        <div style="font-size:14pt; font-weight:bold; color:black; position:relative; left:20px; top:-12px; white-space:nowrap;">
                            {nombre}
                        </div>""")).add_to(mapa)
            else:
                folium.CircleMarker(location=[lat, lon], radius=6, color=ruta_color, fill=True, fill_color=ruta_color, fill_opacity=0.9).add_to(mapa)
                folium.map.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(html=f"""
                        <div style="font-size:10pt; color:{ruta_color}; font-weight:bold; position:relative; left:-20px; top:15px; white-space:nowrap;">
                            {nombre}
                        </div>""")).add_to(mapa)

    # Guardar el mapa en el directorio actual con el nombre del id_combinacion
    nombre_archivo = f"mapa_{id_combinacion}.html"
    mapa.save(nombre_archivo)
    print(f"Mapa guardado en {nombre_archivo}")

def mapa_combinaciones_paradas(graph, network, carpeta_base, id_combinacion):
    colores = [
        'blue', 'green', 'red', 'purple', 'orange', 'darkred', 'lightred',
        'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple',
        'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black'
    ]

    carpeta = id_combinacion
    ruta_archivo = os.path.join(carpeta_base, carpeta, "rutas_coords.csv")
    ruta_stops = os.path.join(carpeta_base, carpeta, "df_stops.csv")

    if not os.path.exists(ruta_archivo):
        print(f"Archivo no encontrado: {ruta_archivo}")
        return

    rutas_df = pd.read_csv(ruta_archivo)
    df_stops = pd.read_csv(ruta_stops)

    # Obtener el centro del mapa
    coordenadas = rutas_df.filter(like='parada_').values.flatten()
    coordenadas = [coord for coord in coordenadas if isinstance(coord, str) and "," in coord]
    if not coordenadas:
        print(f"No hay coordenadas válidas en {ruta_archivo}")
        return
    lat_centro, lon_centro = map(float, coordenadas[0].split(","))
    mapa = folium.Map(location=[lat_centro, lon_centro], zoom_start=13)

    for idx, fila in rutas_df.iterrows():
        puntos = []
        for col in rutas_df.columns:
            if col.startswith("parada_"):
                valor = fila[col]
                if isinstance(valor, str) and "," in valor:
                    try:
                        lat, lon = map(float, valor.split(","))
                        puntos.append((lat, lon))  
                    except:
                        continue

        if len(puntos) == 0:
            continue

        ruta_color = colores[idx % len(colores)]
        ruta_real = []

        if len(puntos) > 1:
            for i in range(len(puntos) - 1):
                try:
                    origen = ox.distance.nearest_nodes(graph, puntos[i][1], puntos[i][0])
                    destino = ox.distance.nearest_nodes(graph, puntos[i+1][1], puntos[i+1][0])
                    path = nx.shortest_path(graph, origen, destino, weight="length")
                    coords = [(graph.nodes[n]['y'], graph.nodes[n]['x']) for n in path]
                    ruta_real.extend(coords)
                except Exception:
                    # Fallback a Pandana
                    try:
                        nodo_origen = network.get_node_ids([puntos[i][1]], [puntos[i][0]])[0]
                        nodo_destino = network.get_node_ids([puntos[i+1][1]], [puntos[i+1][0]])[0]
                        path = network.shortest_path(nodo_origen, nodo_destino)
                        if path is not None and len(path) > 0:
                            coords = [(network.nodes_df.loc[node, 'y'], network.nodes_df.loc[node, 'x']) for node in path if node in network.nodes_df.index]
                            ruta_real.extend(coords)
                    except Exception as e2:
                        print(f"Error calculando ruta con Pandana: {e2}")

        if ruta_real:
            ruta_real = eliminar_puntos_repetidos(ruta_real)
            folium.PolyLine(ruta_real, color=ruta_color, weight=5, opacity=0.8).add_to(mapa)

        for idx_p, (lat, lon) in enumerate(puntos):
            nombre = buscar_nombre_mas_cercano(lat, lon, df_stops)
            if "MUBIL" in nombre.upper():
                folium.CircleMarker(location=[lat, lon], radius=8, color="black", fill=True, fill_color="black", fill_opacity=1).add_to(mapa)
                folium.map.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(html=f"""
                        <div style="font-size:14pt; font-weight:bold; color:black; position:relative; left:20px; top:-12px; white-space:nowrap;">
                            {nombre}
                        </div>""")).add_to(mapa)
            else:
                folium.CircleMarker(location=[lat, lon], radius=6, color=ruta_color, fill=True, fill_color=ruta_color, fill_opacity=0.9).add_to(mapa)
                folium.map.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(html=f"""
                        <div style="font-size:10pt; color:{ruta_color}; font-weight:bold; position:relative; left:-20px; top:15px; white-space:nowrap;">
                            {nombre}
                        </div>""")).add_to(mapa)

    # Guardar el mapa en el directorio actual con el nombre del id_combinacion
    nombre_archivo = f"mapa_{id_combinacion}.html"
    mapa.save(nombre_archivo)
    print(f"Mapa guardado en {nombre_archivo}")

def mapa_ruta_unica(graph, network, df_stops, rutas_df):
    colores = [
        'blue', 'green', 'red', 'purple', 'orange', 'darkred', 'lightred',
        'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple',
        'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black'
    ]

    # Obtener el centro del mapa
    coordenadas = rutas_df.filter(like='parada_').values.flatten()
    coordenadas = [coord for coord in coordenadas if isinstance(coord, str) and "," in coord]
    lat_centro, lon_centro = map(float, coordenadas[0].split(","))
    mapa = folium.Map(location=[lat_centro, lon_centro], zoom_start=13)

    for idx, fila in rutas_df.iterrows():
        puntos = []
        for col in rutas_df.columns:
            if col.startswith("parada_"):
                valor = fila[col]
                if isinstance(valor, str) and "," in valor:
                    try:
                        lat, lon = map(float, valor.split(","))
                        puntos.append((lat, lon))  
                    except:
                        continue

        if len(puntos) == 0:
            continue

        ruta_color = colores[idx % len(colores)]
        ruta_real = []

        if len(puntos) > 1:
            for i in range(len(puntos) - 1):
                try:
                    origen = ox.distance.nearest_nodes(graph, puntos[i][1], puntos[i][0])
                    destino = ox.distance.nearest_nodes(graph, puntos[i+1][1], puntos[i+1][0])
                    path = nx.shortest_path(graph, origen, destino, weight="length")
                    coords = [(graph.nodes[n]['y'], graph.nodes[n]['x']) for n in path]
                    ruta_real.extend(coords)
                except Exception:
                    # Fallback a Pandana
                    try:
                        nodo_origen = network.get_node_ids([puntos[i][1]], [puntos[i][0]])[0]
                        nodo_destino = network.get_node_ids([puntos[i+1][1]], [puntos[i+1][0]])[0]
                        path = network.shortest_path(nodo_origen, nodo_destino)
                        if path is not None and len(path) > 0:
                            coords = [(network.nodes_df.loc[node, 'y'], network.nodes_df.loc[node, 'x']) for node in path if node in network.nodes_df.index]
                            ruta_real.extend(coords)
                    except Exception as e2:
                        print(f"Error calculando ruta con Pandana: {e2}")

        if ruta_real:
            ruta_real = eliminar_puntos_repetidos(ruta_real)
            folium.PolyLine(ruta_real, color=ruta_color, weight=5, opacity=0.8).add_to(mapa)

        for idx_p, (lat, lon) in enumerate(puntos):
            nombre = buscar_nombre_mas_cercano(lat, lon, df_stops)
            if "MUBIL" in nombre.upper():
                folium.CircleMarker(location=[lat, lon], radius=8, color="black", fill=True, fill_color="black", fill_opacity=1).add_to(mapa)
                folium.map.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(html=f"""
                        <div style="font-size:14pt; font-weight:bold; color:black; position:relative; left:20px; top:-12px; white-space:nowrap;">
                            {nombre}
                        </div>""")).add_to(mapa)
            else:
                folium.CircleMarker(location=[lat, lon], radius=6, color=ruta_color, fill=True, fill_color=ruta_color, fill_opacity=0.9).add_to(mapa)
                folium.map.Marker(
                    [lat, lon],
                    icon=folium.DivIcon(html=f"""
                        <div style="font-size:10pt; color:{ruta_color}; font-weight:bold; position:relative; left:-20px; top:15px; white-space:nowrap;">
                            {nombre}
                        </div>""")).add_to(mapa)

    # Guardar el mapa en el directorio actual con el nombre del id_combinacion
    nombre_archivo = f"mapa_rutas_unico.html"
    mapa.save(nombre_archivo)
    print(f"Mapa guardado en {nombre_archivo}")

