import numpy as np
import os
import glob
import statistics
from pathlib import Path
import re
import requests
from io import StringIO
import random
import pdb
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import time
import urbanaccess as ua
from urbanaccess.config import settings
from urbanaccess.gtfsfeeds import feeds
from urbanaccess import gtfsfeeds
from urbanaccess.gtfs.gtfsfeeds_dataframe import gtfsfeeds_dfs
from urbanaccess.network import ua_network, load_network

import pickle
import os
import pandas as pd
from datetime import datetime
import pandana as pdn

import geopy.distance



# Plot
import matplotlib.pyplot as plt


t0 = time.time()

def pp(hour,X, RouteOptDone, CowCoords, CowDays, RemWoPer, RemWoDays, root_dir, MCM_dir):

    """
    feeds.add_feed(add_dict={'dbus': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/dbus/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_areizaga': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_areizaga/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_arrasate': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_arrasate/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_auif_urb': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_auif_urb/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_eibar': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_eibar/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_ekialdebus': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_ekialdebus/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_euskotren_bus': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_euskotren_bus/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_garayar': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_garayar/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_gipuzkoana': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_gipuzkoana/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_goierrialdea': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_goierrialdea/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_hernani': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_hernani/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_lasarte': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_lasarte/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_oiartzun': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_oiartzun/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_pesa': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_pesa/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_renteria': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_renteria/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_tbh': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_tbh/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_tolosaldea': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_tolosaldea/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_tsst': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_tsst/google_transit.zip'})
    feeds.add_feed(add_dict={'lurraldebus_zarautz': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/ATTG/lurraldebus_zarautz/google_transit.zip'})
    feeds.add_feed(add_dict={'Euskotren': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/Euskotren/google_transit.zip'})
    feeds.add_feed(add_dict={'Renfe': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/Renfe/google_transit.zip'})
    feeds.add_feed(add_dict={'Renfe_cercanias': 'https://www.geo.euskadi.eus/cartografia/DatosDescarga/Transporte/Moveuskadi/Renfe_Cercanias/google_transit.zip'})
    #feeds.add_feed(add_dict={'SCP_routes': '.\data\gtfsfeed_zips\routes_EZ_companies.zip'})
    # I download all these feeds, 70sg
    gtfsfeeds.download()
    """

    # Load GTFS data into an UrbanAcess transit data object
    validation = True
    verbose = True
    # bbox for Gipuzkoa
    Lat_min = 42.904155
    Long_min = -2.621987
    Lat_max = 43.403070
    Long_max = -1.740334
    bbox = (Long_min,Lat_min,Long_max,Lat_max,)
    remove_stops_outsidebbox = True
    append_definitions = True

    #filen = 'transit_ped_net.h5'
    gtfsfeed_path = root_dir + MCM_dir + 'GTFS_feeds/'
    networks_path = root_dir + 'data/input_data_MCM/networks/'
    transit_together_path = root_dir + 'data/input_data_MCM/transit_together_24h/'
    towns_path = root_dir + 'data/input_data_MCM/'

    # Definir los valores dados
    timeranges = [
        ['00:00:00', '01:00:00'], ['01:00:00', '02:00:00'], ['02:00:00', '03:00:00'], ['03:00:00', '04:00:00'],
        ['04:00:00', '05:00:00'], ['05:00:00', '06:00:00'], ['06:00:00', '07:00:00'], ['07:00:00', '08:00:00'],
        ['08:00:00', '09:00:00'], ['09:00:00', '10:00:00'], ['10:00:00', '11:00:00'], ['11:00:00', '12:00:00'],
        ['12:00:00', '13:00:00'], ['13:00:00', '14:00:00'], ['14:00:00', '15:00:00'], ['15:00:00', '16:00:00'],
        ['16:00:00', '17:00:00'], ['17:00:00', '18:00:00'], ['18:00:00', '19:00:00'], ['19:00:00', '20:00:00'],
        ['20:00:00', '21:00:00'], ['21:00:00', '22:00:00'], ['22:00:00', '23:00:00'], ['23:00:00', '24:00:00']
    ]
    nombres_archivos = [
        'transit_0001.h5', 'transit_0102.h5', 'transit_0203.h5', 'transit_0304.h5',
        'transit_0405.h5', 'transit_0506.h5', 'transit_0607.h5', 'transit_0708.h5',
        'transit_0809.h5', 'transit_0910.h5', 'transit_1011.h5', 'transit_1112.h5',
        'transit_1213.h5', 'transit_1314.h5', 'transit_1415.h5', 'transit_1516.h5',
        'transit_1617.h5', 'transit_1718.h5', 'transit_1819.h5', 'transit_1920.h5',
        'transit_2021.h5', 'transit_2122.h5', 'transit_2223.h5', 'transit_2324.h5'
    ]
    timeranges=[timeranges[hour]] # elegimos los timeranges que esten en nuestra franja
    nombres_archivos=[nombres_archivos[hour]] # elegimos los nombres que correspondan a la franja
    print(timeranges)
    print(nombres_archivos)



    lista = ["transit_0001",# lista creada para poder encontrar el string transit en la hora pedida
    "transit_0102",
    "transit_0203", 
    "transit_0304", 
    "transit_0405", 
    "transit_0506",
    "transit_0607",
    "transit_0708",
    "transit_0809",
    "transit_0910",
    "transit_1011",
    "transit_1112",
    "transit_1213",
    "transit_1314",
    "transit_1415",
    "transit_1516",
    "transit_1617",
    "transit_1718",
    "transit_1819",
    "transit_1920",
    "transit_2021",
    "transit_2122",
    "transit_2223",
    "transit_2324"]

    cont=0
    for k in lista:# este bucle elige de lista el transit que hayamos solititado, lo carga y lo asigna a el diccionario
        if hour==cont:
            #network_name = root_dir + 'data/input_data_MCM/' + f'/transit_together_24h/{k}.h5'
            network_filename = transit_together_path + f'{k}.h5'
            break
        else:
            cont=cont+1

    print()
    print('test if present:')
    print(networks_path + 'pedestrian_net.h5')
    print(os.path.isfile(networks_path + 'pedestrian_net.h5'))
    if (os.path.isfile(network_filename)==False) or RouteOptDone:
        print()
        print('-------------------------------------------')
        print('Generating a new integrated network file...')
        print('-------------------------------------------')
        print()
        for timerange, nombre_archivo in zip(timeranges, nombres_archivos):
            
            filen = f'{nombre_archivo}'        
            # Create transit network
            urbanaccess_net = ua.network.ua_network

            # Create new transit network from new feeds ##############################################
            loaded_feeds = ua.gtfs.load.gtfsfeed_to_df(gtfsfeed_path=gtfsfeed_path,
                                                    validation=validation,
                                                    verbose=verbose,
                                                    bbox=bbox,
                                                    remove_stops_outsidebbox=remove_stops_outsidebbox,
                                                    append_definitions=append_definitions)
            # Create transit network
            ua.gtfs.network.create_transit_net(gtfsfeeds_dfs=loaded_feeds,
                                            day='monday',
                                            timerange=timerange,
                                            calendar_dates_lookup=None)
            #############################################################################################
            
            print('Transit network:')
            print(urbanaccess_net.transit_edges.head())

            if (os.path.isfile(networks_path + 'pedestrian_net.h5')):

                print('\nLoading saved networks...') 
                #transit_ped_net = ua.network.load_network(dir=root_dir + 'transit_together_24h/', filename=filen)
                #ped_net = ua.network.load_network(dir=root_dir + 'networks/', filename='pedestrian_net.h5')
                ped_net = pdn.Network.from_hdf5(networks_path + 'pedestrian_net.h5')
                print('done!\n')
                
                # The following sh.. is really important!!! Pandana messes up data types (floats instead of int64!) ####################
                ped_net.nodes_df['id'] = ped_net.nodes_df.index 
                ##########################################################################################################################

                ua.osm.network.create_osm_net(osm_edges=ped_net.edges_df, osm_nodes=ped_net.nodes_df, travel_speed_mph=3)
                print('done!\n')

            else:
                nodes, edges = ua.osm.load.ua_network_from_bbox(bbox=bbox, remove_lcn=True)
                # Crear la red de OSM (pedestrian)       

                ua.osm.network.create_osm_net(osm_edges=edges, osm_nodes=nodes, travel_speed_mph=3) 

                ped_net_pdn = pdn.network.Network(
                                        nodes["x"],
                                        nodes["y"],
                                        edges["from"],
                                        edges["to"],
                                        edges[["weight","distance"]])

                ped_net_pdn.save_hdf5(networks_path + 'pedestrian_net.h5')
                #print(urbanaccess_net.osm_nodes.head())
                #print(urbanaccess_net.osm_edges.head()) 

            print('\nIntegrating all networks...')
            # Integrate saved and newly created tansit network 
            ua.network.integrate_network(urbanaccess_network=urbanaccess_net,  # do we need this?
                                        headways=False)     

            # Add average headways to network travel time
            ua.gtfs.headways.headways(gtfsfeeds_df=loaded_feeds,
                                headway_timerange=timerange)
            loaded_feeds.headways

            ua.network.integrate_network(urbanaccess_network=urbanaccess_net,
                                    headways=True,
                                    urbanaccess_gtfsfeeds_df=loaded_feeds,
                                    headway_statistic='mean')
            print('successfully integrated existing and newly created networks!')
        
            #print(urbanaccess_net.net_edges["from_int"].head())
            #urbanaccess_net.net_nodes.set_index('ID', inplace= True)
            transit_ped_net_pdn = pdn.network.Network(
                                    urbanaccess_net.net_nodes["x"],
                                    urbanaccess_net.net_nodes["y"],
                                    urbanaccess_net.net_edges["from_int"],
                                    urbanaccess_net.net_edges["to_int"],
                                    urbanaccess_net.net_edges[["weight"]])
                                    #urbanaccess_net.net_edges[["weight","distance"]])

            transit_ped_net_pdn.save_hdf5(transit_together_path + filen)
  
    else:
        print()
        print('Integrated network file found! Skipped generation of a new one')
        print()
    #eliminar = ['Unnamed: 0', 'Com_Ori', 'Com_Des', 'Modo', 'Municipio', 'Motos','Actividad','Año']
    #X = X.drop(columns=eliminar)

    print()
    print('test again if present:')
    print(networks_path + 'pedestrian_net.h5')
    print(os.path.isfile(networks_path + 'pedestrian_net.h5'))
    print()
    
    # Codify hour manually

    # Create a copy column

    X['Hora_Ini_E'] = X['Hora_Ini'].copy()
    cols = list(X.columns)
    A_index = cols.index('Hora_Ini')
    cols = cols[:A_index+1] + ['Hora_Ini_E'] + cols[A_index+1:-1]
    X = X[cols]

    # Codify it
    X['Hora_Ini'] = pd.to_datetime(X['Hora_Ini_E'], format='%H:%M') # Probably the first is Hora_Ini_E

    # Calculates difference in minutes from "00:00" and divides by 5
    X['Hora_Ini_E'] = ((X['Hora_Ini'] - pd.to_datetime('00:00', format='%H:%M')).dt.total_seconds() / 300).astype(int) + 1
    X['Hora_Ini'] = X['Hora_Ini'].dt.strftime('%H:%M')
    convertido=((hour*60*60)/300)+1
    print(convertido)
    # Get 1-hour interval between "convertido" and "convertido+1hour"? #######
    X=X[X['Hora_Ini_E'] <= (convertido+11)]
    X=X[X['Hora_Ini_E'] >= convertido]
    ##########################################################################
    
    # DRIVE
    networks = dict.fromkeys({
    "walk",
    "drive",
    })

    for k in networks:
        print(k)
        print(root_dir + f'networks/{k}_net.h5')
        #networks[k] = pdn.network.Network.from_hdf5(f'../input_data/networks/{k}_net.h5')
        networks[k] = pdn.network.Network.from_hdf5(root_dir + 'data/input_data_MCM/' + f'networks/{k}_net.h5')

    # # TRANSIT
    transit = dict.fromkeys({
    "transit_0001",
    "transit_0102",
    "transit_0203", # walk_network because transit is not available
    "transit_0304", # walk_network because transit is not available
    "transit_0405", # walk_network because transit is not available
    "transit_0506",
    "transit_0607",
    "transit_0708",
    "transit_0809",
    "transit_0910",
    "transit_1011",
    "transit_1112",
    "transit_1213",
    "transit_1314",
    "transit_1415",
    "transit_1516",
    "transit_1617",
    "transit_1718",
    "transit_1819",
    "transit_1920",
    "transit_2021",
    "transit_2122",
    "transit_2223",
    "transit_2324",
    })

    
    cont=0
    for k in lista:# este bucle elige de lista el transit que hayamos solititado, lo carga y lo asigna a el diccionario
        if hour==cont:
            print(k)
            #transit[k] = pdn.network.Network.from_hdf5(f'../input_data/transit_together_24h/{k}.h5')
            transit[k] = pdn.network.Network.from_hdf5(root_dir + 'data/input_data_MCM/' + f'/transit_together_24h/{k}.h5')
            break
        else:
            cont=cont+1
    
    # Assign tt

    X["distance"] = networks['drive'].shortest_path_lengths(
                networks['drive'].get_node_ids(X.O_long,X.O_lat),
                networks['drive'].get_node_ids(X.D_long,X.D_lat),
                imp_name='distance'
                )

    X_base = X.copy()
    # Coworking hubs #############################################################
    #X["original_distance"] = X["distance"] # save original distance to calculte worst case scenario
    X["original_distance"] = X.loc[:,"distance"] # save original distance to calculte worst case scenario
    X['Coworking'] = 0

    X['Coworking_days'] = CowDays
    #X_base_coords = X[['O_lat','O_long','D_lat','D_long','distance']]
    cowhub_i = 0
    if np.any(CowCoords):
        for cowhub in CowCoords:
            d = {'CowH_lat': [cowhub[0]], 'CowH_lon': [cowhub[1]]}
            # generate dataframe with replicas of the previous coordinates ###########
            temp_df = pd.DataFrame(data=d)
            temp_df = pd.DataFrame(np.repeat(temp_df.values, len(X.index), axis=0))
            temp_df.columns = ['CowH_lat','CowH_lon'] 
            ##########################################################################
            X["distance_CowHub_"+str(cowhub_i)] = networks['drive'].shortest_path_lengths(
                    networks['drive'].get_node_ids(X.O_long,X.O_lat),
                    networks['drive'].get_node_ids(temp_df.CowH_lon,temp_df.CowH_lat),
                    imp_name='distance'
                    )
            #X_temp["distance_CowHub_"+str(cowhub_i)] = networks['drive'].shortest_path_lengths(
            #        networks['drive'].get_node_ids(X.O_long,X.O_lat),
            #        networks['drive'].get_node_ids(temp_df.CowH_lon,temp_df.CowH_lat),
            #        imp_name='distance'
            #        )
            X['CowHub_Lat_'+str(cowhub_i)] = temp_df['CowH_lat'].to_numpy()
            X['CowHub_Lon_'+str(cowhub_i)] = temp_df['CowH_lon'].to_numpy()
            #X_temp['CowHub_Lat_'+str(cowhub_i)] = temp_df['CowH_lat'].to_numpy()
            #X_temp['CowHub_Lon_'+str(cowhub_i)] = temp_df['CowH_lon'].to_numpy()            
            cowhub_i+=1
        #
        ############################################################################################
        filter_cols = [col for col in X if col.startswith('distance_CowHub_')]
        compare_cols = ['distance'] + filter_cols     

        # Keep track of whether coworking hub is closer than original distance #####################
        t = X[compare_cols].idxmin(axis=1) # for each row, get names of the column with min dist
        print('Test1: ')
        print(t)
        print()
        #test1 = pd.DataFrame(t).values
        #test1 = t.copy()        
        #test1.to_csv('C:/Users/gfotidellaf/repositories/UI_SCP/assets/data/test1.csv', index=False)
        #t = [1 if p[0] != 'distance' else 0 for p in t] # set to 1 if coworking hub is at a minimum distance
        t = t.to_frame().reset_index() # convert to dataframe
        t = t.rename(columns= {0: 'closest'}) # assign column name
        t.index.name = 'index'
        print('Test2: ')
        print(t)        
        #test2 = t.copy()
        #test2.to_csv('C:/Users/gfotidellaf/repositories/UI_SCP/assets/data/test2.csv', index=False)

        temp = []
        CowHub_index = []
        for index, row in t.iterrows():
            if row['closest'] != 'distance' and CowDays > 0: # if coworking hub is closer than headquarter
                temp.append(1)                               # and coworking days are > 0,
                                                             # we set Coworking to 1
                CowHub_index.append(row['closest'].split('distance_CowHub_')[1])
            else:                                                   
                temp.append(0)
                CowHub_index.append('distance')
        X['Coworking'] = temp
        #X_temp['Coworking'] = temp
        #X['Coworking'] = t
        ############################################################################################
        # keep minimum distance among work destinations ############################################
        if CowDays > 0:
           X['distance'] = X[compare_cols].min(axis=1)
           #X_temp['distance'] = X_temp[compare_cols].min(axis=1)
        X.drop(columns=filter_cols, inplace=True)     
        #X_temp.drop(columns=filter_cols, inplace=True)     
        ############################################################################################ 

    #for index, row in X_temp.iterrows():
    counter = 0
    for index, row in X.iterrows():
        if row.Coworking==1:
            #X_temp.loc[index, 'D_lat'] = X_temp.loc[index, 'CowHub_Lat_0']
            #X_temp.loc[index, 'D_long'] = X_temp.loc[index, 'CowHub_Lon_0']
            CowHubIndex = CowHub_index[counter]
            X.loc[index, 'D_lat'] = X.loc[index, 'CowHub_Lat_'+CowHubIndex]
            X.loc[index, 'D_long'] = X.loc[index, 'CowHub_Lon_'+CowHubIndex]
        counter+=1
    try:
        #X = X.drop(['CowHub_Lat_0'], axis=1)
        #X = X.drop(['CowHub_Lon_0'], axis=1)
        X = X[X.columns.drop(list(X.filter(regex='CowHub_Lat_')))]
        X = X[X.columns.drop(list(X.filter(regex='CowHub_Lon_')))]
    except:
        pass

    #X[["Coworking_days"]].multiply(X["Coworking"], axis="index")
    X["Coworking_days"] = X.Coworking_days * X.Coworking

    # Remote working ###########################################################################
    n_rw = int(len(X.index)*RemWoPer/100) # number of workers doing remote work
    X["Rem_work"] = 0
    X_to_set = X.sample(n_rw)
    X_to_set["Rem_work"] = RemWoDays
    X.update(X_to_set)
    #X.to_csv('C:/Users/gfotidellaf/repositories/UI_SCP/assets/data/temp_pp_file.csv')
    ############################################################################################


    X["drive_tt"] = networks['drive'].shortest_path_lengths(
                networks['drive'].get_node_ids(X.O_long,X.O_lat),
                networks['drive'].get_node_ids(X.D_long,X.D_lat),
                imp_name='drive_time_s'
                )
    X["drive_tt"] = X["drive_tt"] / 60 # To min

    X["walk_tt"] = networks['walk'].shortest_path_lengths(
                networks['walk'].get_node_ids(X.O_long,X.O_lat),
                networks['walk'].get_node_ids(X.D_long,X.D_lat)
                )
    X["walk_tt"] = X["walk_tt"] / 60



    # Baseline dataframe #######################################
    X_base["drive_tt"] = networks['drive'].shortest_path_lengths(
                networks['drive'].get_node_ids(X_base.O_long,X_base.O_lat),
                networks['drive'].get_node_ids(X_base.D_long,X_base.D_lat),
                imp_name='drive_time_s'
                )
    X_base["drive_tt"] = X_base["drive_tt"] / 60 # To min

    X_base["walk_tt"] = networks['walk'].shortest_path_lengths(
                networks['walk'].get_node_ids(X_base.O_long,X_base.O_lat),
                networks['walk'].get_node_ids(X_base.D_long,X_base.D_lat)
                )
    X_base["walk_tt"] = X_base["walk_tt"] / 60
    ############################################################


    #bbox = [min(X.O_lat), min(X.O_long), max(X.O_lat), max(X.O_long)]
    stops_file = root_dir +'data/all_bus_stops.csv'
    stops_df = pd.read_csv(stops_file, encoding='latin-1')
    #stops_lat_lon = stops_df[['stop_lat','stop_lon']].to_numpy()

    #box1_cond = (bottom <= stops_df.lat) & (stops_df.lat <= top) & (left <= stops_df.lng) & (stops_df.lng <= right)
    bbox_stops = (min(X.O_lat) <= stops_df.stop_lat) & (stops_df.stop_lat <= max(X.O_lat)) & (min(X.O_long) <= stops_df.stop_lon) & (stops_df.stop_lon <= max(X.O_long))
    stops_df = stops_df[bbox_stops]

    #network_name = nombre_archivo.split('.h5')[0]
    #print(network_name)
    #transit_network = pdn.network.Network.from_hdf5(root_dir + 'data/input_data_MCM/' + f'/transit_together_24h/{nombres_archivos[0]}')
    #poi_node_ids = transit_network.get_node_ids(stops_df.stop_lon, stops_df.stop_lat).values
    poi_node_ids = networks['walk'].get_node_ids(stops_df.stop_lon, stops_df.stop_lat).values
    print()
    print('start calculating distances...')
    ori_node_ids = networks['walk'].get_node_ids(X.O_long,X.O_lat).values
    print()
    print('lengths before:')  
    print(len(ori_node_ids), len(poi_node_ids))

    origins = [[ori_node_ids[i]]*len(poi_node_ids) for i in range(len(ori_node_ids))]
    dest = list([poi_node_ids[:]]*len(ori_node_ids))

    import itertools
    origins = list(itertools.chain.from_iterable(origins)) #flatten and merge list of lists
    dest = list(itertools.chain.from_iterable(dest)) #flatten and merge list of lists 

    distances_to_pt = networks['walk'].shortest_path_lengths(origins, dest)
    #print('distance:')
    #print(distances_to_pt)

    #temp_df = pd.DataFrame(np.column_stack([origins, dest, distances_to_pt]), 
    #                           columns=['ori_node', 'dest_node', 'dist'])
    temp_df = pd.DataFrame(distances_to_pt, 
                               columns=['dist'])    
    #closest_POI = temp_df.groupby(np.arange(len(temp_df))//len(poi_node_ids)).min() #group by number of destinations and keep the min for each origin node
    closest_POIs = temp_df.groupby(np.arange(len(temp_df))//len(poi_node_ids))
    distances_df = closest_POIs['dist'].apply(lambda x: pd.Series(x.values)).unstack()
    #distances_df = distances_df.to_frame()
    distances_df_sorted = distances_df.apply(np.sort, axis = 1)
    #distances_df_sorted = distances_df_sorted.to_frame()

    print()
    print('distances:')
    print(distances_df_sorted.head())
    #distances_df_sorted = pd.DataFrame.from_items(zip(distances_df_sorted.index, distances_df_sorted.values)).T
    distances_df_sorted = pd.DataFrame(np.vstack(distances_df_sorted.T))

    cols = range(5,len(distances_df_sorted.columns)) #keep first 5 smaller distances
    distances_df_sorted.drop(distances_df_sorted.columns[cols],axis=1,inplace=True) 
    distances_df_sorted.columns = ['distance_stop_' + str(i) for i in range(len(distances_df_sorted.columns))]
    print('distances dataframe:')
    print(distances_df_sorted.head())
    print()
    print('size of distance_df:')
    print(len(distances_df_sorted.index))
    print('size of X:')
    print(len(X.index))

    #print()
    #print('first check')
    #print(X['O_long'].isnull().values.any(),X['O_lat'].isnull().values.any(),X['D_long'].isnull().values.any(),X['D_lat'].isnull().values.any())
    X = pd.merge(X, distances_df_sorted, on=X.index, how='outer')
    X.drop(['key_0'], axis=1, inplace=True) # key_0 is added automatically by "merge", we need to drop it
    pd.set_option('display.max_columns', None)
    #print()
    #print('second check')
    #print(X['O_long'].isnull().values.any(),X['O_lat'].isnull().values.any(),X['D_long'].isnull().values.any(),X['D_lat'].isnull().values.any())
    #print(X)

    # Add TRANSIT

    lista = ["transit_0001",
    "transit_0102",
    "transit_0203", 
    "transit_0304", 
    "transit_0405", 
    "transit_0506",
    "transit_0607",
    "transit_0708",
    "transit_0809",
    "transit_0910",
    "transit_1011",
    "transit_1112",
    "transit_1213",
    "transit_1314",
    "transit_1415",
    "transit_1516",
    "transit_1617",
    "transit_1718",
    "transit_1819",
    "transit_1920",
    "transit_2021",
    "transit_2122",
    "transit_2223",
    "transit_2324"]
    cont=0
    for k in lista:# este bucle elige de lista el transit que hayamos solititado, lo carga y lo asigna a el diccionario
        if hour==cont:
            #X[f"{k}_tt"] = transit[k].shortest_path_lengths(
            #transit[k].get_node_ids(X.O_long,X.O_lat),
            #transit[k].get_node_ids(X.D_long,X.D_lat),
            #imp_name='distance'
            #)
            #X[f"{k}_tt"] = transit[k].shortest_path_lengths(
            #transit[k].get_node_ids(X.O_long,X.O_lat),
            #transit[k].get_node_ids(X.D_long,X.D_lat),
            #imp_name='weight'
            #)
            X[f"{k}_tt"] = transit[k].shortest_path_lengths(   # original code
            transit[k].get_node_ids(X.O_long,X.O_lat),         # original code
            transit[k].get_node_ids(X.D_long,X.D_lat)          # original code
            )                                                  # original code

            # Baseline dataframe ###################################
            X_base[f"{k}_tt"] = transit[k].shortest_path_lengths(   # original code
            transit[k].get_node_ids(X.O_long,X.O_lat),         # original code
            transit[k].get_node_ids(X.D_long,X.D_lat)          # original code
            )                                                  # original code
            ########################################################
            
            break
        else:
            cont=cont+1

    def asignar_valor(row):
        if 1 <= row['Hora_Ini_E'] <= 12:
            return row['transit_0001_tt']
        elif 13 <= row['Hora_Ini_E'] <= 24:
            return row['transit_0102_tt']
        elif 25 <= row['Hora_Ini_E'] <= 36:
            return row['transit_0203_tt']
        elif 37 <= row['Hora_Ini_E'] <= 48:
            return row['transit_0304_tt']
        elif 49 <= row['Hora_Ini_E'] <= 60:
            return row['transit_0405_tt']
        elif 61 <= row['Hora_Ini_E'] <= 72:
            return row['transit_0506_tt']
        elif 73 <= row['Hora_Ini_E'] <= 84:
            return row['transit_0607_tt']
        elif 85 <= row['Hora_Ini_E'] <= 96:
            return row['transit_0708_tt']
        elif 97 <= row['Hora_Ini_E'] <= 108:
            return row['transit_0809_tt']
        elif 109 <= row['Hora_Ini_E'] <= 120:
            return row['transit_0910_tt']
        elif 121 <= row['Hora_Ini_E'] <= 132:
            return row['transit_1011_tt']
        elif 133 <= row['Hora_Ini_E'] <= 144:
            return row['transit_1112_tt']
        elif 145 <= row['Hora_Ini_E'] <= 156:
            return row['transit_1213_tt']
        elif 157 <= row['Hora_Ini_E'] <= 168:
            return row['transit_1314_tt']
        elif 169 <= row['Hora_Ini_E'] <= 180:
            return row['transit_1415_tt']
        elif 181 <= row['Hora_Ini_E'] <= 192:
            return row['transit_1516_tt']
        elif 193 <= row['Hora_Ini_E'] <= 204:
            return row['transit_1617_tt']
        elif 205 <= row['Hora_Ini_E'] <= 216:
            return row['transit_1718_tt']
        elif 217 <= row['Hora_Ini_E'] <= 228:
            return row['transit_1819_tt']
        elif 229 <= row['Hora_Ini_E'] <= 240:
            return row['transit_1920_tt']
        elif 241 <= row['Hora_Ini_E'] <= 252:
            return row['transit_2021_tt']
        elif 253 <= row['Hora_Ini_E'] <= 264:
            return row['transit_2122_tt']
        elif 265 <= row['Hora_Ini_E'] <= 276:
            return row['transit_2223_tt']
        elif 277 <= row['Hora_Ini_E'] <= 288:
            return row['transit_2324_tt']
        else:
            return None 

    # Create new column
    X['transit_tt'] = X.apply(asignar_valor, axis=1)
    # Don't know why but there are some extreme outliers on drive_tt. 70000 mins?
    X = X.loc[X['drive_tt'] < 200].reset_index(drop=True)
    X = X.drop(columns=[k + '_tt']) # k?
    X = X.loc[X['transit_tt'] <= 700]
    X = X.loc[X['walk_tt'] <= 2000]
    X = X.reset_index(drop=True)
    X = X.drop(columns=['Hora_Ini'])


    # Basline dataframe ############################################
    X_base['transit_tt'] = X_base.apply(asignar_valor, axis=1)
    # Don't know why but there are some extreme outliers on drive_tt. 70000 mins?
    X_base = X_base.loc[X_base['drive_tt'] < 200].reset_index(drop=True)
    X_base = X_base.drop(columns=[k + '_tt']) # k?
    X_base = X_base.loc[X_base['transit_tt'] <= 700]
    X_base = X_base.loc[X_base['walk_tt'] <= 2000]
    X_base = X_base.reset_index(drop=True)
    X_base = X_base.drop(columns=['Hora_Ini'])
    ############################################################

    # Codify family type manually

    X['Tipo_familia'].unique()
    family = {'Tipo': ['Hogar de una persona', 'Otros hogares sin niños', '2 adultos',
        '2 adultos con niño(s)', '1 adulto con niño(s)',
        'Otros hogares con niños'], 'Codigo': [1, 2, 3, 4, 5, 6]}
    family = pd.DataFrame(family)
    X = pd.merge(X, family, left_on='Tipo_familia', right_on='Tipo', how='left')
    X = X.drop(columns=['Tipo_familia', 'Tipo'])
    X.rename(columns={'Codigo': 'Tipo_familia'}, inplace=True)


    # Baseline dataframe ############################################
    X_base = pd.merge(X_base, family, left_on='Tipo_familia', right_on='Tipo', how='left')
    X_base = X_base.drop(columns=['Tipo_familia', 'Tipo'])
    X_base.rename(columns={'Codigo': 'Tipo_familia'}, inplace=True)
    ############################################################


    # Codify Mun_Ori y Mun_Des
    #aqui obtenemos los códigos  de cada pueblo 
    pueblos = pd.read_excel(towns_path + "data_towns.xlsx")
    eliminar = ['Region', 'Latitud', 'Longitud', 'Comarca',            # -> original code
        'Altitud (m.s.n.m.)', 'Superficie (kmÂ²)', 'PoblaciÃ³n (2019)', # -> original code
        'Densidad (hab./kmÂ²)', 'Incluido']                            # -> original code
    pueblos = pueblos.drop(columns=eliminar) 

    X = pd.merge(X, pueblos, left_on='Mun_Ori', right_on='Town')
    X = X.drop(columns=['Town', 'Mun_Ori'])
    X.rename(columns={'Código': 'Mun_Ori'}, inplace=True)
    X = pd.merge(X, pueblos, left_on='Mun_Des', right_on='Town')
    X = X.drop(columns=['Town', 'Mun_Des'])
    X.rename(columns={'Código': 'Mun_Des'}, inplace=True)


    # Baseline dataframe ############################################
    X_base = pd.merge(X_base, pueblos, left_on='Mun_Ori', right_on='Town')
    X_base = X_base.drop(columns=['Town', 'Mun_Ori'])
    X_base.rename(columns={'Código': 'Mun_Ori'}, inplace=True)

    X_base = pd.merge(X_base, pueblos, left_on='Mun_Des', right_on='Town')
    X_base = X_base.drop(columns=['Town', 'Mun_Des'])
    X_base.rename(columns={'Código': 'Mun_Des'}, inplace=True)
    ############################################################

    t1 = time.time()
    print()
    print('Total time:', (t1-t0)/60) 
    print()    

    #f=open('column_names_before.txt','w')
    #f.write(X.columns.values)
    #f.close()
    #X.to_csv('C:/Users/gfotidellaf/repositories/UI_SCP/assets/data/X_after_pp.csv', index=False)
    print()
    print('Final dataframe:')
    print(X.head(20))

    return X, X_base



        
        
    
    
