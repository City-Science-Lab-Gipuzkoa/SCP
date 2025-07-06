import pandas as pd
import numpy as np
import geopandas

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, adjusted_rand_score

from pylab import cm
import matplotlib

from os import listdir    

#root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP_touchscreen_local/assets/'
root_dir = '/Users/mariapena/Library/CloudStorage/GoogleDrive-mpenamerck@alumni.unav.es/My Drive/4º/PFG/Código/Código Final/SCP_files/assets/'

def run_MCM(trips_ez, root_Dir, Transh, routeOptDone, co2km_car=0.15, co2km_eCar= 0.01081, co2km_bus=1.3, co2km_train=0.049, bus_train_ratio=0.8, NremDays=0, NremWork=0, NeCar=0, CowCoords=[], CowDays=0):
        import pandas as pd
        import sys    
        root_dir = root_Dir
        sys.path.append(root_dir + 'modules')
        #sys.path.append(root_dir + 'components')
        print()
        print('root dir:', root_dir + 'modules')
        print()
        import pp
        import prediction
        import pandas as pd

        # ref for CO2 emissions:
        # car: https://www.eea.europa.eu/en/analysis/indicators/co2-performance-of-new-passenger#:~:text=Compared%20to%202021%2C%202022%20saw,108.1g%20CO2%2Fkm.
        # bus: https://www.carbonindependent.org/20.html#:~:text=The%20typical%20bus%20produces%20about,quoted%20by%20Goodall%20%5B7%5D).
        # train: https://www.carbonindependent.org/21.html
    
        if Transh == None:
            Transh = 8
            print('Transport hour not selected. Using default (08:00)')
        else:
            print('Chosen transport hour: ',Transh)

        print()
        print('root dir: ', root_dir)
        #workers_data_dir = root_dir + 'assets/data/'
        MCM_data_dir = 'data/input_data_MCM/'   
        #model_dir = root_dir + 'models/'
    
        eliminar = ['Unnamed: 0', 'Com_Ori', 'Com_Des', 'Modo', 'Municipio',
                    'Motos','Actividad','Año','Recur', 'Income', 'Income_Percentile'] 
        try:
            trips_ez = trips_ez.drop(columns=eliminar)
        except:
            pass
        print('check dir:',MCM_data_dir)
        trips_ez, trips_ez_base=pp.pp(Transh,trips_ez, routeOptDone, CowCoords, CowDays, NremWork, NremDays, root_dir) 

        
        prediction=prediction.predict(trips_ez, trips_ez_base, routeOptDone, co2km_car, co2km_eCar, co2km_bus, co2km_train, bus_train_ratio, NeCar, root_dir)  

        print()
        print('check if condition for saving baseline scenario is met...:')
        print(routeOptDone, CowDays, NremDays)
        if (routeOptDone == 0) and (CowDays==0) and (NremDays==0):
            print()
            print('Saving baseline scenario..., check directory:')
            print(root_dir + MCM_data_dir + 'baseline_scenario.csv')
            print()
            prediction.to_csv(root_dir + MCM_data_dir + 'baseline_scenario.csv', index=False)

        return prediction
        

root_dir_2 = '/Users/mariapena/Library/CloudStorage/GoogleDrive-mpenamerck@alumni.unav.es/My Drive/4º/PFG/Código/Código Final/'   
input_df = pd.read_csv(root_dir_2 + 'workers_df_225.csv')

#run_MCM(trips_ez, root_Dir, Transh, routeOptDone, co2km_car=0.15, co2km_eCar= 0.01081, co2km_bus=1.3, co2km_train=0.049, bus_train_ratio=0.8, NremDays=0, NremWork=0, NeCar=0, CowCoords=[], CowDays=0)
run_MCM(input_df, root_dir, 8, 1, co2km_car=0.15, co2km_eCar= 0.01081, co2km_bus=1.3, co2km_train=0.049, bus_train_ratio=0.8, NremDays=0, NremWork=0, NeCar=0, CowCoords=[], CowDays=0)
