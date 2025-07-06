def permutations(df_stops):
    import pandas as pd
    import itertools

    df_stops = df_stops.sort_values(by='id').reset_index(drop=True)
    nodos_pandana = df_stops['node_id_pdna'].values.tolist()

    print("DEBUG nodos_pandana dentro de permutaciones():", nodos_pandana)

    permutations = list(itertools.permutations(nodos_pandana, 2))

    df_permutations = pd.DataFrame(permutations, columns=["node_id_o", "node_id_d"])
    df_permutations.index = df_permutations.index + 1
    df_permutations.index.name = "combination_id"

    # Merge con trazas de debug
    df_origen = df_stops[["node_id_pdna", "id"]].rename(columns={"node_id_pdna": "node_id_o", "id": "id_origen"})
    df_destino = df_stops[["node_id_pdna", "id"]].rename(columns={"node_id_pdna": "node_id_d", "id": "id_destino"})

    print("DEBUG df_origen head:\n", df_origen.head())
    print("DEBUG df_destino head:\n", df_destino.head())

    df_permutations = df_permutations.merge(df_origen, on="node_id_o", how="left")
    df_permutations = df_permutations.merge(df_destino, on="node_id_d", how="left")

    print("df_permutations generado con éxito.")

    df_permutations = df_permutations.sort_index(axis=0).sort_index(axis=1)
    return df_permutations
