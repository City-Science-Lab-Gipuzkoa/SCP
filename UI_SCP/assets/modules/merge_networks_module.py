import numpy as np
#import pandas as pd
import os
import glob
from pathlib import Path
import re
import requests
from io import StringIO
import random
import pdb

#import matplotlib
#matplotlib.use('agg')  # allows notebook to be tested in Travis

import pandas as pd
#import cartopy.crs as ccrs
#import cartopy
#import matplotlib.pyplot as plt
#import pandana as pdna
import time

#!pip install pandana
import pandana as pdna

# !pip install cartopy
# import cartopy.crs as ccrs
# import cartopy

#!pip install urbanaccess
import urbanaccess as ua
from urbanaccess.config import settings
from urbanaccess.gtfsfeeds import feeds
from urbanaccess import gtfsfeeds
from urbanaccess.gtfs.gtfsfeeds_dataframe import gtfsfeeds_dfs
from urbanaccess.network import ua_network, load_network

import matplotlib
from matplotlib import pyplot as plt

pd.set_option('display.max_columns', None)

q=8

# # Load data to an Urban Access TRANSIT data object

t0 = time.time()
# I manually add all the feeds from the bus transit companies of Gipuzkoa
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
#feeds.add_feed(add_dict={'SCP_routes': '.\data\gtfsfeed_zips\routes.zip'})
# I download all these feeds, 70sg
gtfsfeeds.download()
#feeds.add_feed(add_dict={'SCP_routes': '..model\data\gtfsfeed_zips'})
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

urbanaccess_net = ua.network.ua_network

loaded_feeds = ua.gtfs.load.gtfsfeed_to_df(gtfsfeed_path="C:/Users/gfotidellaf/data/gtfsfeed_text",
                                           validation=validation,
                                           verbose=verbose,
                                           bbox=bbox,
                                           remove_stops_outsidebbox=remove_stops_outsidebbox,
                                           append_definitions=append_definitions)

# Create transit network
ua.gtfs.network.create_transit_net(gtfsfeeds_dfs=loaded_feeds,
                                   day='monday',
                                   timerange=['08:00:00', '09:00:00'],
                                   calendar_dates_lookup=None)

#filen = 'C:/Users/gfotidellaf/data/saved_network_h5/integrated_base_network.h5'
filen = 'C:/Users/gfotidellaf/data/saved_network_h5/pedestrian_net.h5'
if (os.path.isfile(filen)):
    
    print('\nLoading saved pedestrian networks...') 
    #saved_transit_net = ua.network.load_network(filename='saved_network_h5/integrated_base_network.h5')
    ped_net = ua.network.load_network(filename='saved_network_h5/pedestrian_net.h5')
    print('done!\n')

    # Crear la red de OSM (pedestrian)
    print('\nCreating pedestrian network from saved file...')
    ua.osm.network.create_osm_net(osm_edges=ped_net.net_edges, osm_nodes=ped_net.net_nodes, travel_speed_mph=3)
    print('done!\n')

    print('\nIntegrating all networks...')
    # Integrate saved and newly created tansit network
    #ua.network.integrate_network(urbanaccess_network=saved_transit_net,
    #                         headways=False) 
    ua.network.integrate_network(urbanaccess_network=urbanaccess_net,
                             headways=False)     
    print('successfully integrated existing and newly created networks!')
    #ua.plot.plot_net(nodes=saved_transit_net.net_nodes,
    #             edges=saved_transit_net.net_edges,
    #             bbox=bbox,
    #             fig_height=30, margin=0.02,
    #             edge_color='#999999', edge_linewidth=1, edge_alpha=1,
    #             node_color='black', node_size=1.1, node_alpha=1, node_edgecolor='none', node_zorder=3, nodes_only=False)
    ua.plot.plot_net(nodes=urbanaccess_net.net_nodes,
                 edges=urbanaccess_net.net_edges,
                 bbox=bbox,
                 fig_height=30, margin=0.02,
                 edge_color='#999999', edge_linewidth=1, edge_alpha=1,
                 node_color='black', node_size=1.1, node_alpha=1, node_edgecolor='none', node_zorder=3, nodes_only=False)

else:

    nodes, edges = ua.osm.load.ua_network_from_bbox(bbox=bbox, remove_lcn=True)
    # Crear la red de OSM (pedestrian)
    ua.osm.network.create_osm_net(osm_edges=edges, osm_nodes=nodes, travel_speed_mph=3)
    # integrate transit and pedestrian networks
    
    ua.network.integrate_network(urbanaccess_network=urbanaccess_net,
                             headways=False)

    urbanaccess_net.net_nodes['zone_id'] = urbanaccess_net.net_nodes['zone_id'].astype(str)
    """
    ped_net_pdna = pdna.network.Network(
                               nodes["x"],
                               nodes["y"],
                               edges["from"],
                               edges["to"],
                               edges[["weight","distance"]])
    """
    ped_net_pdna = pdna.network.Network(
                               urbanaccess_net.net_nodes["x"],
                               urbanaccess_net.net_nodes["y"],
                               urbanaccess_net.net_edges["from_int"],
                               urbanaccess_net.net_edges["to_int"],
                               urbanaccess_net.net_edges[["weight","distance"]])

    ped_net_pdna.save_hdf5('C:/Users/gfotidellaf/data/saved_network_h5/pedestrian_net.h5')
    #ua.network.save_network(urbanaccess_net, 'integrated_base_network.h5', dir='C:/Users/gfotidellaf/data/saved_network_h5/', overwrite_key=True, overwrite_hdf5=True)  
    