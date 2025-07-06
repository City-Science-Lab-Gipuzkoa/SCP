import pandas as pd
import folium
from sklearn.cluster import KMeans
from geopy.distance import geodesic
import osmnx as ox
import matplotlib.pyplot as plt

def clustering_paradas(k, graph, network, workers_df, bus_stops_df) :
    
    north, south, east, west = 43.35, 43.1615, -1.7000, -2.2046

    # Filtrar trabajadores dentro del bounding box
    workers_df = workers_df[
        (workers_df["O_lat"] <= north) &
        (workers_df["O_lat"] >= south) &
        (workers_df["O_long"] <= east) &
        (workers_df["O_long"] >= west)
    ].copy()

    # Centrar el mapa en la zona de Donostia-San Sebastián
    mapa = folium.Map(location=[workers_df["O_lat"].mean(), workers_df["O_long"].mean()], zoom_start=12)

    # Añadir cada punto al mapa
    for _, row in workers_df.iterrows():
        folium.CircleMarker(
            location=[row["O_lat"], row["O_long"]],
            radius=3,
            color="blue",
            fill=True,
            fill_opacity=0.7
        ).add_to(mapa)

    # Extraer coordenadas como array para sklearn
    coords = workers_df[["O_lat", "O_long"]].values

    # Aplicar KMeans
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    workers_df["cluster"] = kmeans.fit_predict(coords)

    # Obtener centroides
    centroids = kmeans.cluster_centers_

    # Mapa para los clusters
    mapa_clusters = folium.Map(location=[workers_df["O_lat"].mean(), workers_df["O_long"].mean()], zoom_start=12)

    colors = [
    "red", "darkblue", "green", "yellow", "orange", 
    "purple", "pink", "white", "black", "gray", 
    "lightblue", "lightgreen", "brown", "cyan"
    ]


    # Añadir puntos por cluster
    for _, row in workers_df.iterrows():
        folium.CircleMarker(
            location=[row["O_lat"], row["O_long"]],
            radius=3,
            color=colors[row["cluster"]],
            fill=True,
            fill_opacity=0.7
        ).add_to(mapa_clusters)

    # Añadir centroides
    for i, (lat, lon) in enumerate(centroids):
        folium.Marker(
            location=[lat, lon],
            popup=f"Centroide {i}",
            icon=folium.Icon(color="black", icon="star")
        ).add_to(mapa_clusters)

    centroides_df = pd.DataFrame(centroids, columns=["lat", "lon"])

    paradas_cercanas_info = []

    depot_data = {
    "stop_name": "MUBIL",
    "stop_lat": "43.256347",
    "stop_lon": "-2.033693"
    }

    paradas_cercanas_info.append(depot_data)

    for idx, (lat_c, lon_c) in enumerate(centroids):
        min_dist = float('inf')
        parada_mas_cercana = None

        for _, row in bus_stops_df.iterrows():
            lat_p, lon_p = row['stop_lat'], row['stop_lon']
            dist = geodesic((lat_c, lon_c), (lat_p, lon_p)).meters
            if dist < min_dist:
                min_dist = dist
                parada_mas_cercana = {
                    "stop_name": row["stop_name"],
                    "stop_lat": lat_p,
                    "stop_lon": lon_p,
                }

        paradas_cercanas_info.append(parada_mas_cercana)


    # Añadir Depot al mapa con marcador distintivo
    folium.Marker(
        location=[float(depot_data["stop_lat"]), float(depot_data["stop_lon"])],
        popup="Depot (MUBIL)",
        icon=folium.Icon(color="blue", icon="home", prefix="fa")
    ).add_to(mapa_clusters)

    mapa_clusters.save("mapa_clusters.html")

    # Crear DataFrame
    paradas_df = pd.DataFrame(paradas_cercanas_info)
    ids = ["Depot"] + ["P" + str(i + 1) for i in range(len(paradas_df) - 1)] 
    paradas_df["id"] = ids


    # Obtener coordenadas como listas separadas
    lats = paradas_df["stop_lat"].astype(float).tolist()
    lons = paradas_df["stop_lon"].astype(float).tolist()

    # Encontrar nodos más cercanos en el grafo de OSMnx
    paradas_df["node_id"] = [ox.distance.nearest_nodes(graph, lon, lat) for lat, lon in zip(lats, lons)]

    # Encontrar nodos más cercanos en el grafo de Pandana
    paradas_df["node_id_pdna"] = network.get_node_ids(lons, lats).tolist()

    paradas_df["stop_lat"] = pd.to_numeric(paradas_df["stop_lat"], errors="coerce")
    paradas_df["stop_lon"] = pd.to_numeric(paradas_df["stop_lon"], errors="coerce")


    print(f"df_stops: {paradas_df}")

    return paradas_df





