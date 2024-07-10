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

def estimate_emissions(df):  
        aver_N_passengers =29
        if df['Mode']=='Walk':
            return 0.0
        elif df['Mode']=='PT':
            return (1.1*2.3*df['distance']/1000/aver_N_passengers)*0.5 + (35.1*10**-3*df['distance']/1000/aver_N_passengers)*0.5
        else:
            return (1./12)*2.3*df['distance']/1000

def predict(df, model_dir):
    model_name = "rf"  # El nombre del modelo que guardaste anteriormente
    #file_path = os.path.join("models", f'{model_name}.pkl')
    #with open(file_path, 'rb') as file:
    with open(model_dir+f'{model_name}.pkl', 'rb') as file:
        model = pickle.load(file)
    
    gdf = gpd.GeoDataFrame(
            df.copy(), geometry=gpd.points_from_xy(df.O_long, df.O_lat), crs="EPSG:4326"
         )
    x = np.array(df.drop(columns = ['Mun_Des', 'Mun_Ori', 'O_long', 'O_lat', 'D_long', 'D_lat']))  
    y_pred = model.predict(x)
    gdf['prediction'] = y_pred
    #unique_labels, counts = np.unique(y_pred, return_counts=True)
    #d = {'mode_code': y_pred}
    #df = pd.DataFrame(data=d)
    #df['Mode'] = df['mode_code'].apply(categorize)
    gdf['Mode'] = gdf['prediction'].apply(categorize)
    gdf['CO2']  = gdf.apply(estimate_emissions, axis=1)
    #labels = ['walk', 'PT', 'car']
    #colors = ['#99ff66','#00ffff','#ff3300']
    return gdf
    #return y_pred