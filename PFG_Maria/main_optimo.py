import pandas as pd
import os
from docplex.mp.model import Model
import convert_to_coords
import permutations
import dist_mat
import generar_grafos
import time_mat
import clustering_paradas
import gtfs_combinaciones
import dibujar_rutas_folium
import MCM
import calculo_CO2
import numpy as np
import random
import solve

np.random.seed(42)
random.seed(42)

def resolver(workers_df, alpha, beta, k, m):
    # --- Parámetros fijos ---
    print(f"alpha={alpha}, beta={beta}, k={k}, m={m}")
    carpeta_base = os.getcwd()
    carpeta_combinacion = "combinacion_unica"
    os.makedirs(carpeta_combinacion, exist_ok=True)

    # --- Cargar datos base ---
    all_bus_stops_df = pd.read_csv("all_bus_stops.csv")

    # --- Generar grafos ---
    graph, network = generar_grafos.generar_grafos()

    # --- Clustering ---
    df_stops = clustering_paradas.clustering_paradas(k, graph, network, workers_df, all_bus_stops_df) # Devuelve un df con el posicionamiento de las paraddas según los clusters
    df_permutations = permutations.permutations(df_stops)

    df_permutations.to_csv(os.path.join(carpeta_combinacion, "df_permutations.csv"), index=False)

    # --- Matrices ---
    dist_matrix_df = dist_mat.dist_mat(graph, network, df_stops, df_permutations)
    print("Matriz de distancias generada")
    time_matrix_df = time_mat.time_mat(graph, network, df_stops, df_permutations)
    print("Matriz de tiempos generada")
    dist_matrix = dist_matrix_df.values.tolist()
    time_matrix = time_matrix_df.values.tolist()
    # --- Guardar archivos auxiliares ---
    df_stops.to_csv(os.path.join(carpeta_combinacion, "df_stops.csv"), index=False)
    dist_matrix_df.to_csv(os.path.join(carpeta_combinacion, "dist_mat.csv"), index=True)
    time_matrix_df.to_csv(os.path.join(carpeta_combinacion, "time_mat.csv"), index=True)

    # --- Resolver mTSP ---
    rutas, total_distance, balanceo_tiempos = solve.solve(
        df_stops, dist_matrix, time_matrix, m, alpha, beta
    )

    if not rutas:
        raise ValueError("❌ No se generaron rutas.")

    # --- Guardar rutas ---
    max_len = max(len(r) for r in rutas)
    rutas_data = []

    for i, ruta in enumerate(rutas):
        fila = [f"vehiculo_{i+1}"] + ruta + [None] * (max_len - len(ruta))
        rutas_data.append(fila)

    columnas = ['vehiculo'] + [f'parada_{i}' for i in range(max_len)]
    rutas_df = pd.DataFrame(rutas_data, columns=columnas)
    rutas_df.to_csv(os.path.join(carpeta_combinacion, "rutas.csv"), index=False)

    # --- Coordenadas de rutas ---
    rutas_coords_df = rutas_df.copy()
    for col in rutas_coords_df.columns:
        if col.startswith("parada_"):
            rutas_coords_df[col] = rutas_coords_df[col].apply(
                lambda nodo: convert_to_coords.convert_to_coords(nodo, df_stops) if pd.notnull(nodo) else None
            )
    rutas_coords_df.to_csv(os.path.join(carpeta_combinacion, "rutas_coords.csv"), index=False)

    # --- Crear archivos GTFS ---
    gtfs_combinaciones.generar_gtfs_paradas(carpeta_base, [carpeta_combinacion])

    # --- Ejecutar el MCM ---
    dfs_resultado = MCM.MCM([carpeta_combinacion], carpeta_base)

    # --- Calcular CO2 ---
    co2_mcm = calculo_CO2.calculo_CO2_unico()
    co2_rutas = round(total_distance * 1.3 * 2, 4)
    co2_total_final = co2_rutas + co2_mcm

    print(f"✅ Resultado único para k={k}, m={m}:")
    print(f"- Distancia total: {total_distance}")
    print(f"- Balanceo tiempos: {balanceo_tiempos}")
    print(f"- CO2 rutas: {co2_rutas}")
    print(f"- CO2 MCM: {co2_mcm}")
    print(f"- CO2 total: {co2_total_final}")


    # --- Dibujar ruta con Folium ---
    id_combinacion = "combinacion_unica"
    dibujar_rutas_folium.mapa_combinaciones(graph, network, df_stops, carpeta_base, id_combinacion)
    return co2_total_final


np.random.seed(42)
random.seed(42)

def resolver_sin_beta(k, m):
    # --- Parámetros fijos ---
    print(f"k={k}, m={m}")
    carpeta_base = os.getcwd()
    carpeta_combinacion = "combinacion_sin_beta"
    os.makedirs(carpeta_combinacion, exist_ok=True)

    # --- Cargar datos base ---
    workers_df = pd.read_csv("workers_df_225.csv")
    all_bus_stops_df = pd.read_csv("all_bus_stops.csv")

    # --- Generar grafos ---
    graph, network = generar_grafos.generar_grafos()

    # --- Clustering ---
    df_stops = clustering_paradas.clustering_paradas(k, graph, network, workers_df, all_bus_stops_df)
    df_permutations = permutations.permutations(df_stops)

    df_permutations.to_csv(os.path.join(carpeta_combinacion, "df_permutations.csv"), index=False)

    # --- Matrices ---
    dist_matrix_df = dist_mat.dist_mat(graph, network, df_stops, df_permutations)
    print("Matriz de distancias generada")
    time_matrix_df = time_mat.time_mat(graph, network, df_stops, df_permutations)
    print("Matriz de tiempos generada")
    dist_matrix = dist_matrix_df.values.tolist()
    time_matrix = time_matrix_df.values.tolist()
    # --- Guardar archivos auxiliares ---
    df_stops.to_csv(os.path.join(carpeta_combinacion, "df_stops.csv"), index=False)
    dist_matrix_df.to_csv(os.path.join(carpeta_combinacion, "dist_mat.csv"), index=True)
    time_matrix_df.to_csv(os.path.join(carpeta_combinacion, "time_mat.csv"), index=True)

    # --- Resolver mTSP ---
    rutas, total_distance = solve.solve_sin_beta(
        df_stops, dist_matrix, time_matrix, m
    )

    if not rutas:
        raise ValueError("❌ No se generaron rutas.")

    # --- Guardar rutas ---
    max_len = max(len(r) for r in rutas)
    rutas_data = []

    for i, ruta in enumerate(rutas):
        fila = [f"vehiculo_{i+1}"] + ruta + [None] * (max_len - len(ruta))
        rutas_data.append(fila)

    columnas = ['vehiculo'] + [f'parada_{i}' for i in range(max_len)]
    rutas_df = pd.DataFrame(rutas_data, columns=columnas)
    rutas_df.to_csv(os.path.join(carpeta_combinacion, "rutas.csv"), index=False)

    # --- Coordenadas de rutas ---
    rutas_coords_df = rutas_df.copy()
    for col in rutas_coords_df.columns:
        if col.startswith("parada_"):
            rutas_coords_df[col] = rutas_coords_df[col].apply(
                lambda nodo: convert_to_coords.convert_to_coords(nodo, df_stops) if pd.notnull(nodo) else None
            )
    rutas_coords_df.to_csv(os.path.join(carpeta_combinacion, "rutas_coords.csv"), index=False)

    # --- Crear archivos GTFS ---
    gtfs_combinaciones.generar_gtfs_paradas(carpeta_base, [carpeta_combinacion])

    # --- Ejecutar el MCM ---
    dfs_resultado = MCM.MCM([carpeta_combinacion], carpeta_base)

    # --- Calcular CO2 ---
    co2_mcm = calculo_CO2.calculo_CO2_unico_1()
    co2_rutas = round(total_distance * 1.3 * 2, 4)
    co2_total_final = co2_rutas + co2_mcm

    print(f"✅ Resultado único para k={k}, m={m}:")
    print(f"- Distancia total: {total_distance}")
    print(f"- CO2 rutas: {co2_rutas}")
    print(f"- CO2 MCM: {co2_mcm}")
    print(f"- CO2 total: {co2_total_final}")


    # --- Dibujar ruta con Folium ---
    id_combinacion = "combinacion_sin_beta"
    dibujar_rutas_folium.mapa_combinaciones(graph, network, df_stops, carpeta_base, id_combinacion)
    return co2_total_final
