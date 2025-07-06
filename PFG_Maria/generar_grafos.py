
def generar_grafos() :
    import osmnx as ox
    import pandas as pd
    from pandana.loaders import osm

    # === Definir coordenadas del rectángulo en latitud/longitud (San Sebastián) ===
    north, south, east, west = 43.35, 43.1615, -1.7000, -2.2046
    bbox = (west, south, east, north)

    # === Crear red vial con velocidades y tiempos ===
    cf = '["highway"~"motorway|trunk|primary|secondary|residential|motorway_link|trunk_link|primary_link|secondary_link"]'
    hwy_speeds = {
        "motorway": 120, "trunk": 100, "primary": 100,
        "residential": 50, "unclassified": 50, "maxspeed": 120
    }

    graph = ox.graph_from_bbox(bbox, network_type='drive', simplify=False, custom_filter=cf)
    graph = ox.routing.add_edge_speeds(graph, hwy_speeds=hwy_speeds)
    graph = ox.add_edge_travel_times(graph)
    graph = ox.distance.add_edge_lengths(graph)

    nodes, edges = ox.graph_to_gdfs(graph)
    nodes = nodes.reset_index()
    edges = edges.reset_index()

    print("Grafo OSMnx generado con éxito.")

    ### PANDANA NETWORK
    network = osm.pdna_network_from_bbox(south, west, north, east, network_type='drive')

    print("Número de aristas antes del filtro:", len(network.edges_df))
    valid_highways = ['motorway', 'trunk', 'primary', 'secondary', 'residential', 'motorway_link', 'trunk_link', 'primary_link', 'secondary_link']
    edges_valid = edges[edges['highway'].apply(lambda h: any(hw in valid_highways for hw in h if isinstance(h, list)) if isinstance(h, list) else h in valid_highways)]
    valid_uv = set(zip(edges_valid['u'], edges_valid['v']))
    network.edges_df = network.edges_df[network.edges_df.apply(lambda row: (row['from'], row['to']) in valid_uv, axis=1)]
    print("Número de aristas después del filtro:", len(network.edges_df))

    print("Grafo Pandana generado con éxito.")

    return graph, network

