import pandas as pd

def convert_to_coords(nodo, paradas_df):
    try:
        if pd.isna(nodo) or nodo == '':
            return ""

        # Convertir nodo a índice entero (por si viene como 0.0, etc.)
        nodo_int = int(float(nodo))

        # Obtener el ID correspondiente (posición en el DataFrame)
        if nodo_int >= 0 and nodo_int < len(paradas_df):
            id_str = paradas_df.iloc[nodo_int]['id']

            fila = paradas_df[paradas_df['id'] == id_str]
            if not fila.empty:
                lat = round(fila['stop_lat'].values[0], 4)
                lon = round(fila['stop_lon'].values[0], 4)
                return f"{lat},{lon}"
            else:
                print("-> No se encontró el id en paradas_df")
                return "NA,NA"
        else:
            print("-> nodo_int fuera de rango")
            return "NA,NA"

    except Exception as e:
        print(f"-> Error al procesar nodo: {e}")
        return "NA,NA"