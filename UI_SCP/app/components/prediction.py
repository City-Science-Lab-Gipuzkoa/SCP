import pickle
import numpy as np
# Plot
import matplotlib.pyplot as plt
import geopandas as gpd
    
def categorize(code):
    if code == 'Walk':
        return 0
    elif code == 'PT':
        return 1
    else:
        return 2


def estimate_emissions(df, co2km_car, co2km_ecar, co2km_bus, co2km_train, bus_train_ratio):
        # weekly CO2 emissions in tons 
        #aver_N_passengers = 29 
        aver_N_passengers = 10
        bus_train_ratio = bus_train_ratio/100.
        n_rw = df['Rem_work']
        n_cw = df['Coworking_days']

        # Baseline result #######################################
        if df['Mode_base']=='Walk':
            CO2_base = 0.0
        elif df['Mode_base']=='PT':
            # We add a factor of "2" into CO2 calculation to account for round trip
            CO2_base =  2*(co2km_bus*df['distance_base']/1000/aver_N_passengers)*bus_train_ratio + 2*(co2km_train*df['distance_base']/1000)*(1-bus_train_ratio)
        else:        
            if df['eCar'] == 0: # combustion car
                # We add a factor of "2" into CO2 calculation to account for round trip
                CO2_base =  2*co2km_car*df['distance_base']/1000 
            else:               # electric car
                # We add a factor of "2" into CO2 calculation to account for round trip
                CO2_base =  2*co2km_ecar*co2km_car*df['distance_base']/1000
            #CO2_base =  co2km_car*df['distance_base']/1000
        #######################################################

        # Result with interventions ################################
        if df['Mode']=='Walk':
            CO2_interv = 0.0
        elif df['Mode']=='PT':
            # We add a factor of "2" into CO2 calculation to account for round trip
            CO2_interv =  2*(co2km_bus*df['distance']/1000/aver_N_passengers)*bus_train_ratio + 2*(co2km_train*df['distance']/1000)*(1-bus_train_ratio)
        else:        
            if df['eCar'] == 0: # combustion car
                # We add a factor of "2" into CO2 calculation to account for round trip
                CO2_interv =  2*co2km_car*df['distance']/1000 
            else:               # electric car
                # We add a factor of "2" into CO2 calculation to account for round trip
                CO2_interv =  2*co2km_ecar*co2km_car*df['distance']/1000
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

def predict(df, df_base, routeOptDone, co2km_car, co2km_ecar, co2km_bus, co2km_train, bus_train_ratio, NeCar, model_dir):
    model_name = "rf_scp"  # El nombre del modelo que guardaste anteriormente
    with open(model_dir+f'{model_name}.pkl', 'rb') as file:
        model = pickle.load(file)
    
    gdf = gpd.GeoDataFrame(
            df.copy(), geometry=gpd.points_from_xy(df.O_long, df.O_lat), crs="EPSG:4326"
         )

    gdf['distance_base'] = df_base['distance']

    df = df[['Hora_Ini_E', 'Per_hog', 'Turismos', 'Sexo', 'Edad', 'crnt_tur', 'drive_tt', 'distance', 'walk_tt', 'transit_tt', 'Tipo_familia']]
    df_base = df_base[['Hora_Ini_E', 'Per_hog', 'Turismos', 'Sexo', 'Edad', 'crnt_tur', 'drive_tt', 'distance', 'walk_tt', 'transit_tt', 'Tipo_familia']]

    x = np.array(df) 
    y_pred = model.predict(x)

    x_base = np.array(df_base) 
    y_base_pred = model.predict(x_base)

    gdf['Mode'] = y_pred
    gdf['Mode_base'] = y_base_pred
    gdf['prediction'] = gdf['Mode'].apply(categorize)
    gdf['prediction_base'] = gdf['Mode_base'].apply(categorize)

    #df['prediction'] = y_pred
    
    # Set eCar ###########################################################################    
    gdf["eCar"] = 0
    if NeCar > 0.0:
        n_rw = int(len(gdf.index)*NeCar/100) # number of workers using eCar
        df_to_set = gdf[gdf['Mode']=='Car'].sample(n_rw) # sample n_rw workers using Car
        df_to_set["eCar"] = 1
        gdf.update(df_to_set)
    ######################################################################################  
    
    #gdf['CO2']  = gdf.apply(estimate_emissions, args=(gkm_car, gkm_bus, co2lt), axis=1)
    #gdf['CO2']  = gdf.apply(estimate_emissions, args=(co2km_car, co2km_bus, co2km_train, bus_train_ratio), axis=1)
    gdf['CO2']  = gdf.apply(estimate_emissions, args=(co2km_car, co2km_ecar, co2km_bus, co2km_train, bus_train_ratio), axis=1)
   
    #CO2_aver_europe = 5.37 # aver. ton per person in 2021
    CO2_target = 2.3 * 0.4 # target CO2 ton per person in 2030 * 0.4 (assumes that 40% is associated to transportation)   
    n_weeks = 52 # weeks in one year
    print('columns names:')
    print(gdf.columns.values)
    gdf['CO2_over_target'] = gdf['CO2']/(CO2_target*1000/n_weeks) 
    #gdf['CO2_worst_case']  = 5*gkm_car*co2lt*gdf['original_distance']/1000 # 5 = number of days, 1./12 = lt per Km, 2.3 = CO2 Kg per lt
    
    # We add a factor of "2" into CO2 calculation to account for round trip
    gdf['CO2_worst_case']  = 2*5*co2km_car*gdf['original_distance']/1000 # 5 = number of days, 2 for round trip
    gdf['CO2_worst_case_over_target'] = gdf['CO2_worst_case']/(CO2_target*1000/n_weeks) 
    
    gdf['distance_week'] = 2*gdf['original_distance']*(5-gdf['Rem_work']-gdf['Coworking_days']) + 2*gdf['distance']*gdf['Coworking_days'] # weekly distance: 5 = number of days, 1./12 = lt per Km, 2.3 = CO2 Kg per lt
    gdf['distance_week_interv'] = 2*gdf['distance']*gdf['Coworking_days'] + 0.0*gdf['Rem_work'] 
    gdf['distance_week_no_interv'] = 2*gdf['original_distance']*(5-gdf['Rem_work']-gdf['Coworking_days']) 

    gdf['weighted_d']  = gdf.apply(calculate_indicator_d, axis=1)
    #gdf['weighted_n']  = gdf.apply(calculate_indicator_n, axis=1)
    gdf['n_close_stops']  = gdf.apply(calculate_indicator_n, axis=1)

    return gdf