import numpy as np
import networkx as nx

def time_mat(graph, network, df_stops, df_permutations):
    # Mapeo ID a node_id para el network osmnx
    id_to_node = dict(zip(df_stops['id'].astype(str), df_stops['node_id']))
    tiempos = []

    for _, row in df_permutations.iterrows():
        o_id, d_id = row['id_origen'], row['id_destino']

        if o_id == d_id:
            tiempos.append(0.0)
            continue

        tiempo = None

        try:
            n_o = int(id_to_node[o_id])
            n_d = int(id_to_node[d_id])
            tiempo_osm = tiempo_osmnx(graph, n_o, n_d)
            if tiempo_osm is not None:
                tiempo = round(tiempo_osm / 60, 4)
        except Exception as e:
            pass

        if tiempo is None:
            try:
                tiempo = tiempo_pandana(network, df_permutations, o_id, d_id)
            except Exception as e:
                tiempo = None

        # Añadir siempre un valor
        tiempos.append(tiempo)

    # Asignar columna de tiempos
    df_permutations = df_permutations.copy()
    df_permutations["Min_time"] = tiempos

    # Crear matriz cuadrada
    ids = sorted(set(df_permutations['id_origen']) | set(df_permutations['id_destino']))
    df_matrix = df_permutations.pivot_table(index='id_origen', columns='id_destino', values='Min_time')
    df_matrix = df_matrix.reindex(index=ids, columns=ids)
    np.fill_diagonal(df_matrix.values, 0)

    return df_matrix


def tiempo_osmnx(graph, origen, destino):
    try:
        path = nx.shortest_path(graph, source=origen, target=destino, weight='length')
        tiempo_total = 0
        for u, v in zip(path[:-1], path[1:]):
            edge_data = graph.get_edge_data(u, v)
            if isinstance(edge_data, dict):
                edge = list(edge_data.values())[0]
            else:
                edge = edge_data
            tiempo_total += edge.get('travel_time', 0)
        return int(tiempo_total)
    except Exception:
        return None


def tiempo_pandana(network, df_permutations, origen, destino):
    shortest_path_length = network.shortest_path_lengths(df_permutations["node_id_o"].values,
                                                         df_permutations["node_id_d"].values,
                                                         imp_name='distance')
    shortest_path_length = np.array(shortest_path_length) / 1000
    df_permutations["shortest_distance_pandana_km"] = shortest_path_length

    velocidad_media_kmh = 50
    df_permutations["time_pandana_min"] = (df_permutations["shortest_distance_pandana_km"] / velocidad_media_kmh) * 60

    fila = df_permutations[
        (df_permutations["id_origen"] == origen) &
        (df_permutations["id_destino"] == destino)
    ]
    if not fila.empty:
        return fila.iloc[0]["time_pandana_min"]
    return None
