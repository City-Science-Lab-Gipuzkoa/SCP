import pandas as pd
import os
from datetime import datetime, timedelta

def generar_gtfs(carpeta_base, carpetas, paradas_df, matriz_tiempos):

    for carpeta in carpetas:
        carpeta_path = os.path.join(carpeta_base, carpeta)
        print(f"Procesando carpeta: {carpeta}")

        rutas_files = [f for f in os.listdir(carpeta_path) if f.startswith("rutas") and f.endswith(".csv")]
        if not rutas_files:
            print(f"❌ No se encontró archivo de rutas en {carpeta_path}")
            continue

        rutas_file = os.path.join(carpeta_path, rutas_files[0])
        rutas_df = pd.read_csv(rutas_file)

        output_folder = os.path.join(carpeta_path, "gtfs_output")
        os.makedirs(output_folder, exist_ok=True)

        # stops.txt
        stops_txt = paradas_df.rename(columns={
            "id": "stop_id",
            "stop_name": "stop_name",
            "stop_lat": "stop_lat",
            "stop_lon": "stop_lon"
        })[["stop_id", "stop_name", "stop_lat", "stop_lon"]]
        stops_txt.to_csv(os.path.join(output_folder, "stops.txt"), index=False)

        # agency.txt
        agency_txt = pd.DataFrame([{
            "agency_id": "MUBIL",
            "agency_name": "MUBIL Urban Bus",
            "agency_url": "http://mubil.eus",
            "agency_timezone": "Europe/Madrid"
        }])
        agency_txt.to_csv(os.path.join(output_folder, "agency.txt"), index=False)

        # routes.txt
        rutas_unicas = rutas_df["vehiculo"].unique()
        routes_txt = pd.DataFrame({
            "route_id": rutas_unicas,
            "agency_id": "MUBIL",
            "route_short_name": rutas_unicas,
            "route_long_name": rutas_unicas,
            "route_type": 3
        })
        routes_txt.to_csv(os.path.join(output_folder, "routes.txt"), index=False)

        # calendar.txt
        hoy = datetime.today()
        calendar_txt = pd.DataFrame([{
            "service_id": "WEEKDAY",
            "monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1, "friday": 1,
            "saturday": 0, "sunday": 0,
            "start_date": hoy.strftime("%Y%m%d"),
            "end_date": (hoy + timedelta(days=365)).strftime("%Y%m%d")
        }])
        calendar_txt.to_csv(os.path.join(output_folder, "calendar.txt"), index=False)

        # feed_info.txt
        feed_info = pd.DataFrame([{
            "feed_publisher_name": "MUBIL",
            "feed_publisher_url": "http://mubil.eus",
            "feed_lang": "es",
            "feed_start_date": hoy.strftime("%Y%m%d"),
            "feed_end_date": (hoy + timedelta(days=365)).strftime("%Y%m%d"),
            "feed_contact_email": "info@mubil.eus",
            "feed_version": hoy.strftime("%Y.%m")
        }])
        feed_info.to_csv(os.path.join(output_folder, "feed_info.txt"), index=False)

        # trips, stop_times, shapes
        trips = []
        stop_times = []
        shapes = []

        horarios = ["08:00:00", "17:00:00"]
        shape_id_counter = 0

        for _, row in rutas_df.iterrows():
            vehiculo = row["vehiculo"]
            ruta = [int(x) for x in row.drop("vehiculo").dropna().values]

            for h in horarios:
                trip_id = f"{vehiculo}_{h.replace(':','')}"
                shape_id = f"{vehiculo}_shape_{shape_id_counter}"
                shape_id_counter += 1

                trips.append({
                    "route_id": vehiculo,
                    "service_id": "WEEKDAY",
                    "trip_id": trip_id,
                    "shape_id": shape_id
                })

                time_cursor = datetime.strptime(h, "%H:%M:%S")
                tiempo_acumulado = 0

                for seq, parada_idx in enumerate(ruta):
                    stop_info = paradas_df.iloc[parada_idx]
                    stop_id = str(stop_info["id"])
                    lat = stop_info["stop_lat"]
                    lon = stop_info["stop_lon"]

                    if seq > 0:
                        parada_anterior_idx = ruta[seq - 1]
                        stop_id_anterior = str(paradas_df.iloc[parada_anterior_idx]["id"])
                        tiempo_entre = matriz_tiempos.loc[stop_id_anterior, stop_id]
                        tiempo_acumulado += tiempo_entre

                    arrival = (time_cursor + timedelta(minutes=tiempo_acumulado)).strftime("%H:%M:%S")
                    departure = (time_cursor + timedelta(minutes=tiempo_acumulado, seconds=30)).strftime("%H:%M:%S")

                    stop_times.append({
                        "trip_id": trip_id,
                        "arrival_time": arrival,
                        "departure_time": departure,
                        "stop_id": stop_id,
                        "stop_sequence": seq
                    })

                    shapes.append({
                        "shape_id": shape_id,
                        "shape_pt_lat": lat,
                        "shape_pt_lon": lon,
                        "shape_pt_sequence": seq
                    })

        pd.DataFrame(trips).to_csv(os.path.join(output_folder, "trips.txt"), index=False)
        pd.DataFrame(stop_times).to_csv(os.path.join(output_folder, "stop_times.txt"), index=False)
        pd.DataFrame(shapes).to_csv(os.path.join(output_folder, "shapes.txt"), index=False)

def generar_gtfs_paradas(carpeta_base, carpetas):
    for carpeta in carpetas:
        carpeta_path = os.path.join(carpeta_base, carpeta)
        print(f"Procesando carpeta: {carpeta}")

        rutas_files = [f for f in os.listdir(carpeta_path) if f.startswith("rutas") and f.endswith(".csv")]
        if not rutas_files:
            print(f"❌ No se encontró archivo de rutas en {carpeta_path}")
            continue
        rutas_file = os.path.join(carpeta_path, rutas_files[0])
        rutas_df = pd.read_csv(rutas_file)

        stops_files = [f for f in os.listdir(carpeta_path) if f.startswith("df_stops") and f.endswith(".csv")]
        if not stops_files:
            print(f"❌ No se encontró df_stops.csv en {carpeta_path}")
            continue
        stops_file = os.path.join(carpeta_path, stops_files[0])
        paradas_df = pd.read_csv(stops_file)

        matriz_files = [f for f in os.listdir(carpeta_path) if f.startswith("time_mat") and f.endswith(".csv")]
        if not matriz_files:
            print(f"❌ No se encontró time_mat.csv en {carpeta_path}")
            continue
        matriz_file = os.path.join(carpeta_path, matriz_files[0])
        matriz_tiempos = pd.read_csv(matriz_file, index_col=0)

        matriz_tiempos.index = matriz_tiempos.index.astype(str)
        matriz_tiempos.columns = matriz_tiempos.columns.astype(str)

        output_folder = os.path.join(carpeta_path, "gtfs_output")
        os.makedirs(output_folder, exist_ok=True)

        # stops.txt
        stops_txt = paradas_df.rename(columns={
            "id": "stop_id",
            "stop_name": "stop_name",
            "stop_lat": "stop_lat",
            "stop_lon": "stop_lon"
        })[["stop_id", "stop_name", "stop_lat", "stop_lon"]]
        stops_txt.to_csv(os.path.join(output_folder, "stops.txt"), index=False)

        # agency.txt
        agency_txt = pd.DataFrame([{
            "agency_id": "MUBIL",
            "agency_name": "MUBIL Urban Bus",
            "agency_url": "http://mubil.eus",
            "agency_timezone": "Europe/Madrid"
        }])
        agency_txt.to_csv(os.path.join(output_folder, "agency.txt"), index=False)

        # routes.txt
        rutas_unicas = rutas_df["vehiculo"].unique()
        routes_txt = pd.DataFrame({
            "route_id": rutas_unicas,
            "agency_id": "MUBIL",
            "route_short_name": rutas_unicas,
            "route_long_name": rutas_unicas,
            "route_type": 3
        })
        routes_txt.to_csv(os.path.join(output_folder, "routes.txt"), index=False)

        # calendar.txt
        hoy = datetime.today()
        calendar_txt = pd.DataFrame([{
            "service_id": "WEEKDAY",
            "monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1, "friday": 1,
            "saturday": 0, "sunday": 0,
            "start_date": hoy.strftime("%Y%m%d"),
            "end_date": (hoy + timedelta(days=365)).strftime("%Y%m%d")
        }])
        calendar_txt.to_csv(os.path.join(output_folder, "calendar.txt"), index=False)

        # feed_info.txt
        feed_info = pd.DataFrame([{
            "feed_publisher_name": "MUBIL",
            "feed_publisher_url": "http://mubil.eus",
            "feed_lang": "es",
            "feed_start_date": hoy.strftime("%Y%m%d"),
            "feed_end_date": (hoy + timedelta(days=365)).strftime("%Y%m%d"),
            "feed_contact_email": "info@mubil.eus",
            "feed_version": hoy.strftime("%Y.%m")
        }])
        feed_info.to_csv(os.path.join(output_folder, "feed_info.txt"), index=False)

        # trips, stop_times, shapes
        trips = []
        stop_times = []
        shapes = []

        horarios = ["08:00:00", "17:00:00"]
        shape_id_counter = 0

        for _, row in rutas_df.iterrows():
            vehiculo = row["vehiculo"]
            ruta = [int(x) for x in row.drop("vehiculo").dropna().values]

            for h in horarios:
                trip_id = f"{vehiculo}_{h.replace(':','')}"
                shape_id = f"{vehiculo}_shape_{shape_id_counter}"
                shape_id_counter += 1

                trips.append({
                    "route_id": vehiculo,
                    "service_id": "WEEKDAY",
                    "trip_id": trip_id,
                    "shape_id": shape_id
                })

                time_cursor = datetime.strptime(h, "%H:%M:%S")
                tiempo_acumulado = 0

                for seq, parada_idx in enumerate(ruta):
                    stop_info = paradas_df.iloc[parada_idx]
                    stop_id = str(stop_info["id"])
                    lat = stop_info["stop_lat"]
                    lon = stop_info["stop_lon"]

                    if seq > 0:
                        parada_anterior_idx = ruta[seq - 1]
                        stop_id_anterior = str(paradas_df.iloc[parada_anterior_idx]["id"])
                        tiempo_entre = matriz_tiempos.loc[stop_id_anterior, stop_id]
                        tiempo_acumulado += tiempo_entre

                    arrival = (time_cursor + timedelta(minutes=tiempo_acumulado)).strftime("%H:%M:%S")
                    departure = (time_cursor + timedelta(minutes=tiempo_acumulado, seconds=30)).strftime("%H:%M:%S")

                    stop_times.append({
                        "trip_id": trip_id,
                        "arrival_time": arrival,
                        "departure_time": departure,
                        "stop_id": stop_id,
                        "stop_sequence": seq
                    })

                    shapes.append({
                        "shape_id": shape_id,
                        "shape_pt_lat": lat,
                        "shape_pt_lon": lon,
                        "shape_pt_sequence": seq
                    })

        pd.DataFrame(trips).to_csv(os.path.join(output_folder, "trips.txt"), index=False)
        pd.DataFrame(stop_times).to_csv(os.path.join(output_folder, "stop_times.txt"), index=False)
        pd.DataFrame(shapes).to_csv(os.path.join(output_folder, "shapes.txt"), index=False)

def generar_gtfs_unico(output_folder, rutas_df, paradas_df, matriz_tiempos):
    # stops.txt
    stops_txt = paradas_df.rename(columns={
        "id": "stop_id",
        "stop_name": "stop_name",
        "stop_lat": "stop_lat",
        "stop_lon": "stop_lon"
    })[["stop_id", "stop_name", "stop_lat", "stop_lon"]]
    stops_txt.to_csv(os.path.join(output_folder, "stops.txt"), index=False)

    # agency.txt
    agency_txt = pd.DataFrame([{
        "agency_id": "MUBIL",
        "agency_name": "MUBIL Urban Bus",
        "agency_url": "http://mubil.eus",
        "agency_timezone": "Europe/Madrid"
    }])
    agency_txt.to_csv(os.path.join(output_folder, "agency.txt"), index=False)

    # routes.txt
    rutas_unicas = rutas_df["vehiculo"].unique()
    routes_txt = pd.DataFrame({
        "route_id": rutas_unicas,
        "agency_id": "MUBIL",
        "route_short_name": rutas_unicas,
        "route_long_name": rutas_unicas,
        "route_type": 3
    })
    routes_txt.to_csv(os.path.join(output_folder, "routes.txt"), index=False)

    # calendar.txt
    hoy = datetime.today()
    calendar_txt = pd.DataFrame([{
        "service_id": "WEEKDAY",
        "monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1, "friday": 1,
        "saturday": 0, "sunday": 0,
        "start_date": hoy.strftime("%Y%m%d"),
        "end_date": (hoy + timedelta(days=365)).strftime("%Y%m%d")
    }])
    calendar_txt.to_csv(os.path.join(output_folder, "calendar.txt"), index=False)

    # feed_info.txt
    feed_info = pd.DataFrame([{
        "feed_publisher_name": "MUBIL",
        "feed_publisher_url": "http://mubil.eus",
        "feed_lang": "es",
        "feed_start_date": hoy.strftime("%Y%m%d"),
        "feed_end_date": (hoy + timedelta(days=365)).strftime("%Y%m%d"),
        "feed_contact_email": "info@mubil.eus",
        "feed_version": hoy.strftime("%Y.%m")
    }])
    feed_info.to_csv(os.path.join(output_folder, "feed_info.txt"), index=False)

    # trips, stop_times, shapes
    trips = []
    stop_times = []
    shapes = []

    horarios = ["08:00:00", "17:00:00"]
    shape_id_counter = 0

    for _, row in rutas_df.iterrows():
        vehiculo = row["vehiculo"]
        ruta = [int(x) for x in row.drop("vehiculo").dropna().values]

        for h in horarios:
            trip_id = f"{vehiculo}_{h.replace(':','')}"
            shape_id = f"{vehiculo}_shape_{shape_id_counter}"
            shape_id_counter += 1

            trips.append({
                "route_id": vehiculo,
                "service_id": "WEEKDAY",
                "trip_id": trip_id,
                "shape_id": shape_id
            })

            time_cursor = datetime.strptime(h, "%H:%M:%S")
            tiempo_acumulado = 0

            for seq, parada_idx in enumerate(ruta):
                stop_info = paradas_df.iloc[parada_idx]
                stop_id = str(stop_info["id"])
                lat = stop_info["stop_lat"]
                lon = stop_info["stop_lon"]

                if seq > 0:
                    parada_anterior_idx = ruta[seq - 1]
                    stop_id_anterior = str(paradas_df.iloc[parada_anterior_idx]["id"])
                    tiempo_entre = matriz_tiempos.loc[stop_id_anterior, stop_id]
                    tiempo_acumulado += tiempo_entre

                arrival = (time_cursor + timedelta(minutes=tiempo_acumulado)).strftime("%H:%M:%S")
                departure = (time_cursor + timedelta(minutes=tiempo_acumulado, seconds=30)).strftime("%H:%M:%S")

                stop_times.append({
                    "trip_id": trip_id,
                    "arrival_time": arrival,
                    "departure_time": departure,
                    "stop_id": stop_id,
                    "stop_sequence": seq
                })

                shapes.append({
                    "shape_id": shape_id,
                    "shape_pt_lat": lat,
                    "shape_pt_lon": lon,
                    "shape_pt_sequence": seq
                })

    pd.DataFrame(trips).to_csv(os.path.join(output_folder, "trips.txt"), index=False)
    pd.DataFrame(stop_times).to_csv(os.path.join(output_folder, "stop_times.txt"), index=False)
    pd.DataFrame(shapes).to_csv(os.path.join(output_folder, "shapes.txt"), index=False)

