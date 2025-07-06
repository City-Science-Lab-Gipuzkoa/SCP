
import os
import pandas as pd
import folium
import networkx as nx
import osmnx as ox
import generar_grafos

graph, network = generar_grafos.generar_grafos()

# ====== 1. Rutas y paradas ======
base_dir = "combinacion_unica"
df_stops = pd.read_csv(os.path.join(base_dir, "df_stops.csv"))
rutas_df = pd.read_csv(os.path.join(base_dir, "rutas_coords.csv"))

# ====== 2. DataFrame con puntos que cambiaron de modo ======
archivo_coords = "Data_after_prediction_id_optima.csv"
archivo_base = "Data_after_prediction_sin_GTFS_225.csv"

df_base = pd.read_csv(archivo_base)
df_pred = pd.read_csv(archivo_coords)

# Detectar cambios de coche a PT
cambiaron = (df_base['Mode'] == 'Car') & (df_pred['Mode'] == 'PT')
df_coords_cambiadas = df_pred.loc[cambiaron, ['O_lat', 'O_long']].copy()

# ====== 3. Mapa base ======
coordenadas = rutas_df.filter(like='parada_').values.flatten()
coordenadas = [coord for coord in coordenadas if isinstance(coord, str) and "," in coord]
lat_centro, lon_centro = map(float, coordenadas[0].split(","))
mapa = folium.Map(location=[lat_centro, lon_centro], zoom_start=13)

# ====== 4. Colores por ruta ======
colores = [
    'blue', 'green', 'red', 'purple', 'orange', 'darkred', 'lightred',
    'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple',
    'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black'
]

# ====== 5. Dibujar rutas ======
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
                try:
                    nodo_origen = network.get_node_ids([puntos[i][1]], [puntos[i][0]])[0]
                    nodo_destino = network.get_node_ids([puntos[i+1][1]], [puntos[i+1][0]])[0]
                    path = network.shortest_path(nodo_origen, nodo_destino)
                    if path is not None and len(path) > 0:
                        coords = [(network.nodes_df.loc[node, 'y'], network.nodes_df.loc[node, 'x']) for node in path if node in network.nodes_df.index]
                        ruta_real.extend(coords)
                except Exception as e2:
                    print(f"Error calculando ruta con Pandana: {e2}")

    # Eliminar puntos repetidos seguidos
    def eliminar_puntos_repetidos(puntos):
        if not puntos:
            return []
        filtrados = [puntos[0]]
        for p in puntos[1:]:
            if p != filtrados[-1]:
                filtrados.append(p)
        return filtrados

    if ruta_real:
        ruta_real = eliminar_puntos_repetidos(ruta_real)
        folium.PolyLine(ruta_real, color=ruta_color, weight=5, opacity=0.8).add_to(mapa)

contador = 0
# ====== 6. Añadir puntos que cambiaron de modo ======
for i, fila in df_coords_cambiadas.iterrows():
    lat = fila['O_lat']
    lon = fila['O_long']
    folium.Marker(
        location=[lat, lon],
        popup="Cambio a PT",
        icon=folium.Icon(color="blue", icon="user", prefix="fa")
    ).add_to(mapa)
    contador += 1

print(f"Personas que han cambiado de modo: {contador}")

    # Añadir marcadores para cada parada
for _, row in df_stops.iterrows():
    lat, lon = row["stop_lat"], row["stop_lon"]
    nombre = row["stop_name"]

    if "MUBIL" in nombre.upper():
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color="black", icon="briefcase", prefix="fa")
        ).add_to(mapa)
        folium.map.Marker(
            [lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style='font-size:14pt; font-weight:bold; color:black; position:relative; left:20px; top:-12px; white-space:nowrap;'>
                    MUBIL
                </div>""")).add_to(mapa)
    else:
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color="darkred", icon="bus", prefix="fa")
        ).add_to(mapa)
        folium.map.Marker(
            [lat, lon],
            icon=folium.DivIcon(html=f"""
                <div style="font-size:10pt; color:darkred; font-weight:bold; position:relative; left:-20px; top:15px; white-space:nowrap;">
                    {nombre}
                </div>""")).add_to(mapa)


# ====== 7. Guardar mapa ======
nombre_mapa = "map_workers_to_PT.html"
mapa.save(nombre_mapa)
print(f"✅ Mapa guardado en {nombre_mapa}")
