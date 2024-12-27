## #!/home/cslgipuzkoa/virtual_machine_disk/anaconda3/envs/SCP_test/bin/python
import dash
from dash import Dash
import dash_bootstrap_components as dbc
import dash_loading_spinners as dls
from dash import html, callback_context, ALL
from dash import dcc, Output, Input, State, callback, dash_table

from dash_extensions import Download
#from dash_extensions.enrich import html, Output, Input, State, callback, dcc

#from dash_extensions.snippets import send_file
from dash_extensions.snippets import send_data_frame

import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_daq as daq
import dash_html_components as html

from flask import Flask, render_template, send_from_directory
from flask import Flask, render_template, request, send_from_directory

import sys    
#root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
#root_dir = '/home/cslgipuzkoa/virtual_machine_disk/UI_SCP/assets/'
root_dir = 'C:/Users/gfotidellaf/repositories/test_UI_SCP/app/'
sys.path.append(root_dir + 'components')
from misc_functions import MiscFunctions as mf


import csv

import plotly.express as px
# plot test data
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import base64
import datetime
import io
from io import StringIO

#import re
import json
import pandas as pd
import geopy.distance
import numpy as np
import geopandas

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, adjusted_rand_score

from pylab import cm
import matplotlib

#from google.colab import drive
#drive.mount('/content/drive',  force_remount=True)

import sys
import os
from os import listdir
import shutil

import time
import getpass

from dash.long_callback import DiskcacheLongCallbackManager
## Diskcache
import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

stops_file = root_dir +'assets/data/all_bus_stops.csv'
stops_df = pd.read_csv(stops_file, encoding='latin-1')
stops_lat_lon = stops_df[['stop_lat','stop_lon']].to_numpy()

bus_icon = "https://i.ibb.co/HV0K5Fp/bus-stop.png" 
worker_icon = "https://i.ibb.co/W0H7nYM/meeting-point.png"
coworking_icon = "https://i.ibb.co/J2qXGKN/coworking-icon.png"
IndPark_icon = "https://i.ibb.co/bLytVQM/industry-icon.png"
IndPark_pos = (43.25632640541216, -2.029996706597628)
center = (43.26852347667122, -1.9741372404905988)
#    iconUrl= 'https://uxwing.com/wp-content/themes/uxwing/download/location-travel-map/bus-stop-icon.png',
#    iconUrl= "https://i.ibb.co/6n1tzcQ/bus-stop.png",
custom_icon_bus = dict(
    iconUrl= bus_icon,
    iconSize=[40,40],
    iconAnchor=[22, 40]
)
custom_icon_worker = dict(
    iconUrl= worker_icon,
    iconSize=[40,40],
    iconAnchor=[22, 40]
)
custom_icon_coworking = dict(
    iconUrl= coworking_icon,
    iconSize=[40,40],
    iconAnchor=[22, 40]
)
custom_icon_IndPark = dict(
    iconUrl= IndPark_icon,
    iconSize=[40,40],
    iconAnchor=[22, 40]
)


stops_actions = [
                 {'label': 'Add bus stop', 'value': 'AS'},    
                 {'label': 'Delete bus stop', 'value': 'DS'},                   
                ]
cow_actions = [{'label': 'Add coworking hub', 'value': 'AC'},
               {'label': 'Delete coworking hub', 'value': 'DC'}                   
            ]
def register_callbacks(app):
    # The following callback is just needed to refresh the map when the page is loaded, otherwise the map #############################
    # does not appear
    @app.callback([Output('internal-value_first_refresh_1','data'),
                Output('map_1','children',allow_duplicate=True)],
                State('internal-value_first_refresh_1','data'),
                [Input('title_SCP_1', 'children')],      # -> dummy variable, it does not matter, we just need a trigger variable
                prevent_initial_call='initial_duplicate'
                )
    def first_page_refresh(first_refresh, N):
        #center = (43.26802146639027, -1.9777370771095362)
        IndParkCoord = (43.25632640541216, -2.029996706597628)
        IndPark_marker = [dl.Marker(dl.Tooltip("Industrial Park"), position=IndParkCoord, icon=custom_icon_IndPark, id='IndPark_1')]
        if first_refresh == 0:
            newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + IndPark_marker,
                                center=center, zoom=12, id="map_1",
                                style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
            first_refresh = 1
            return [first_refresh, newMap]
    ###################################################################################################################################

    
    @app.callback(
        [Output('user_ip', 'data'),
        Output('root_dir_1','data')],
        [State('user_ip', 'modified_timestamp')],     
        [Input('url', 'pathname'), Input('user_ip', 'data')]
    )
    def update_user_ip(modified_timestamp, pathname, user_ip):
        user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        print()
        print()
        print('user IP: ', user_ip)   
        print()
        print()
        #root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
        #root_dir = '/home/cslgipuzkoa/virtual_machine_disk/UI_SCP/assets/'
        root_dir = 'C:/Users/gfotidellaf/repositories/test_UI_SCP/app/'
        with open(root_dir +'assets/data/'+'login_data.txt','r') as f:
            #username = f.readline().split(' ')[0]
            username = f.readlines()[-1].split(' ')[0]
        new_root_dir = root_dir[:-1] + '_' + username + '/'

        if os.path.exists(new_root_dir):
            # Delete Folder code
            shutil.rmtree(new_root_dir)
            print("The folder has been deleted successfully!")
            print()
        print('Generating a user-specific copy of the root directory...')
        shutil.copytree(root_dir, new_root_dir)
        root_dir = new_root_dir
        print(root_dir)
        print('done!')
        #
        # sys.path.append(root_dir + 'modules')

        print()
        print('Cleaning folders...')
        shutil.rmtree(root_dir + 'assets/data/input_data_MCM/GTFS_feeds')
        shutil.rmtree(root_dir + 'assets/data/input_data_MCM/transit_together_24h')
        shutil.copytree(root_dir + 'assets/data/input_data_MCM/GTFS_feeds_backup', root_dir + 'assets/data/input_data_MCM/GTFS_feeds')
        shutil.copytree(root_dir + 'assets/data/input_data_MCM/transit_together_24h_backup', root_dir + 'assets/data/input_data_MCM/transit_together_24h')
        print('done!')
        print()
        return [user_ip, root_dir]
    

    @app.callback(
        Output('user_ip', 'modified_timestamp'),
        [Input('url', 'pathname')]
    )
    def set_modified_timestamp(pathname):
        from datetime import datetime
        return datetime.now().timestamp()


    # Left sidebar subpanels #############################################
    @callback(
        Output("Load_data_panel_1", "is_open"),
        [Input("Load_data_button_1", "n_clicks")],
        [State("Load_data_panel_1", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @callback(
        Output("Run_baseline_panel_1", "is_open"),
        [Input("Run_baseline_button_1", "n_clicks")],
        [State("Run_baseline_panel_1", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open


    @callback(
        Output("Intervention_type_panel_1", "is_open"),
        [Input("Intervention_type_button_1", "n_clicks")],
        [State("Intervention_type_panel_1", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open


    @callback(
        Output("Select_time_panel_1", "is_open"),
        [Input("Select_time_button_1", "n_clicks")],
        [State("Select_time_panel_1", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open


    @callback(
        Output("Advanced_settings_panel_1", "is_open"),
        [Input("Advanced_settings_button_1", "n_clicks")],
        [State("Advanced_settings_panel_1", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open
    #################################################################


    #### Update internal values from sliders and dropdown menus #######################
    # Output('internal-value_scenario','data',allow_duplicate=True),
    @callback([
            Output('internal-value_bus_number_1', 'data',allow_duplicate=True),
            ],
            Input('num_buses_1','value'),
            prevent_initial_call=True)
    def update_remote_work(Nroutes):
        print('number of routes updated to: ', Nroutes)
        return [Nroutes]

    @callback([
            Output('internal-value_remote_days_1', 'data',allow_duplicate=True),
            Output('internal-value_remote_workers_1', 'data',allow_duplicate=True)
            ],
            [
            Input('choose_remote_days_1','value'),
            Input('choose_remote_workers_1','value')
            ],
            prevent_initial_call=True)
    def update_remote_work(rem_days, rem_work):
        return [rem_days, rem_work]


    @callback([
            Output('internal-value_eCar_adoption_1', 'data',allow_duplicate=True),
            Output('internal-value_eCar_co2_km_1', 'data',allow_duplicate=True)
            ],
            [
            Input('choose_eCar_adoption_1','value'),
            Input('choose_eCar_co2_km_1','value')
            ],
            prevent_initial_call=True)
    def update_remote_work(eCarAdop, eCarCO2):
        print('inside update ECa')
        print('Percentage of electric cars: ')
        print(eCarAdop)
        print('Electric car co2: ')
        print(eCarCO2)
        return [eCarAdop, eCarCO2]

    @callback([
            Output('internal-value_coworking_days_1', 'data',allow_duplicate=True)
            ],
            Input('choose_coworking_days_1','value'),
            prevent_initial_call=True)
    def update_coworking(cow_days):
        print()
        print('updating coworking days')
        print(cow_days)
        print()    
        return [cow_days]


    @callback([
            Output('internal-value_trip_num_1', 'data',allow_duplicate=True),
            ],
            Input('num_trips_1','value'),
            prevent_initial_call=True)
    def update_trip_number(Ntrips):
        print()
        print('updating trip number')
        print(Ntrips)
        print()
        return [Ntrips]

    @callback([
            Output('internal-value_trip_freq_1', 'data',allow_duplicate=True),
            ],
            Input('trip_freq_1','value'),
            prevent_initial_call=True)
    def update_trip_freq(TripFreq):
        return [TripFreq]

    #          Input('choose_start_hour_1','value'),
    @callback([
            Output('internal-value_start_hour_1', 'data',allow_duplicate=True),
            ],
            Input('choose_start_time_1','value'),
            prevent_initial_call=True)
    def update_start_time(StartHour):
        return [StartHour]

    @callback([
            Output('internal-value_co2_km_car_1', 'data',allow_duplicate=True),
            Output('internal-value_co2_km_bus_1', 'data',allow_duplicate=True),
            Output('internal-value_co2_km_train_1', 'data',allow_duplicate=True),
            Output('internal-value_bus_train_ratio_1', 'data',allow_duplicate=True)
            ],
            [
            Input('choose_co2_km_car_1','value'),
            Input('choose_co2_km_bus_1','value'),
            Input('choose_co2_km_train_1','value'),
            Input('choose_bus_train_ratio_1','value')
            ],
            prevent_initial_call=True)
    def update_co2_values(co2_car, co2_bus, co2_train, bus_ratio):
        return [co2_car, co2_bus, co2_train, bus_ratio]

    ###########################################################################


    # Output('internal-value_scenario','data',allow_duplicate=True),
    @callback([Output('Indicator_panel_1', 'figure',allow_duplicate=True),
            Output('map_1','children',allow_duplicate=True),
            Output('graph2','figure',allow_duplicate=True),
            Output('Indicator_panel_3', 'figure',allow_duplicate=True),
            Output("Tab_3", "children",allow_duplicate=True),
            Output('internal-value_scenario_1','data',allow_duplicate=True),
            Output('internal-value_calculated_scenarios_1','data',allow_duplicate=True)],
            [
            State('root_dir_1', 'data'),
            State('worker_data_1', 'data'),
            State('internal-value_calculated_scenarios_1','data'),
            State('internal-value_remote_days_1','data'),
            State('internal-value_remote_workers_1','data'),
            State('internal-value_eCar_adoption_1','data'),
            State('internal-value_eCar_co2_km_1','data'),
            State('internal-value_route_opt_done_1','data'),
            State('internal-value_routes_len_1','data'),
            State('internal-value_stops_1','data'),
            State('internal-value_coworking_1','data'),
            State('internal-value_coworking_days_1','data'),
            State('internal-value_ind_park_coord_1','data'),
            State('internal-value_bus_number_1','data'),
            State('choose_start_time_1','value'),
            State('choose_co2_km_car_1','value'),
            State('choose_co2_km_bus_1','value'),
            State('choose_co2_km_train_1','value'),
            State('choose_bus_train_ratio_1','value'),
            State('Tab_3', 'children')
            ],
            [Input('run_baseline_1','n_clicks'),
            Input('run_MCM_1', 'n_clicks')],
            prevent_initial_call=True)
    def run_MCM_callback(root_dir, workerData, stored_scenarios, NremDays, NremWork, NeCar, co2km_eCar, RouteOptDone, RouteLengths, StopsCoords, CowoFlags, CowDays, IndParkCoord, Nbuses, TransH, co2km_car, co2km_bus, co2km_train, bus_train_ratio, Tab3, Nclicks_base, Nclicks):
        CowoIn = np.nonzero(CowoFlags)[0]
        CowoCoords = np.array(StopsCoords)[CowoIn]
        TransH = int(TransH.split(':')[0])

        df = pd.DataFrame.from_dict(workerData)    
        #result = run_MCM(df, root_dir, TransH, RouteOptDone, gkm_car, gkm_bus, co2lt, NremDays, NremWork, CowoCoords, CowDays)  
        # run_MCM(trips_ez, root_Dir, Transh, routeOptDone, co2km_car=0.1081, co2km_bus=1.3, co2km_train=0.049, bus_train_ratio=0.8, NremDays=0, NremWork=0, CowCoords=[], CowDays=0):
        result = mf.run_MCM(df, root_dir, TransH, RouteOptDone, co2km_car, co2km_eCar, co2km_bus, co2km_train, bus_train_ratio, NremDays, NremWork, NeCar, CowoCoords, CowDays)  

        # additional CO2 quota due to company bus service (if any) ###########
        if RouteOptDone:
            #MCM_data_dir = 'data/input_data_MCM/'
            MCM_data_dir = 'assets/data/input_data_MCM/'
            baseline_scenario = pd.read_csv(root_dir + MCM_data_dir + 'baseline_scenario.csv')
            if os.path.isfile(root_dir + MCM_data_dir + 'BL_plus_PT.csv'):
                BL_plus_PT = pd.read_csv(root_dir + MCM_data_dir + 'BL_plus_PT.csv')
                temp = pd.concat([baseline_scenario[['Mode','Coworking_days']], BL_plus_PT['Mode']], axis=1, ignore_index=True)
            else:
                result.to_csv(root_dir + MCM_data_dir + 'BL_plus_PT.csv')
                temp = pd.concat([baseline_scenario[['Mode','Coworking_days']], result['Mode']], axis=1, ignore_index=True)

            temp.columns = ['Mode1','Coworking_days','Mode2']
            temp_df = temp.loc[(temp['Mode1']=='Car') & (temp['Mode2']=='PT') & (temp['Coworking_days']==0)].dropna()
                
            result.loc[temp_df.index.values, 'CO2'] = 0
            #result.to_csv(root_dir + MCM_data_dir + 'calculated_scenario.csv')
            additional_co2 = sum ([RouteLengths_i*(1/1000)*co2km_bus for RouteLengths_i in RouteLengths])
            print()
            print('CO2 emissions of Car->PT workers set to zero!')
        else:
            additional_co2 = 0

        out = mf.plot_result(result, NremDays, NremWork, CowDays, NeCar, Nbuses, additional_co2, co2km_eCar, stored_scenarios, IndParkCoord, StopsCoords, CowoFlags)

        scenario = pd.DataFrame(result.drop(columns='geometry'))
        scenario_json = scenario.to_dict('records') # not working?
        ##return [out[0],out[1],out[2],out[3], out[4], scenario_json]

        #return [out[0],out[1],out[2], out[0], scenario_json]

        indicators_n = html.Div(
                [              
                dcc.Graph(
                    figure=out[3],
                    style={'width': '60vh', 'height': '100vh'}) 
                ]
                )

        print()
        print('New calculation done with:')
        print('percent of eCars:',NeCar)
        print('co2km_ecar:',co2km_eCar)
        #return [fig_total, fig_decomp, new_map, Tab3 + [dbc.Col(indicators_n, width='auto')]]
        #return [out[0], out[1], out[2], out[0], Tab3 + [dbc.Col(indicators_n, width='auto')], scenario_json, new_stored_scenarios]
        return [out[0], out[1], out[2], out[3], Tab3 + [dbc.Col(indicators_n, width='auto')], scenario_json, out[4]]
        #      fig_total, fig_comp, fig_decomp, new_map, new_stored_scenarios

    @callback([
            Output('map_1','children',allow_duplicate=True)],
            State('internal-value_scenario_1','data'),
            State('internal-value_ind_park_coord','data'),
            Input('lc_1', "baseLayer"),
            prevent_initial_call=True)
    def switch_layer(Scen, IndParkCoord, layer):

        print('switching layer...')
        print(layer)

        markers_all_1 = []
        markers_remote_1 = []
        markers_cow_1 = []
        markers_remote_cow_1 = []
        markers_comm_1 = []

        Legend_workers =  html.Div(
            style={
                'position': 'absolute',
                'top': '650px',
                'left': '700px',
                'zIndex': 1000,  # Adjust the z-index as needed
                },
            children=[
                html.Div(
                    style={
                        'display': 'inline-block',
                        'margin-right': '25px',
                    },
                    children=[
                        html.Div(
                            style={
                                'width': '25px',
                                'height': '25px',
                                'backgroundColor': '#f1948a',
                                "border":"2px black solid",
                                "transform": "rotate(45deg)"                            
                            }
                        ),
                        html.Span('Remote', style={'color': 'blue', 'font-size': '14px', 'font-weight': 'bold'})
                    ]
                ),
                html.Div(
                    style={
                        'display': 'inline-block',
                        'margin-right': '15px',
                    },
                    children=[
                        html.Div(
                            style={
                                'width': '25px',
                                'height': '25px',
                                "border":"2px black solid",
                                'backgroundColor': '#f1948a',
                            }
                        ),
                        html.Span('Coworking', style={'color': 'blue', 'font-size': '14px', 'font-weight': 'bold'})
                    ]
                ),
                html.Div(
                    style={
                        'display': 'inline-block',
                        'margin-right': '5px',
                    },
                    children=[
                        html.Div(
                            style={
                                'width': '0',
                                'height': '0',
                                'borderTop': '28px solid #f1948a',
                                'borderLeft': '22px solid transparent',
                                'borderRight': '22px solid transparent',                        
                            }
                        ),
                        html.Span('Remote + coworking', style={'color': 'blue', 'font-size': '14px', 'font-weight': 'bold'})
                    ]
                ),

            ]
        )

        Legend_bus_stops =  html.Div(
            style={
                'position': 'absolute',
                'top': '650px',
                'left': '700px',
                'zIndex': 1000,  # Adjust the z-index as needed
                },
            children=[
                html.Div(
                    style={
                        'display': 'inline-block',
                        'margin-right': '10px',
                    },
                    children=[
                        html.Div(
                            style={
                                'width': '25px',
                                'height': '25px',
                                'borderRadius': '50%',
                                'backgroundColor': '#cb4335',
                                "border":"2px black solid"                            
                            }
                        ),
                        html.Span('bus stops',style={'color': 'blue', 'font-size': '14px', 'font-weight': 'bold'})
                    ]
                ),
                html.Div(
                    style={
                        'display': 'inline-block',
                        'margin-right': '10px',
                    },
                    children=[
                        html.Div(
                            style={
                                'width': '25px',
                                'height': '25px',
                                'borderRadius': '50%',
                                "border":"2px black solid",
                                'backgroundColor': '#f4d03f',
                            }
                        ),
                        html.Span('no bus stops',style={'color': 'blue', 'font-size': '14px', 'font-weight': 'bold'})
                    ]
                )
            ]
        )

        Legend_family =  html.Div(
            style={
                'position': 'absolute',
                'top': '650px',
                'left': '700px',
                'zIndex': 1000,  # Adjust the z-index as needed
                },
            children=[
                html.Div(
                    style={
                        'display': 'inline-block',
                        'margin-right': '10px',
                    },
                    children=[
                        html.Div(
                            style={
                                'width': '25px',
                                'height': '25px',
                                'borderRadius': '50%',
                                'backgroundColor': '#2b62c0',
                                "border":"2px black solid"                            
                            }
                        ),
                        html.Span('no kids',style={'color': 'blue', 'font-size': '14px', 'font-weight': 'bold'})
                    ]
                ),
                html.Div(
                    style={
                        'display': 'inline-block',
                        'margin-right': '10px',
                    },
                    children=[
                        html.Div(
                            style={
                                'width': '25px',
                                'height': '25px',
                                'borderRadius': '50%',
                                "border":"2px black solid",
                                'backgroundColor': '#f4d03f',
                            }
                        ),
                        html.Span('kids',style={'color': 'blue', 'font-size': '14px', 'font-weight': 'bold'})
                    ]
                )
            ]
        )
        
        Legend = []
        if Scen:
            Legend = Legend_workers
            scen_df = pd.DataFrame(Scen)
            scen_df = geopandas.GeoDataFrame(
                    scen_df, geometry=geopandas.points_from_xy(scen_df.O_long, scen_df.O_lat), crs="EPSG:4326"
                    )

            for i_pred in scen_df.itertuples():

                if layer == "CO2":
                    #maxCO2 = scen_df['CO2'].max()
                    maxCO2 = scen_df.groupby("Mode")['CO2'].max()[i_pred.Mode]

                    #color = generate_color_gradient(maxCO2_worst_case,i_pred.CO2, i_pred.Mode) 
                    color = mf.generate_color_gradient(maxCO2,i_pred.CO2, i_pred.Mode)
                    if i_pred.Mode == 'PT':
                        print('maxCO2: ',maxCO2)
                        print('CO2: ',i_pred.CO2)
                    text = 'CO2: ' + '{0:.2f}'.format(i_pred.CO2) + ' Kg ' + '(' + i_pred.Mode + ')' + '<br>' +  'Weekly distance: ' + '{0:.2f}'.format(i_pred.distance_week/1000) + ' Km'

                elif layer == "CO2/CO2_target":
                    #maxCO2 = scen_df.groupby("Mode")['CO2_over_aver'].max()[i_pred.Mode]
                    #color = generate_color_gradient(maxCO2,i_pred.CO2_over_aver, i_pred.Mode)
                    color = mf.generate_color_gradient(1,i_pred.CO2_over_target, i_pred.Mode)  
                    text = 'CO2_over_2030_target: ' + '{0:.2f}'.format(i_pred.CO2_over_target) + ' (' + i_pred.Mode + ')' + '<br>' +  'Weekly distance: ' + '{0:.2f}'.format(i_pred.distance_week/1000) + ' Km'

                #elif layer == "weighted_d":
                #    #maxCO2 = scen_df.groupby("Mode")['weighted_d'].max()[i_pred.Mode]
                #    #color = generate_color_gradient(maxCO2,i_pred.weighted_d, i_pred.Mode)
                #    color = generate_color_gradient(1,i_pred.weighted_d, i_pred.Mode) 
                #    text = 'weighted_d: ' + '{0:.2f}'.format(i_pred.weighted_d) + ' (' + i_pred.Mode + ')' + '<br>' +  'Weekly distance: ' + '{0:.2f}'.format(i_pred.distance_week/1000) + ' Km'  

                elif layer == "Has a bus stop":            
                    #maxCO2 = scen_df.groupby("Mode")['weighted_n'].max()[i_pred.Mode] 
                    #color = generate_color_gradient(maxCO2,i_pred.weighted_d, i_pred.Mode)
                    #color = generate_color_gradient(1,i_pred.n_close_stops, i_pred.Mode)
                    if (i_pred.Mode == "Car") and (i_pred.n_close_stops > 0):
                        color = '#cb4335'
                    else:
                        color = '#f4d03f'

                    text = 'N. bus stops: ' + '{0:2d}'.format(int(i_pred.n_close_stops)) + ' ( using: ' + i_pred.Mode + ')' + '<br>' +  'Weekly distance: ' + '{0:.2f}'.format(i_pred.distance_week/1000) + ' Km'  
                    Legend = Legend_bus_stops

                else:
                    family_types = ['Hogar de una persona', 'Otros hogares sin niños', '2 adultos',
                                    '2 adultos con niño(s)', '1 adulto con niño(s)',
                                    'Otros hogares con niños']
                    colors = mf.generate_colors(len(family_types))
                    color = colors[i_pred.Tipo_familia-1]
                    if i_pred.Tipo_familia in range(3) and i_pred.Mode == 'Car':
                        #color = '#C0392B'
                        color = '#2b62c0'
                    else:
                        color = '#f4d03f'                    
                    text = 'Family type: ' + family_types[i_pred.Tipo_familia-1] + ' (' + i_pred.Mode + ')' + '<br>' +  'Weekly distance: ' + '{0:.2f}'.format(i_pred.distance_week/1000) + ' Km'  
                    Legend = Legend_family

                n_rw = int(i_pred.Rem_work)
                text = text + '<br>' + 'Remote working: ' + (['Yes']*n_rw + ['No'])[n_rw-1]

                try:
                    n_cw = int(i_pred.Coworking)
                except:
                    n_cw = 0    
                text = text + '<br>' + 'Coworking: ' + (['Yes']*n_cw + ['No'])[n_cw-1]  
        
                marker_i = dl.CircleMarker(
                            id=str(i_pred),
                            children=[dl.Tooltip(content=text)],
                            center=[i_pred.geometry.y, i_pred.geometry.x],
                            radius=10,
                            fill=True,
                            fillColor=color,
                            fillOpacity=1.0,                            
                            stroke=True,
                            weight = 2.0,
                            color='black'
                            )

                try:
                    if  i_pred.Rem_work > 0.0 and i_pred.Coworking == 0.0:
                        #marker_i = dl.Marker(children=[dl.Tooltip(content=text)], 
                        #                     position=[i_pred.geometry.y, i_pred.geometry.x], 
                        #                     icon=custom_icon_home, 
                        #                     id=str(i_pred))
                        marker_i = dl.Marker(
                            id=str(i_pred),
                            children=[dl.Tooltip(content=text, offset={"x": 5, "y": 10})],
                            position=[i_pred.geometry.y, i_pred.geometry.x],
                            icon=mf.create_diamond_marker(color, (0, 0, 0))
                        )
                        markers_remote_cow_1.append(marker_i)
                except:
                    pass
                try:
                    if  i_pred.Coworking > 0.0 and i_pred.Rem_work == 0.0:
                        #marker_i = dl.Marker(children=[dl.Tooltip(content=text)], 
                        #                     position=[i_pred.geometry.y, i_pred.geometry.x], 
                        #                     icon=custom_icon_coworking, 
                        #                     id=str(i_pred))
                        marker_i = dl.Marker(
                                id=str(i_pred),
                                children=[dl.Tooltip(content=text, offset={"x": 5, "y": 10})],
                                position=[i_pred.geometry.y, i_pred.geometry.x],
                                icon=mf.create_square_marker(color, (0, 0, 0))
                        )                     
                        markers_cow_1.append(marker_i)
                except:
                    pass  

                try:
                    if  i_pred.Coworking > 0.0 and i_pred.Rem_work > 0.0:
                        #marker_i = dl.Marker(children=[dl.Tooltip(content=text)], 
                        #                     position=[i_pred.geometry.y, i_pred.geometry.x], 
                        #                     icon=custom_icon_coworking, 
                        #                     id=str(i_pred))
                        marker_i = dl.Marker(
                                id=str(i_pred),
                                children=[dl.Tooltip(content=text, offset={"x": 5, "y": 10})],
                                position=[i_pred.geometry.y, i_pred.geometry.x],
                                icon=mf.create_triangle_marker(color, (0, 0, 0))
                        )                     
                        markers_remote_cow_1.append(marker_i)
                except:
                    pass 

                markers_all_1.append(marker_i)  

        markers_comm_1 = list(set(markers_all_1) - set(markers_remote_1) - set(markers_cow_1) )

        Baselayer = [dl.BaseLayer(dl.TileLayer(), name='CO2', checked=False),
                    dl.BaseLayer(dl.TileLayer(), name='CO2/CO2_target', checked=False),
                    #dl.BaseLayer(dl.TileLayer(), name='weighted_d', checked=False),
                    dl.BaseLayer(dl.TileLayer(), name='Has a bus stop', checked=False),
                    dl.BaseLayer(dl.TileLayer(), name='Family type', checked=False)]

        OL1 = dl.LayerGroup(markers_all_1)
        OL2 = dl.LayerGroup(markers_remote_1)
        OL3 = dl.LayerGroup(markers_cow_1)
        OL4 = dl.LayerGroup(markers_comm_1)
        OL5 = dl.LayerGroup(markers_remote_cow_1)
    
        children = [    Legend,
                        dl.TileLayer(),
                        dl.ScaleControl(position="topright"),
                        dl.LayersControl(Baselayer +
                                        [dl.Overlay(OL1, name="all", checked=True),
                                        dl.Overlay(OL2, name="remote", checked=False),
                                        dl.Overlay(OL3, name="coworking", checked=False),
                                        dl.Overlay(OL4, name="home-headquarters", checked=False),
                                        dl.Overlay(OL5, name="remote and coworking", checked=False)], 
                                        id="lc_1"
                                        )
                        ]
        #Eskuz_marker = [dl.Marker(dl.Tooltip("Eskuzaitzeta Industrial Park"), position=Eskuz_pos, icon=custom_icon_Eskuz, id='Eskuz_1')]
        IndPark_marker = [dl.Marker(dl.Tooltip("Industrial Park"), position=IndParkCoord, icon=custom_icon_IndPark, id='IndPark_1')]

        children = children + IndPark_marker
        new_map = dl.Map(children, center=center,
                                            zoom=12,                        
                                            id="map_1",
                                            style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
            
        return [new_map]
        


    # Download files callbacks ###########################################
    # Download files callbacks ###########################################
    @callback([Output("download_template_1", "data")],
            [State('root_dir_1','data')],
            Input('button_download_template_1', 'n_clicks'),
            prevent_initial_call=True)
    def download_template(rootDir, Nclicks):
        tmpFile = rootDir + 'data/template_data.csv'
        template_df = pd.read_csv(tmpFile)  
        return [send_data_frame(template_df.to_csv, "template_input_data.csv", index=False)]



    @callback([Output("download_scenario_1", "data")],
            [
            State('internal-value_scenario_1','data')],
            Input('button_download_scenario_1', 'n_clicks'),
            prevent_initial_call=True)
    def download_scenario(Scen, Nclicks):
        scen_df = pd.DataFrame(Scen)
        print('data to download:')
        print(scen_df.head())
        return [send_data_frame(scen_df.to_csv, "scenario.csv", index=False)]

    @callback([Output("download_inputs_1", "data")],
            [
            State('internal-value_remote_days_1', 'data'),
            State('internal-value_remote_workers_1', 'data'),
            State('internal-value_coworking_days_1','data'),          
            State('internal-value_bus_number_1','data'),          
            State('choose_start_time_1','value'),
            State('choose_co2_km_car_1','value'),
            State('choose_co2_km_bus_1','value'),
            State('choose_co2_km_train_1','value'),
            State('choose_bus_train_ratio_1','value')],
            Input('button_download_scenario_1', 'n_clicks'),
            prevent_initial_call=True)
    def download_inputs(NremDays, NremWork, CowDays, Nbuses, TransH, co2_km_car, co2_km_bus, co2_km_train, bus_train_ratio, Nclicks):
        inputs_dict = {'NremDays': NremDays, 'NremWork':NremWork, 
                    'CowDays': CowDays,                    
                    'Nbuses': Nbuses,
                    'TransH': TransH, 
                    'co2_km_car': co2_km_car, 
                    'co2_km_bus': co2_km_bus, 
                    'co2_km_train': co2_km_train, 
                    'bus_train_ratio': bus_train_ratio 
                    }
        inputs_df = pd.DataFrame(inputs_dict, index=[0])
        print('trying to save inputs...')
        return [send_data_frame(inputs_df.to_csv, "inputs.csv", index=False)]

    @callback([Output("download_StopsCowHubs_1", "data")],
            [
            State('internal-value_stops_1','data'),
            State('internal-value_coworking_1','data')],
            Input('button_download_scenario_1', 'n_clicks'),
            prevent_initial_call=True)
    def download_stops(StopsCoords, CowoFlags, Nclicks):
        if len(StopsCoords)>0:
            lats, lons = map(list, zip(*StopsCoords))
            stops_and_cow_df = pd.DataFrame(np.column_stack([lats, lons, CowoFlags]), 
                                columns=['lat', 'lon', 'CowHub'])
            return [send_data_frame(stops_and_cow_df.to_csv, "StopsCowHubs.csv", index=False)]




    @callback([Output('worker_data_1', 'data',allow_duplicate=True),
            Output('n_clusters_1','value',allow_duplicate=True)],
                [Input('upload-data_1', 'contents'),
                State('upload-data_1', 'filename'),
                State('upload-data_1', 'last_modified'),            
                State('choose_start_time_1', 'value'),],
                prevent_initial_call=True)
    def load_worker_data(list_of_contents, list_of_names, list_of_dates, startHour):       
        if list_of_contents is not None:
            children = [
                mf.parse_contents(c, n, d) for c, n, d in
                zip(list_of_contents, list_of_names, list_of_dates)]
            works_data = children[0]
            startHour = 8
            suggested_N_clusters = mf.suggest_clusters(works_data, startHour)
            #print('workers dataframe?', works_data)
            workers = pd.DataFrame(works_data.drop(columns='geometry'))
            workers_dict = workers.to_dict('records') 
            
            return [workers_dict,suggested_N_clusters]
    ############################################################################################

    @app.callback([Output('internal-value_stops_1','data',allow_duplicate=True),
                Output('internal-value_coworking_1','data',allow_duplicate=True),
                Output('map_1','children',allow_duplicate=True)],
                State("n_clusters_1", "value"),
                State('worker_data_1', 'data'),

                State('internal-value_stops_1','data'),
                State('internal-value_coworking_1','data'),
                State('internal-value_ind_park_coord_1','data'),

                State('root_dir_1','data'),
                State('choose_start_time_1', 'value'),
                State('internal-value_scenario_1','data'),     
                Input("propose_stops_1", "n_clicks"),
                prevent_initial_call=True
                )
    def propose_stops(n_clusters,workerData, StopsCoords, CowFlags, IndParkCoord, root_dir, startHour, result_json, Nclick):
        if Nclick > 0:  
            #sys.path.append(root_dir + 'modules')     
            sys.path.append(root_dir + 'components')  
            import find_stops_module   
            n_clusters  = int(n_clusters)
            cutoff = 0.99 # cutoff for maximum density: take maxima which are at least cutoff*max  
            workers_DF = pd.DataFrame.from_dict(workerData)
            startHour = int(startHour.split(':')[0])
            stops_DF = pd.read_csv(root_dir + 'assets/data/'+ "all_bus_stops.csv", encoding='latin-1')
            bus_stops_df,model,yhat = find_stops_module.FindStops(workers_DF, startHour, stops_DF, n_clusters, cutoff)
            out = ''
            St = StopsCoords
            Cow = CowFlags
            for ind in bus_stops_df.index:
                out = out + str(bus_stops_df['Lat'][ind]) + ',' + str(bus_stops_df['Lon'][ind]) +';'
                St.append((bus_stops_df['Lat'][ind],bus_stops_df['Lon'][ind]))
                Cow.append(0)
            
            markers = []
            for i, pos in enumerate(St):
                if Cow[i] == 0:
                    marker_i = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i})
                else:
                    marker_i = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_coworking, id={'type': 'marker', 'index': i})
                markers.append(marker_i)

            #markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
            IndPark_marker = [dl.Marker(dl.Tooltip("Industrial Park"), position=IndParkCoord, icon=custom_icon_IndPark, id='IndPark_1')]

            if len(result_json) ==0:
                newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers + IndPark_marker,
                            center=center, zoom=12, id="map_1",
                            style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
            else:
                result = pd.DataFrame.from_dict(result_json) 
                result = geopandas.GeoDataFrame(
                        result, geometry=geopandas.points_from_xy(result.O_long, result.O_lat), crs="EPSG:4326"
                        )
                newMap = mf.generate_map(result, Cow, St, markers + IndPark_marker)
            return [St,Cow,newMap]    

    @app.callback([Output('map_1','children',allow_duplicate=True)],
                    State("n_clusters_1", "value"),
                    State('worker_data_1', 'data'),
                    State('internal-value_ind_park_coord_1', 'data'),
                    State('choose_start_time_1', 'value'),
                [Input("show_workers_1", "n_clicks")],
                prevent_initial_call=True
                )
    def show_workers(n_clusters,workerData, IndParkCoord, startHour, N):
        workers_df = pd.DataFrame.from_dict(workerData)
        IndPark_marker = [dl.Marker(dl.Tooltip("Industrial Park"), position=IndParkCoord, icon=custom_icon_IndPark, id='IndPark_1')]

        try:
            startHour = int(startHour.split(':')[0])
            # select specific hour #####################################################
            workers_df['Hora_Ini_E'] = workers_df['Hora_Ini'].copy()
            workers_df['Hora_Ini'] = pd.to_datetime(workers_df['Hora_Ini_E'], format='%H:%M')
            workers_df['Hora_Ini_E'] = ((workers_df['Hora_Ini'] - pd.to_datetime('00:00', format='%H:%M')).dt.total_seconds() / 300).astype(int) + 1
            workers_df['Hora_Ini'] = workers_df['Hora_Ini'].dt.strftime('%H:%M')
            convertido=((startHour*60*60)/300)+1
            # Get 1-hour interval between "convertido" and "convertido+1hour"? #######
            workers_df=workers_df[workers_df['Hora_Ini_E'] <= (convertido+11)]
            workers_df=workers_df[workers_df['Hora_Ini_E'] >= convertido]
            ############################################################################    
        except:
            pass

        if len(workers_df.index) > 0:
            clusters, clusters_size = mf.drawclusters(workers_df,n_clusters)
            n_max = max(len(x) for x in clusters ) # find maximum size of the clusters
            n_min = min(len(x) for x in clusters ) # find maximum size of the clusters
            #colors = generate_colors(n_clusters)
            n_colors = n_max
            #n_colors = 255
            print(len(clusters), len(clusters_size), n_clusters)
            #colors = [generate_color_gradient(n_max, len(clusters[i])) for i in range(len(clusters))]
            colors = [mf.generate_color_gradient(n_max, clusters_size[i]) for i in range(n_clusters)]
            print(colors)
            #colors = [generate_color_gradient(n_max, len(clusters[i])) for i in range(len(clusters))]
            cluster_shapes = [dl.Polygon(children = dl.Tooltip('Number of workers: '+str(clusters_size[i])), positions=clusters[i], fill=True, fillColor = colors[i], fillOpacity=0.9) for i in range(n_clusters)]
            newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + cluster_shapes + IndPark_marker,
                            center=center, zoom=12, id="map_1",
                            style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})

        else:
            newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + IndPark_marker,
                            center=center, zoom=12, id="map_1",
                            style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})

        return [newMap]


    @app.callback([Output('sidebar_intervention_1','children',allow_duplicate=True)],
                State('internal-value_stops_1','data'),
                State('internal-value_coworking_1','data'),
                State('internal-value_coworking_days_1','data'),        
                State('internal-value_remote_days_1', 'data'),
                State('internal-value_remote_workers_1', 'data'),

                State('internal-value_eCar_adoption_1', 'data'),
                State('internal-value_eCar_co2_km_1', 'data'),
                
                State('internal-value_bus_number_1', 'data'),
                State('internal-value_routes_1', 'data'),
                State('internal-value_trip_number_1', 'data'),
                State('internal-value_trip_freq_1', 'data'),
                State('internal-value_start_hour_1', 'data'),
                State('internal-value_scenario_1','data'),
                State('internal-value_calculated_scenarios_1', 'data'),
                Input('choose_intervention_1',"value"),
                prevent_initial_call=True
                )
    def choose_intervention(St,Cow,CowDays, RemDays, RemWorkers, NeCar, eCar_co2_km, Nbuses, RoutesCoords, Ntrips, TripFreq, StartHour, current_scenario, stored_scenarios, interv):
        print('chosen interv.: ', interv)
            
        if interv == 'CT':
            sidebar_transport = html.Div(
                [           
                dbc.Button("Propose stops", id="propose_stops_1", n_clicks=0,style={"margin-top": "15px","font-weight": "bold"}),
                #dbc.Popover(dcc.Markdown(mouse_over_mess_stops, dangerously_allow_html=True),
                #          target="propose_stops_1",
                #          body=True,
                #          trigger="hover",style = {'font-size': 12, 'line-height':'2px'}),

                dbc.Button("Match stops", id="match_stops_1", n_clicks=0, style={"margin-left": "15px", "margin-top": "15px", "font-weight": "bold"}),
                #dbc.Popover(dcc.Markdown(mouse_over_mess, dangerously_allow_html=True),
                #          target="match_stops_1",
                #          body=True,
                #          trigger="hover",style = {'font-size': 12, 'line-height':'2px'}),                      
                html.P(['Modify stops'],id='action_select_bus_stops_1',style={"margin-top": "15px", "font-weight": "bold"}),
                dcc.Dropdown(stops_actions, multi=False,style={"margin-top": "15px"}, id='choose_stop_action_1'),                       

                html.P(['Choose number of routes'],id='choose_bus_num_1',style={"margin-top": "15px","font-weight": "bold"}),
                dcc.Slider(0, 10, 1,
                    value=Nbuses,
                    id='num_buses_1'
                ),

                dbc.ButtonGroup(
                                [
                                dbc.Button("Calculate routes", id="calc_routes_1", n_clicks=0, style={"margin-top": "15px"}),
                                dbc.Button("Visualize routes", id="visualize_routes_1", n_clicks=0, style={"margin-top": "15px"}),
                                ],
                                vertical=True,
                                style={"margin-top": "15px"}
                ),              
                html.Div(id='outdata_1', style={"margin-top": "15px"}),
                dcc.Store(id='internal-value_stops_1', data=St),
                dcc.Store(id='internal-value_coworking_1', data=Cow),
                dcc.Store(id='internal-value_coworking_days_1', data=CowDays),
                dcc.Store(id='internal-value_remote_days_1', data=RemDays),
                dcc.Store(id='internal-value_remote_workers_1', data=RemWorkers),


                dcc.Store(id='internal-value_eCar_adoption_1', data=NeCar),
                dcc.Store(id='internal-value_eCar_co2_km_1', data=eCar_co2_km),

                dcc.Store(id='internal-value_bus_number_1', data=Nbuses),
                dcc.Store(id='internal-value_trip_freq_1', data=TripFreq),
                dcc.Store(id='internal-value_trip_number_1', data=Ntrips),
                dcc.Store(id='internal-value_start_hour_1', data=StartHour),
                dcc.Store(id='internal-value_routes_1', data=RoutesCoords),        
                dcc.Store(id='internal-value_scenario_1', data=current_scenario),        
                dcc.Store(id='internal-value_calculated_scenarios_1', data=stored_scenarios)
                ])      
            return [sidebar_transport]

        if interv == 'RW':         
            
            sidebar_remote_work = html.Div(
                    [
                    #html.P([ html.Br(),'Choose number of days of remote working'],id='remote_days_num_1',style={"margin-top": "15px","font-weight": "bold"}),
                    html.P(['Choose number of days of remote working'],id='remote_days_num_1',style={"margin-top": "15px","font-weight": "bold"}),

                    #dcc.Input(id="choose_buses", type="text", value='3'),
                    dcc.Slider(0, 5, 1,
                        value=RemDays,
                        id='choose_remote_days_1'
                    ),
                    #html.P([ html.Br(),'Choose "%" of remote workers'],id='remote_workers_num_1',style={"margin-top": "15px","font-weight": "bold"}),
                    html.P(['Choose "%" of remote workers'],id='remote_workers_num_1',style={"margin-top": "15px","font-weight": "bold"}),

                    #dcc.Input(id="choose_buses", type="text", value='3'),
                    dcc.Slider(0, 100, 5,
                        value=RemWorkers,
                        id='choose_remote_workers_1',
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": True}                       
                    ),
                    #html.Br(),               
                    html.Div(id='outdata_1', style={"margin-top": "15px"}),
                    dcc.Store(id='internal-value_stops_1', data=St),
                    dcc.Store(id='internal-value_coworking_1', data=Cow),
                    dcc.Store(id='internal-value_coworking_days_1', data=CowDays),
                    dcc.Store(id='internal-value_remote_days_1', data=RemDays),
                    dcc.Store(id='internal-value_remote_workers_1', data=RemWorkers),


                    dcc.Store(id='internal-value_eCar_adoption_1', data=NeCar),
                    dcc.Store(id='internal-value_eCar_co2_km_1', data=eCar_co2_km),

                    dcc.Store(id='internal-value_bus_number_1', data=Nbuses),
                    dcc.Store(id='internal-value_trip_freq_1', data=TripFreq),
                    dcc.Store(id='internal-value_trip_number_1', data=Ntrips),
                    dcc.Store(id='internal-value_start_hour_1', data=StartHour),
                    dcc.Store(id='internal-value_routes_1', data=RoutesCoords),        
                    dcc.Store(id='internal-value_scenario_1', data=current_scenario),        
                    dcc.Store(id='internal-value_calculated_scenarios_1', data=stored_scenarios)
                    ])        
            return [sidebar_remote_work]

        if interv == 'ECa':        

            print()
            print('inside ECa')
            print('Percentage of electric cars: ')
            print(NeCar)
            print('Electric car co2: ')
            print(eCar_co2_km)
            sidebar_electric_car = html.Div(
                    [
                    html.P(['Choose car electrifcation %'],id='ecar_adoption_1',style={"margin-top": "15px","font-weight": "bold"}),

                    dcc.Slider(0, 100, 5,
                        value=NeCar,
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": True},
                        id='choose_eCar_adoption_1'
                    ),
                    html.P(['Electric car CO2 emissions (WRT combustion car)'],id='ecar_CO2_1',style={"margin-top": "15px","font-weight": "bold"}),
                    dcc.Slider(0, 1 ,0.1,
                        value=eCar_co2_km,
                        id='choose_eCar_co2_km_1',
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),  
                    html.Div(id='outdata_1', style={"margin-top": "15px"}),
                    dcc.Store(id='internal-value_stops_1', data=St),
                    dcc.Store(id='internal-value_coworking_1', data=Cow),
                    dcc.Store(id='internal-value_coworking_days_1', data=CowDays),
                    dcc.Store(id='internal-value_remote_days_1', data=RemDays),
                    dcc.Store(id='internal-value_remote_workers_1', data=RemWorkers),

                    dcc.Store(id='internal-value_eCar_adoption_1', data=NeCar),
                    dcc.Store(id='internal-value_eCar_co2_km_1', data=eCar_co2_km),

                    dcc.Store(id='internal-value_bus_number_1', data=Nbuses),
                    dcc.Store(id='internal-value_trip_freq_1', data=TripFreq),
                    dcc.Store(id='internal-value_trip_number_1', data=Ntrips),
                    dcc.Store(id='internal-value_start_hour_1', data=StartHour),
                    dcc.Store(id='internal-value_routes_1', data=RoutesCoords),        
                    dcc.Store(id='internal-value_scenario_1', data=current_scenario),        
                    dcc.Store(id='internal-value_calculated_scenarios_1', data=stored_scenarios)
                    ])        
            return [sidebar_electric_car]


        if interv == 'CW':         
            
            sidebar_cowork = html.Div(
                    [
                    html.P(['Modify coworking hubs'],id='action_select_cow_1',style={"margin-top": "15px", "font-weight": "bold"}),
                    dcc.Dropdown(cow_actions, multi=False,style={"margin-top": "15px"}, id='choose_coworking_action_1'),                       

                    #html.P([ html.Br(),'Choose number of days of coworking'],id='coworking_days_num_1',style={"margin-top": "15px","font-weight": "bold"}),
                    html.P(['Choose number of days of coworking'],id='coworking_days_num_1',style={"margin-top": "15px","font-weight": "bold"}),
                    #dcc.Input(id="choose_buses", type="text", value='3'),
                    dcc.Slider(0, 5, 1,
                            value=CowDays,
                            id='choose_coworking_days_1'
                    ),
                    #html.Br(),               
                    html.Div(id='outdata_1', style={"margin-top": "15px"}),
                    dcc.Store(id='internal-value_stops_1', data=St),
                    dcc.Store(id='internal-value_coworking_1', data=Cow),
                    dcc.Store(id='internal-value_coworking_days_1', data=CowDays),
                    dcc.Store(id='internal-value_remote_days_1', data=RemDays),
                    dcc.Store(id='internal-value_remote_workers_1', data=RemWorkers),

                    dcc.Store(id='internal-value_eCar_adoption_1', data=NeCar),
                    dcc.Store(id='internal-value_eCar_co2_km_1', data=eCar_co2_km),

                    dcc.Store(id='internal-value_bus_number_1', data=Nbuses),
                    dcc.Store(id='internal-value_trip_freq_1', data=TripFreq),
                    dcc.Store(id='internal-value_trip_number_1', data=Ntrips),
                    dcc.Store(id='internal-value_start_hour_1', data=StartHour),
                    dcc.Store(id='internal-value_routes_1', data=RoutesCoords),        
                    dcc.Store(id='internal-value_scenario_1', data=current_scenario),        
                    dcc.Store(id='internal-value_calculated_scenarios_1', data=stored_scenarios)
                    ])   
            return [sidebar_cowork]


    #               State('num_trips_1', 'value'),
    #               State('trip_freq_1', 'value'),
    #               Output("choose_route_1", "options",allow_duplicate=True),

    """
    @app.long_callback([
                Output("outdata_1", "children",allow_duplicate=True),
                Output("internal-value_route_opt_done_1", 'data',allow_duplicate=True),
                Output('internal-value_routes_1','data',allow_duplicate=True),
                Output('internal-value_bus_number_1','data',allow_duplicate=True),
                Output('map_1','children',allow_duplicate=True)],
                State('num_buses_1', 'value'), 
                State('choose_start_time_1', 'value'),  
                State('internal-value_stops_1','data'),
                State('internal-value_coworking_1','data'),
                State('internal-value_co2_km_car_1','data'),
                State('root_dir_1','data'),
                Input("calc_routes_1", "n_clicks"),
                manager=long_callback_manager,
                prevent_initial_call=True
                )
    """

    @app.long_callback([
                Output("outdata_1", "children",allow_duplicate=True),
                Output("internal-value_route_opt_done_1", 'data',allow_duplicate=True),
                Output('internal-value_routes_1','data',allow_duplicate=True),
                Output('internal-value_routes_len_1','data',allow_duplicate=True),
                Output('map_1','children',allow_duplicate=True)],
                State('internal-value_bus_number_1','data'), 
                State('choose_start_time_1', 'value'),  
                State('internal-value_stops_1','data'),
                State('internal-value_coworking_1','data'),
                State('internal-value_ind_park_coord_1','data'),
                State('internal-value_co2_km_car_1','data'),
                State('root_dir_1','data'),
                Input("calc_routes_1", "n_clicks"),
                manager=long_callback_manager,
                prevent_initial_call=True
                )
    def calc_routes(Nroutes,StartHour,St,Cow,IndParkCoord, CO2km, root_dir, Nclick):
        Ntrips = 1 # default
        freq = 30 # default
        if Nclick > 0:
            #root_dir = root_Dir
            sys.path.append(root_dir + 'components')
            print()
            print('Cleaning folders...')
            shutil.rmtree(root_dir + 'assets/data/input_data_MCM/GTFS_feeds')
            shutil.rmtree(root_dir + 'assets/data/input_data_MCM/transit_together_24h')
            shutil.copytree(root_dir + 'assets/data/input_data_MCM/GTFS_feeds_backup', root_dir + 'assets/data/input_data_MCM/GTFS_feeds')
            shutil.copytree(root_dir + 'assets/data/input_data_MCM/transit_together_24h_backup', root_dir + 'assets/data/input_data_MCM/transit_together_24h')
            print('done!')
            print()


        import calcroutes_module
        import dash_leaflet as dl
        import generate_GTFS_module as gGTFS
        custom_icon_bus = dict(
        iconUrl= "https://i.ibb.co/HV0K5Fp/bus-stop.png",
        iconSize=[40,40],
        iconAnchor=[22, 40]
        )

        custom_icon_coworking = dict(
        iconUrl= "https://i.ibb.co/J2qXGKN/coworking-icon.png",
        iconSize=[40,40],
        iconAnchor=[22, 40]
        )    
        
        IndPark_marker = [dl.Marker(dl.Tooltip("Industrial Park"), position=IndParkCoord, icon=custom_icon_IndPark, id='IndPark_1')]

        #center = (43.26852347667122, -1.9741372404905988)
        center = IndParkCoord
        # Set origin of bus routes to Eskuzaitzeta #######################################
        #origin_bus_routes = (43.257414680347246, -2.027512109345033)        
        origin_bus_routes = IndParkCoord        
        St.insert(0, origin_bus_routes)
        Cow.insert(0, 0)
        ###################################################################################
        
        #list_routes = range(1,int(Nroutes)+1)    
        list_routes = range(int(Nroutes))
        new_menu = [{'label': 'Route ' +str(i+1), 'value': i} for i in list_routes]
        Stops = []
        markers = []
        print('Discriminating bus stops from coworking hubs...')
        for i, pos in enumerate(St): 
            if Cow[i]==1:
                custom_icon = custom_icon_coworking
            else:
                custom_icon = custom_icon_bus
                Stops.append(pos)
            tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
            markers.append(tmp)  

        print('List of Stops generated')        
        print('\n')
        print('\n')
        print('Start calculating routes...')
        routes, routes_points_coords, Graph, route_lengths = calcroutes_module.CalcRoutes_module(Stops,int(Nroutes),root_dir,float(CO2km))
        print('Routes calculated!')
        #print(routes_points_coords)
        print('')
        print('root dir: ', root_dir)
        print('Ntrips: ', Ntrips)
        print('freq: ', freq)
        print('StartHour: ', StartHour)
        #StartHour = int(StartHour)
        #StartHour = "{:02d}".format(StartHour) + ':00'
        gGTFS.gGTFS(routes, Stops, Graph, root_dir, Ntrips, freq, StartHour)
        route_opt = 1
        # We don't really need to update the map here. We do it just to make the Spinner work: ############ 
        #markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(Stops)]
        newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers + IndPark_marker,
                        center=center, zoom=12, id="map_1",
                        style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"}) 
        ###################################################################################################   
        #return ["Calculation completed for: "+str(len(Stops)), route_opt, routes_points_coords, Nroutes, new_menu, newMap]
        return ["Calculation completed for: "+str(len(Stops)) +' stops', route_opt, routes_points_coords, route_lengths,newMap]


    #              [State('choose_route_1',"value"),
    @app.callback([Output('map_1','children',allow_duplicate=True)],
                [State('internal-value_stops_1','data'),
                State('internal-value_coworking_1','data'),
                State('internal-value_ind_park_coord_1','data'),
                State('internal-value_routes_1','data'),
                State('internal-value_scenario_1','data')],
                [Input("visualize_routes_1", "n_clicks")],
                prevent_initial_call=True
                )
    #def visualize_route(Route,St,Cow,RoutesCoords,Nclick):
    def visualize_route(St,Cow,IndParkCoord, RoutesCoords,result_json,Nclick):
        if Nclick > 0:
            print()
            print('Start route visualization...')
            markers = []
            for i, pos in enumerate(St): 
                if Cow[i]==1:
                    custom_icon = custom_icon_coworking
                else:
                    custom_icon = custom_icon_bus
                tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
                markers.append(tmp)  

            IndPark_marker = [dl.Marker(dl.Tooltip("Industrial Park"), position=IndParkCoord, icon=custom_icon_IndPark, id='IndPark_1')]

            map_routes = []
            colors = mf.generate_colors(len(RoutesCoords))
            for i in range(len(RoutesCoords)):
                map_routes.append(dl.Polyline(positions=[RoutesCoords[i]], pathOptions={'weight':10, 'color': colors[i]}))         

            if len(result_json) ==0:
                    newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + map_routes + markers + IndPark_marker,
                                center=center, zoom=12, id="map_1",
                                style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
            else:
                    result = pd.DataFrame.from_dict(result_json) 
                    result = geopandas.GeoDataFrame(
                            result, geometry=geopandas.points_from_xy(result.O_long, result.O_lat), crs="EPSG:4326"
                            )
                    newMap = mf.generate_map(result, Cow, St, map_routes + markers + IndPark_marker)


            print('Route visualization completed!')
            return [newMap]


    @app.callback([ 
                Output('internal-value_stops_1','data',allow_duplicate=True),
                Output('map_1','children',allow_duplicate=True)],
                [State('internal-value_stops_1','data'),
                State('internal-value_coworking_1','data'),
                State('internal-value_ind_park_coord_1','data'),
                State('internal-value_scenario_1','data')],
                Input("match_stops_1", "n_clicks"),
                prevent_initial_call=True
                )
    def match_stops(St,Cow,IndParkCoord, result_json,Nclick):
        if Nclick > 0:
            bus_stops = []
            out = ''
            for i_st in range(len(St)):
                if Cow[i_st] == 0:  
                    ref = np.array([St[i_st][0],St[i_st][1]])
                    ref = np.tile(ref,(len(stops_lat_lon),1)) # generate replicas of ref point
                    #d = [sum((p-q)**2)**0.5 for p, q in zip(ref, stops_lat_lon)] # calculate distance of each bus stop to ref point
                    d = [geopy.distance.geodesic((p[0],p[1]), (q[0],q[1])).km for p, q in zip(ref, stops_lat_lon)] # calculate distance of each bus stop to ref point

                    ind_min = d.index(min(d)) # find index of closest bus stop  
                    x = stops_lat_lon[ind_min][0]
                    y = stops_lat_lon[ind_min][1]
                    bus_stops.append((x, y))
                    St[i_st]=(x,y)
                    out = out + str(St[i_st][0]) + ', ' + str(St[i_st][1]) + '; '
            markers = []
            for i, pos in enumerate(St): 
                if Cow[i] == 1:
                    custom_icon = custom_icon_coworking
                    #print('setting coworking icon...')
                else:
                    custom_icon = custom_icon_bus
                tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
                markers.append(tmp)
            #markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]

            IndPark_marker = [dl.Marker(dl.Tooltip("Industrial Park"), position=IndParkCoord, icon=custom_icon_IndPark, id='IndPark_1')]

            if len(result_json) ==0:
                    newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers + IndPark_marker,
                                center=center, zoom=12, id="map_1",
                                style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
            else:
                    result = pd.DataFrame.from_dict(result_json) 
                    result = geopandas.GeoDataFrame(
                            result, geometry=geopandas.points_from_xy(result.O_long, result.O_lat), crs="EPSG:4326"
                            )
                    newMap = mf.generate_map(result, Cow, St, markers + IndPark_marker)      
            
            return [St,newMap]

    # Save marker option in internal value #####################################

    @app.callback(
        [
        Output('internal-value_marker_option_1', 'data', allow_duplicate=True)
        ],
        [Input('choose_stop_action_1', 'value')],
        prevent_initial_call=True
    )
    def set_stop(selection):
        print('checking selection...: ', selection)
        return [selection]


    @app.callback(
        [
        Output('internal-value_marker_option_1', 'data', allow_duplicate=True)
        ],
        [Input('choose_coworking_action_1', 'value')],
        prevent_initial_call=True
    )
    def set_coworking(selection):
        print('checking selection..: ', selection)
        return [selection]
    ################################################################################


    @app.callback(
        [
            Output('internal-value_stops_1', 'data', allow_duplicate=True),
            Output('internal-value_coworking_1', 'data', allow_duplicate=True),
            Output('internal-value_ind_park_coord_1','data',allow_duplicate=True),
            Output('map_1', 'children', allow_duplicate=True)
        ],
        [
            State('internal-value_stops_1', 'data'),
            State('internal-value_coworking_1', 'data'),
            State('internal-value_marker_option_1', 'data'),        
            State('set_ind_park_1','value'),
            State('internal-value_ind_park_coord_1','data'),
            State('internal-value_scenario_1','data')        
        ],
        [Input('map_1', 'dblclickData')],
        prevent_initial_call=True
    )
    def add_marker(St, Cow, MarkerOption, set_park, IndParkCoord, result_json, clickd):

        if MarkerOption == 'AS' or MarkerOption == 'AC':
            result = pd.DataFrame.from_dict(result_json) 
            result = geopandas.GeoDataFrame(
                    result, geometry=geopandas.points_from_xy(result.O_long, result.O_lat), crs="EPSG:4326"
                    )    
            print('adding marker...')
            print(clickd)
            print('Selected action:')
            print(MarkerOption)
            marker_lat = clickd['latlng']['lat']
            marker_lon = clickd['latlng']['lng']
            St.append((marker_lat, marker_lon))
            if MarkerOption == 'AS':
                Cow.append(0)
            if MarkerOption == 'AC':
                Cow.append(1)

            out = '' # -> not needed anymore
            for i in range(len(St)):
                out = out + str(St[i][0]) + ', ' + str(St[i][1]) + '; '

            markers = []
            for i, pos in enumerate(St):
                if Cow[i] == 1:
                    custom_icon = custom_icon_coworking
                else:
                    custom_icon = custom_icon_bus
                tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})
                markers.append(tmp)

            #newMap = dl.Map([dl.TileLayer(), dl.ScaleControl(position="topright")] + markers,
            #                center=center, zoom=12, id="map_1",
            #                style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})

            newMap = mf.generate_map(result, Cow, St, markers) 
            return [St, Cow, IndParkCoord, newMap]
        if set_park:
            if set_park[0]==1:
                print('start modifying map...')
                marker_lat = clickd['latlng']['lat']
                marker_lon = clickd['latlng']['lng']
                #St.append((marker_lat, marker_lon))
                #Cow.append(0)

                out = '' # -> not needed anymore
                for i in range(len(St)):
                    out = out + str(St[i][0]) + ', ' + str(St[i][1]) + '; '

                markers = []
                for i, pos in enumerate(St):
                    if Cow[i] == 1:
                        custom_icon = custom_icon_coworking
                    else:
                        custom_icon = custom_icon_bus
                    tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})
                    markers.append(tmp)

                print('creating new marker...')
                IndParkCoord = (marker_lat,marker_lon)
                IndPark_marker = [dl.Marker(dl.Tooltip("Industrial Park"), position=IndParkCoord, icon=custom_icon_IndPark, id='IndPark_1')]
                print('new marker created')

                print('generating new map...')
                if len(result_json) ==0:
                    newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers + IndPark_marker,
                                center=center, zoom=12, id="map_1",
                                style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
                else:
                    result = pd.DataFrame.from_dict(result_json) 
                    result = geopandas.GeoDataFrame(
                            result, geometry=geopandas.points_from_xy(result.O_long, result.O_lat), crs="EPSG:4326"
                            )
                    newMap = mf.generate_map(result, Cow, St, markers + IndPark_marker)        
                print('new map generated!')
                return [St, Cow, [marker_lat, marker_lon], newMap]


    #               Output('internal-value_marker_option_1', 'data',allow_duplicate=True),
    @app.callback([Output("outdata_1", "children",allow_duplicate=True),
                Output('internal-value_stops_1','data',allow_duplicate=True),
                Output('internal-value_coworking_1','data',allow_duplicate=True),
                Output('internal-value_marker_option_1', 'data',allow_duplicate=True),
                Output('map_1','children',allow_duplicate=True)],
                [State('internal-value_stops_1','data'), 
                State('internal-value_coworking_1','data'), 
                State('internal-value_ind_park_coord_1','data'), 
                State('internal-value_marker_option_1', 'data'),
                State('internal-value_scenario_1','data')],
                [Input({"type": "marker", "index": ALL},"n_clicks")],
                prevent_initial_call=True)
    def change_stop_marker(St, Cow, IndParkCoord, marker_operation, result_json, *args):
        marker_id = callback_context.triggered[0]["prop_id"].split(".")[0].split(":")[1].split(",")[0]
        n_clicks = callback_context.triggered[0]["value"]
        result = pd.DataFrame.from_dict(result_json) 
        result = geopandas.GeoDataFrame(
                    result, geometry=geopandas.points_from_xy(result.O_long, result.O_lat), crs="EPSG:4326"
                    )

        print('changing marker...')
        print('requested Marker Operation:')
        print(marker_operation)
        
        if marker_operation == "DS" or marker_operation == "DC": 
            print()   
            print('deleting stop...')
            print()  
            del St[int(marker_id)]
            del Cow[int(marker_id)]
        
            markers = []
            for i, pos in enumerate(St): 
                if Cow[i]==1:
                    custom_icon = custom_icon_coworking
                else:
                    custom_icon = custom_icon_bus
                tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
                markers.append(tmp)    
            #newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
            #                center=center, zoom=12, id="map_1",
            #                style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
            IndPark_marker = [dl.Marker(dl.Tooltip("Industrial Park"), position=IndParkCoord, icon=custom_icon_IndPark, id='IndPark_1')]

            newMap = mf.generate_map(result, Cow, St, markers + IndPark_marker)

            return ['Marker deleted!',St,Cow,'',newMap]

