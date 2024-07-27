import pickle
import os
import numpy as np
# Plot
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd

def categorize(code):
    if code == 0:
        return 'Walk'
    elif code == 1:
        return 'PT'
    else:
        return 'Car'

def estimate_emissions(df, GasKm_car, GasKm_bus, CO2lt):  
        aver_N_passengers =29
        if df['Mode']=='Walk':
            return 0.0
        elif df['Mode']=='PT':
            return (5-df['Rem_work'])*(GasKm_bus*CO2lt*df['distance']/1000/aver_N_passengers)*0.5 + (5-df['Rem_work'])*(35.1*10**-3*df['distance']/1000/aver_N_passengers)*0.5
        else:
            return (5-df['Rem_work'])*GasKm_car*CO2lt*df['distance']/1000

def predict(df, gkm_car, gkm_bus, co2lt, model_dir):
    model_name = "rf"  # El nombre del modelo que guardaste anteriormente
    #file_path = os.path.join("models", f'{model_name}.pkl')
    #with open(file_path, 'rb') as file:
    with open(model_dir+f'{model_name}.pkl', 'rb') as file:
        model = pickle.load(file)
    
    gdf = gpd.GeoDataFrame(
            df.copy(), geometry=gpd.points_from_xy(df.O_long, df.O_lat), crs="EPSG:4326"
         )
    #if baseline == 0:
    #x = np.array(df.drop(columns = ['Mun_Des', 'Mun_Ori', 'O_long', 'O_lat', 'D_long', 'D_lat'])) 
    #x = np.array(df.drop(columns = ['Mun_Des', 'Mun_Ori', 'O_long', 'O_lat', 'D_long', 'D_lat', 'Rem_work','Coworking']))      
    cols_to_drop = df.columns[df.columns.str.contains('distance_stop')]
    # Drop the columns containing the string "Email"
    df.drop(cols_to_drop, axis=1, inplace=True)
    print()
    print('inside predict')
    print(df.head())  
    print()
    df = df.drop(columns = ['Mun_Des', 'Mun_Ori', 'O_long', 'O_lat', 'D_long', 'D_lat', 'original_distance','Rem_work','Coworking'], errors='ignore') # errors='ignore' only for the Baseline scenario where we do not have the 'Coworking' column      
    print('After second dopr:')
    print(df.head())
    x = np.array(df) 

    y_pred = model.predict(x)
    gdf['prediction'] = y_pred
    gdf['Mode'] = gdf['prediction'].apply(categorize)
 
    gdf['CO2']  = gdf.apply(estimate_emissions, args=(gkm_car, gkm_bus, co2lt), axis=1)
    gdf['CO2_worst_case']  = 5*gkm_car*co2lt*gdf['original_distance']/1000 # 5 = number of days, 1./12 = lt per Km, 2.3 = CO2 Kg per lt
    gdf['distance']  = gdf['distance']*(5-gdf['Rem_work']) # 5 = number of days, 1./12 = lt per Km, 2.3 = CO2 Kg per lt
    #labels = ['walk', 'PT', 'car']
    #colors = ['#99ff66','#00ffff','#ff3300']
    return gdf
    #return y_pred