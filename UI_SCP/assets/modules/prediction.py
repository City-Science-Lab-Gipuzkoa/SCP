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
    
def rev_categorize(code):
    if code == 'Walk':
        return 0
    elif code == 'PT':
        return 1
    else:
        return 2

#def estimate_emissions(df, GasKm_car, GasKm_bus, CO2lt):
def estimate_emissions(df, co2km_car, co2km_bus, co2km_train, bus_train_ratio):
        # weekly CO2 emissions in tons 
        aver_N_passengers = 29
        bus_train_ratio = bus_train_ratio/100.
        if df['Mode']=='Walk':
            return 0.0
        #elif df['Mode']=='PT':
        #    return (5-df['Rem_work'])*(GasKm_bus*CO2lt*df['distance']/1000/aver_N_passengers)*0.8 + (5-df['Rem_work'])*(35.1*10**-3*df['distance']/1000/aver_N_passengers)*0.2
        #else:
        #    return (5-df['Rem_work'])*GasKm_car*CO2lt*df['distance']/1000
        elif df['Mode']=='PT':
            return (5-df['Rem_work'])*(co2km_bus*df['distance']/1000/aver_N_passengers)*bus_train_ratio + (5-df['Rem_work'])*(co2km_train*df['distance']/1000/aver_N_passengers)*(1-bus_train_ratio)
        else:
            return (5-df['Rem_work'])*co2km_car*df['distance']/1000


def estimate_emissions_2(df, co2km_car, co2km_bus, co2km_train, bus_train_ratio):
        # weekly CO2 emissions in tons 
        aver_N_passengers = 29
        bus_train_ratio = bus_train_ratio/100.
        n_rw = df['Rem_work']
        n_cw = df['Coworking_days']

        # Baseline result #######################################
        if df['Mode_base']=='Walk':
            CO2_base = 0.0
        elif df['Mode_base']=='PT':
            CO2_base =  (co2km_bus*df['distance_base']/1000/aver_N_passengers)*bus_train_ratio + (co2km_train*df['distance_base']/1000/aver_N_passengers)*(1-bus_train_ratio)
        else:
            CO2_base =  co2km_car*df['distance_base']/1000
        #######################################################

        # Result with interventions ################################
        if df['Mode']=='Walk':
            CO2_interv = 0.0
        elif df['Mode']=='PT':
            CO2_interv =  (co2km_bus*df['distance']/1000/aver_N_passengers)*bus_train_ratio + (co2km_train*df['distance']/1000/aver_N_passengers)*(1-bus_train_ratio)
        else:
            CO2_interv =  co2km_car*df['distance']/1000
        ########################################################

        return (5 - n_rw - n_cw)*CO2_base + n_cw*CO2_interv

def calculate_indicator_d(df):
        mask = df.index.to_list()
        mask = [s for s in mask if "distance_stop" in s]
        min_dist = df[mask].min()
        den = 1 + min_dist/300 # at d=300 meters, temp = 1.5
        temp = df['CO2_over_target']*(1+1/den) 
        return temp         

def calculate_indicator_n(df):
        mask = df.index.to_list()
        mask = [s for s in mask if "distance_stop" in s]
        thr = 500
        n = (df[mask] < thr).values.sum() # number of stops closer than thr
        #return df['CO2_over_target']*(1 + n/3.)
        return n      


#def predict(df, gkm_car, gkm_bus, co2lt, model_dir):
def predict(df, df_base, co2km_car, co2km_bus, co2km_train, bus_train_ratio, model_dir):
    model_name = "rf_scp"  # El nombre del modelo que guardaste anteriormente
    #file_path = os.path.join("models", f'{model_name}.pkl')
    #with open(file_path, 'rb') as file:
    with open(model_dir+f'{model_name}.pkl', 'rb') as file:
        model = pickle.load(file)
    
    gdf = gpd.GeoDataFrame(
            df.copy(), geometry=gpd.points_from_xy(df.O_long, df.O_lat), crs="EPSG:4326"
         )

    gdf['distance_base'] = df_base['distance']
    #if baseline == 0:
    #x = np.array(df.drop(columns = ['Mun_Des', 'Mun_Ori', 'O_long', 'O_lat', 'D_long', 'D_lat'])) 
    #x = np.array(df.drop(columns = ['Mun_Des', 'Mun_Ori', 'O_long', 'O_lat', 'D_long', 'D_lat', 'Rem_work','Coworking']))      
    #cols_to_drop = df.columns[df.columns.str.contains('distance_stop')]
    # Drop the columns containing the string "Email"
    #df.drop(cols_to_drop, axis=1, inplace=True)
    
    #df = df.drop(columns = ['Mun_Des', 'Mun_Ori', 'O_long', 'O_lat', 'D_long', 'D_lat', 'original_distance','Rem_work','Coworking','Coworking_days'], errors='ignore') # errors='ignore' only for the Baseline scenario where we do not have the 'Coworking' column      
    #df_base = df_base.drop(columns = ['Mun_Des', 'Mun_Ori', 'O_long', 'O_lat', 'D_long', 'D_lat'], errors='ignore') # errors='ignore' only for the Baseline scenario where we do not have the 'Coworking' column      

    ##df.to_csv('C:/Users/gfotidellaf/repositories/UI_SCP/assets/data/X_before_predict.csv', index=False)

    df = df[['Hora_Ini_E', 'Per_hog', 'Turismos', 'Sexo', 'Edad', 'crnt_tur', 'drive_tt', 'distance', 'walk_tt', 'transit_tt', 'Tipo_familia']]
    df_base = df_base[['Hora_Ini_E', 'Per_hog', 'Turismos', 'Sexo', 'Edad', 'crnt_tur', 'drive_tt', 'distance', 'walk_tt', 'transit_tt', 'Tipo_familia']]

    x = np.array(df) 
    y_pred = model.predict(x)

    x_base = np.array(df_base) 
    y_base_pred = model.predict(x_base)

    gdf['Mode'] = y_pred
    gdf['Mode_base'] = y_base_pred
    #gdf['Mode'] = gdf['prediction'].apply(categorize)
    gdf['prediction'] = gdf['Mode'].apply(rev_categorize)
    gdf['prediction_base'] = gdf['Mode_base'].apply(rev_categorize)

    df['prediction'] = y_pred
    #df.to_csv('C:/Users/gfotidellaf/repositories/UI_SCP/assets/data/X_after_predict.csv', index=False)
    print()
    print('Final dataframe before after predict:')
    print(gdf.head(60))

    # Default values ##########################################
    #gkm_car = 1./12
    #gkm_bus = 1.12
    #co2lt = 2.3 # kg per lt
    #co2km_car = 0.3
    #co2km_bus = 0.3
    #co2km_train = 0.3

    #gdf['CO2']  = gdf.apply(estimate_emissions, args=(gkm_car, gkm_bus, co2lt), axis=1)
    #gdf['CO2']  = gdf.apply(estimate_emissions, args=(co2km_car, co2km_bus, co2km_train, bus_train_ratio), axis=1)
    gdf['CO2']  = gdf.apply(estimate_emissions_2, args=(co2km_car, co2km_bus, co2km_train, bus_train_ratio), axis=1)
    #CO2_aver_europe = 5.37 # aver. ton per person in 2021
    CO2_target = 2.3 * 0.4 # target CO2 ton per person in 2030 * 0.4 (assumes that 40% is associated to transportation)   
    n_weeks = 52 # weeks in one year
    print('columns names:')
    print(gdf.columns.values)
    gdf['CO2_over_target'] = gdf['CO2']/(CO2_target*1000/n_weeks) 
    #gdf['CO2_worst_case']  = 5*gkm_car*co2lt*gdf['original_distance']/1000 # 5 = number of days, 1./12 = lt per Km, 2.3 = CO2 Kg per lt
    gdf['CO2_worst_case']  = 5*co2km_car*gdf['original_distance']/1000 # 5 = number of days
    gdf['CO2_worst_case_over_target'] = gdf['CO2_worst_case']/(CO2_target*1000/n_weeks) 
    gdf['distance_week']  = gdf['distance']*(5-gdf['Rem_work']) # weekly distance: 5 = number of days, 1./12 = lt per Km, 2.3 = CO2 Kg per lt
    gdf['weighted_d']  = gdf.apply(calculate_indicator_d, axis=1)
    #gdf['weighted_n']  = gdf.apply(calculate_indicator_n, axis=1)
    gdf['n_close_stops']  = gdf.apply(calculate_indicator_n, axis=1)

    gdf.to_csv('C:/Users/gfotidellaf/repositories/UI_SCP/assets/data/Data_after_predict.csv', index=False)

    return gdf