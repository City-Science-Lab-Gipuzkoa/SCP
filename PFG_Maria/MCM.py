def MCM(carpetas_filtradas, carpeta_base) :
    import shutil
    import subprocess
    import os
    import pandas as pd

    # Base dir = carpeta donde está este script
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Ruta destino para copiar archivos GTFS
    ruta_destino_gtfs = os.path.join(BASE_DIR, "SCP_files", "assets", "data", "input_data_MCM", "GTFS_feeds", "routes_EZ_companies")

    # Ruta al script de predicción
    ruta_script_prediccion = os.path.join(BASE_DIR, "SCP_files", "run_MCM.py")

    # Ruta al CSV generado tras la predicción
    ruta_resultado = os.path.join(BASE_DIR, "SCP_files", "assets", "data", "input_data_MCM", "Data_after_prediction.csv")

    # Ruta donde quieres guardar los resultados renombrados
    ruta_final = BASE_DIR

    resultados = []

    for carpeta in carpetas_filtradas:
        id_combinacion = carpeta.split("combinacion_")[1]

        carpeta_gtfs = os.path.join(carpeta_base, carpeta, "gtfs_output")

        if not os.path.exists(carpeta_gtfs):
            print(f"No se encontró gtfs_output en {carpeta}, se omite.")
            continue

        # 1. Copiar archivos de gtfs_output a la ruta destino (sobreescribiendo si ya existen)
        for archivo in os.listdir(carpeta_gtfs):
            ruta_origen_archivo = os.path.join(carpeta_gtfs, archivo)
            ruta_dest_archivo = os.path.join(ruta_destino_gtfs, archivo)
            shutil.copyfile(ruta_origen_archivo, ruta_dest_archivo)
        print(f"✅ Archivos GTFS copiados para la combinación {id_combinacion}")

        # 2. Ejecutar el script run_MCM.py
        print(f"🚀 Ejecutando modelo para combinación {id_combinacion}...")
        subprocess.run(["python", ruta_script_prediccion], check=True)

        # 3. Copiar el resultado renombrado
        nombre_archivo_resultado = f"Data_after_prediction_id_{id_combinacion}.csv"
        ruta_archivo_resultado_final = os.path.join(ruta_final, nombre_archivo_resultado)

        shutil.copyfile(ruta_resultado, ruta_archivo_resultado_final)
        print(f"📄 Resultado guardado como {nombre_archivo_resultado}\n")

        # Leer el CSV generado como DataFrame y guardarlo en el diccionario
        df = pd.read_csv(ruta_archivo_resultado_final)
        resultados.append((id_combinacion, df))

    return resultados
