import os
import pandas as pd
import re

def calculo_CO2_todos_en_directorio_actual():
    carpeta_actual = '.'  # Directorio actual
    archivo_base = "Data_after_prediction_sin_GTFS_225.csv"
    
    # Leer el archivo base
    df_base = pd.read_csv(archivo_base)

    co2_totales_por_id = {}
    patron = re.compile(r"Data_after_prediction_id_(\d+\.?\d*)\.csv")

    for archivo in os.listdir(carpeta_actual):
        match = patron.match(archivo)
        if match:
            id_comb = match.group(1)
            df_pred = pd.read_csv(archivo)

            if len(df_base) != len(df_pred):
                print(f"⚠️ El archivo {archivo} tiene diferente número de filas que el archivo base. Se salta.")
                continue

            modificadas = 0
            for i in range(len(df_pred)):
                if df_base.loc[i, 'Mode'] == 'Car' and df_pred.loc[i, 'Mode'] == 'PT':
                    df_pred.loc[i, 'CO2'] = 0
                    modificadas += 1

            co2_total = df_pred['CO2'].sum()
            co2_totales_por_id[id_comb] = co2_total

            print(f"{archivo}: CO2 cambiado a 0 en {modificadas} filas - CO2 total = {co2_total:.2f}")

    return co2_totales_por_id


import os
import pandas as pd
import re

def calculo_CO2_unico():
    archivo_base = "Data_after_prediction_sin_GTFS_225.csv"
    
    # Leer el archivo base
    df_base = pd.read_csv(archivo_base)

    archivo_nuevo = "Data_after_prediction_id_unica.csv"
    df_pred = pd.read_csv(archivo_nuevo)

    modificadas = 0
    for i in range(len(df_pred)):
        if df_base.loc[i, 'Mode'] == 'Car' and df_pred.loc[i, 'Mode'] == 'PT':
            df_pred.loc[i, 'CO2'] = 0
            modificadas += 1

    co2_total = df_pred['CO2'].sum()

    print(f"CO2 cambiado a 0 en {modificadas} filas - CO2 MCM = {co2_total:.2f}")

    return co2_total


