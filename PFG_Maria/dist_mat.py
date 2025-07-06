def dist_mat(graph, network, df_stops, df_permutations) :
    import numpy as np
    import networkx as nx
    
    # Calculate the vectorized shortest path length 
    shortest_path_length = network.shortest_path_lengths(df_permutations["node_id_o"].values, df_permutations["node_id_d"].values, imp_name='distance')
    shortest_path_length = np.array(shortest_path_length) / 1000

    df_permutations["shortest_distance_pandana_km"] = shortest_path_length
    df_permutations = df_permutations.drop(columns=["node_id_o", "node_id_d"])

    # Mapeo ID a node_id para el network osmnx
    id_to_node = dict(zip(df_stops['id'].astype(str), df_stops['node_id']))

    # Calcular distancias
    distancias = []
    for _, row in df_permutations.iterrows():
        o_id, d_id = row['id_origen'], row['id_destino']
        if o_id == d_id:
            distancias.append(0.0)
            continue
        try:
            n_o = int(id_to_node[o_id])
            n_d = int(id_to_node[d_id])
            dist = nx.shortest_path_length(graph, n_o, n_d, weight="length")
            distancias.append(round(dist / 1000, 4))
        except Exception :
            try:
                dist = row["shortest_distance_pandana_km"]
                distancias.append(round(dist, 4))
            except Exception as e_pdna:
                print(f"❌ Error Pandana entre {o_id} y {d_id}: {e_pdna}")
                distancias.append(float("inf"))

    df_permutations["Distancia_min"] = distancias

    print()

    # Crear matriz cuadrada
    ids = sorted(set(df_permutations['id_origen']) | set(df_permutations['id_destino']))
    df_matrix = df_permutations.pivot_table(index='id_origen', columns='id_destino', values='Distancia_min')
    df_matrix = df_matrix.reindex(index=ids, columns=ids)
    np.fill_diagonal(df_matrix.values, 0)

    print(df_matrix)

    return df_matrix

