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


import sys
import os
from os import listdir
import shutil


#root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
#root_dir = '/home/cslgipuzkoa/virtual_machine_disk/UI_SCP/assets/'
root_dir = 'C:/Users/gfotidellaf/repositories/test_UI_SCP/app/'

sys.path.append(root_dir + 'layout')

im1 = root_dir +'assets/images/CSL_logo.jpg'

stops_file = root_dir +'assets/data/all_bus_stops.csv'


from PIL import Image
image1 = Image.open(im1)

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

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 60,
    "left": 0,
    "bottom": 0,
    "width": "25rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow": "scroll"           # scrollbar
}

"""
"padding": "2rem 1rem",
"background-color": "#f8f9fa",
"""
# the styles for the main content position it to the right of the sidebar and
# add some padding.

CONTENT_STYLE = {
    "margin-left": "5rem",
    "margin-right": "15rem",
}

CONTENT_STYLE_2 = {
    "margin-left": "0rem",
    "margin-right": "10rem",
}


INDICATORS_STYLE = {
    "background-color": "#f8f9fa",
    "position": "fixed",
    "top": 60,
    "right": 40,
    "bottom": 0,
    "width": "40rem",
    "overflow": "scroll"    
}

INDICATORS_STYLE_2 = {
    "background-color": "#f8f9fa",
    "position": "fixed",
    "top": 60,
    "left": 30,
    "bottom": 0,
    "width": "150rem",
    "overflow": "scroll"    
}


mouse_over_mess = """
Shifts stops to closest
<p>existing bus stops</p>"""

mouse_over_mess_stops = """
Proposes bus stops based on
<p>workers Lats/Lons in CSV file</p>
<p>and the number of clusters</p>"""

mouse_over_mess_clusters = """
Clusters by which to group workers"""

mouse_over_mess_depot = """
Uncheck box for removing bus stops!"""

routes = [{'label': 'Route ' +str(i+1), 'value': i} for i in range(3)]

#                 {'label': 'Set origin of bus routes', 'value': 'SO'} 
stops_actions = [
                 {'label': 'Add bus stop', 'value': 'AS'},    
                 {'label': 'Delete bus stop', 'value': 'DS'},                   
                ]
cow_actions = [{'label': 'Add coworking hub', 'value': 'AC'},
               {'label': 'Delete coworking hub', 'value': 'DC'}                   
            ]

interventions = [{'label': 'Company transportation', 'value': 'CT'},
                 {'label': 'Remote working', 'value': 'RW'},
                 {'label': 'Coworking', 'value': 'CW'},
                 {'label': 'Car electrification', 'value': 'ECa'}                
                ]

choose_transp_hour = [{'label': "{:02d}".format(i) + ':00' + '-' + "{:02d}".format(i+1) + ':00', 'value': i} for i in range(24)] 
#choose_start_hour = [{'label': "{:02d}".format(i) + ':00',  'value': i} for i in range(24)] 
choose_start_hour = [{'label': hour, 'value': hour} for hour in ['All hours','00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00', '09:00', '10:00', '11:00']]

Step_1_text="Step 1:\nLoad and visualize raw data "
Step_2_text="Step 2:\nRun baseline scenario "
Step_3_text="Step 3:\nSelect type of intervention "
#Step_4_text="Step 4:\nSelect time for commuting "

collapse_button_1 = html.Div([

            dbc.Button(
                        [html.I(className="fas fa-plus-circle")],
                        id="Load_data_button_1",
                        className="mb-3",
                        color="primary",
                        n_clicks=0,
                        style={
                                "cursor": "pointer",
                                "display": "inline-block",
                                "white-space": "pre",
                        },
                ),
])

collapse_button_2 = html.Div([

        dbc.Button(
            [html.I(className="fas fa-plus-circle")],
            id="Run_baseline_button_1",
            className="mb-3",
            color="primary",
            n_clicks=0,
            style={
                    "cursor": "pointer",
                    "display": "inline-block",
                    "white-space": "pre",
                    },
        ),
])

collapse_button_3 = html.Div([

        dbc.Button(
            [html.I(className="fas fa-plus-circle")],
            id="Intervention_type_button_1",
            className="mb-3",
            color="primary",
            n_clicks=0,
            style={
                    "cursor": "pointer",
                    "display": "inline-block",
                    "white-space": "pre",
                    },
        ),
])

collapse_button_4 = html.Div([
        dbc.Button(
            [html.I(className="fas fa-plus-circle")],
            id="Select_time_button_1",
            className="mb-3",
            color="primary",
            n_clicks=0,
            style={
                    "cursor": "pointer",
                    "display": "inline-block",
                    "white-space": "pre",
                    },
        ),
])


collapse_button_5 = html.Div([
        dbc.Button(
            [html.I(className="fas fa-plus-circle")],
            id="Advanced_settings_button_1",
            className="mb-3",
            color="primary",
            n_clicks=0,
            style={
                    "cursor": "pointer",
                    "display": "inline-block",
                    "white-space": "pre",
                    },
        ),
])

sidebar_1 =  html.Div(
       [
                 
        dbc.Row([
            dbc.Col([
                    html.P([Step_1_text],style={"font-weight": "bold","white-space": "pre"})
                    ],
                    #style={'height': '80px'},width=8),
                    md=8),                    
            dbc.Col([        
                        collapse_button_1,
                    ],
                    #style={'height': '80px'},width=3),
                    md=3),                                                      
        ]),
        dbc.Row([
                dbc.Collapse([
                        dbc.Checklist(
                                options=[
                                        {"label": "Choose position of Industrial Park", "value": 1},
                                        ],
                                value=[],
                                id="set_ind_park_1",
                                switch=True
                                    ),
                        dcc.Upload(
                                id='upload-data_1',
                                children=html.Div([
                                html.A('Import Files')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px',
                                "margin-top": "15px"
                            },
                            # Allow multiple files to be uploaded
                            multiple=True),
                            html.P(['Choose time'],style={"font-weight": "bold","white-space": "pre"}),
                            #html.Div(dcc.Dropdown(choose_start_hour, multi=False, id='choose_start_time_1')),
                            dcc.Dropdown(options=choose_start_hour, value='08:00', multi=False, id='choose_start_time_1'),        
                            #html.Br(),        
                            #html.P([html.Br(),'Choose number of clusters'],id='cluster_num_1',style={"margin-top": "15px","font-weight": "bold"}),        
                            html.P([ 'Choose number of clusters'],id='cluster_num_1',style={"margin-top": "15px","font-weight": "bold"}),        
                            dbc.Popover(
                                dbc.PopoverBody(mouse_over_mess_clusters), 
                                target="n_clusters_1",
                                body=True,
                                trigger="hover",style = {'font-size': 12, 'line-height':'2px'},
                                placement= 'right',
                                is_open=False),
                            #dcc.Input(id="n_clusters", type="text", value='19'),
                            dcc.Slider(1, 30, 1,
                            value=10,
                            id='n_clusters_1',
                            marks=None,
                            tooltip={"placement": "bottom", "always_visible": True}
                            ),
                            #html.Br(),   
                            dbc.Button("Visualize clusters of workers", id="show_workers_1", n_clicks=0,style={"margin-top": "15px","font-weight": "bold"}),                            

                            html.Div([
                                dbc.Button("Download data template", id="button_download_template_1", n_clicks=0,style={"margin-top": "15px","font-weight": "bold"}),               
                                Download(id="download_template_1"),
                                ])
                            ],
                            id="Load_data_panel_1",
                            is_open=False,
                    )
        ]),

        dbc.Row([
            dbc.Col([
                        html.P([Step_2_text],style={"font-weight": "bold","white-space": "pre"}),
                    ],
                    #style={'height': '80px'},width=8),
                    md=8),
            dbc.Col([        
                        collapse_button_2,
                    ],
                    #style={'height': '80px'},width=3
                    md=3
                    )                    
        ]),
        dbc.Row([
            dbc.Collapse([ 
            dbc.Button('Run', 
                            id="run_baseline_1",
                            className="mb-3",
                            size="lg",
                            n_clicks=0,
                            disabled=False)         
            ],
           id="Run_baseline_panel_1",
           is_open=False,
           )
        ]),



        dbc.Row([
            dbc.Col([
                        html.P([Step_3_text],style={"font-weight": "bold","white-space": "pre"}),
                    ],
                    #style={'height': '80px'},width=8),
                    md=8),
            dbc.Col([        
                        collapse_button_3,
                    ],
                    #style={'height': '80px'},width=3
                    md=3
                    )                    
        ]),
        dbc.Row([
            dbc.Collapse([
            dcc.Dropdown(interventions, multi=False,style={"margin-top": "15px"}, id='choose_intervention_1'),
            #html.P([ html.Br(),'Select action for markers'],id='action_select_1',style={"margin-top": "15px", "font-weight": "bold"}),
            html.Div(id='sidebar_intervention_1', style={"margin-top": "15px"})
            ],
           id="Intervention_type_panel_1",
           is_open=False,
           )
        ]),


        #dbc.Row([
        #    dbc.Col([
        #                html.P([Step_4_text],style={"font-weight": "bold","white-space": "pre"}),
        #            ],
        #            #style={'height': '80px'},width=8),
        #            md=8),
        #    dbc.Col([        
        #                collapse_button_4,
        #            ],
        #            #style={'height': '80px'},width=3
        #            md=3
        #            )                    
        #]),
        #dbc.Row([
        #        dbc.Collapse([
        #            html.P(['Choose time range'],style={"font-weight": "bold","white-space": "pre"}),
        #            html.Div(dcc.Dropdown(choose_transp_hour, multi=False, id='choose_transp_hour_1'))            
        #            ],
        #            id='Select_time_panel_1',
        #            is_open=False,
        #        ),
        #]),
        dbc.Row([
            dbc.Col([
                        html.P(['Advanced_settings'],style={"font-weight": "bold","white-space": "pre"}),
                    ],
                    #style={'height': '80px'},width=8),
                    md=8),
            dbc.Col([        
                        collapse_button_5,
                    ],
                    #style={'height': '80px'},width=3
                    md=3
                    )                    
        ]),
        #html.Br(),
        dbc.Row([
            dbc.Collapse([
                #html.P([ html.Br(),'Liters of gasoline per kilometer (car)'],id='gas_km_car_1',style={"margin-top": "15px","font-weight": "bold"}),
                html.P(['CO2 kg/km (combustion car)'],id='co2_km_car_1',style={"margin-top": "15px","font-weight": "bold"}),
                dcc.Slider(0, 1.0,0.01,
                    value=0.19,
                    id='choose_co2_km_car_1',
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),                 
                #html.P([ html.Br(),'Liters of gasoline per kilometer (bus)'],id='gas_km_bus_1',style={"margin-top": "15px","font-weight": "bold"}),
                html.P(['CO2 kg/km (bus)'],id='co2_km_bus_1',style={"margin-top": "15px","font-weight": "bold"}),
                dcc.Slider(0, 2,0.1,
                    value=1.46,
                    id='choose_co2_km_bus_1',
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),                    
                #html.P([ html.Br(),'CO2 Kg per lt'],id='CO2_lt_1',style={"margin-top": "15px","font-weight": "bold"}),
                html.P(['CO2 kg/km/person (train)'],id='co2_km_train_1',style={"margin-top": "15px","font-weight": "bold"}),
                dcc.Slider(0, 0.5,0.01,
                    value=0.019,
                    id='choose_co2_km_train_1',
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": True}
                ), 

                html.P(['Relative Bus/Train usage'],id='bus_train_ratio_1',style={"margin-top": "15px","font-weight": "bold"}),
                dcc.Slider(0, 100,10,
                    value=80,
                    id='choose_bus_train_ratio_1',
                    marks= {0: "100% Train", 100: "100% Bus"},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),            
                ],
                id="Advanced_settings_panel_1",
                is_open=False,
                ),
        ]),
        
        html.Div(dbc.Button('Run', 
                            id="run_MCM_1",
                            className="mb-3",
                            size="lg",
                            n_clicks=0,
                            disabled=False, 
                            color='warning'),
                            style={"margin-top": "15px","white-space": "pre"}),
              
        #dbc.Row(
        #            html.Div(
        #                      dcc.Upload(id='button_load_scenario_1',
        #                                 children=html.Div([
        #                                 dbc.Button('Load scenario')
        #                                ]),
        #                                # Allow multiple files to be uploaded
        #                                multiple=True
        #                                )
        #            ),
        #            style={"margin-top": "15px"},
        #            #width='auto'
        #        ),

        dbc.Row(
                    html.Div([
                            dbc.Button("Download scenario", id='button_download_scenario_1', n_clicks=0),
                            Download(id="download_scenario_1"),
                            Download(id="download_inputs_1"),
                            Download(id="download_StopsCowHubs_1")
                            ]),
                            style={"margin-top": "15px"},
                            #width="auto"
              ),  

        html.Div(id='outdata_1', style={"margin-top": "15px"}), 
        dcc.Location(id='url'), 
        dcc.Store(id='user_ip', data=0),         
        dcc.Store(id='worker_data_1', data=[]),
        dcc.Store(id='root_dir_1', data = root_dir), 
        dcc.Store(id='internal-value_first_refresh_1', data=0),
        dcc.Store(id='internal-value_ind_park_1', data=0), 
        dcc.Store(id='internal-value_ind_park_coord_1', data=IndPark_pos),        
        dcc.Store(id='internal-value_marker_option_1', data=0),        
        dcc.Store(id='internal-value_route_opt_done_1', data=0),   
        dcc.Store(id='internal-value_stops_1', data=[]),
        dcc.Store(id='internal-value_coworking_1', data=[]),
        dcc.Store(id='internal-value_coworking_days_1', data=0),        
        dcc.Store(id='internal-value_routes_1', data=[]),         
        dcc.Store(id='internal-value_routes_len_1', data=[]),        
        dcc.Store(id='internal-value_scenario_1', data=[]),       
        dcc.Store(id='internal-value_loaded_scenario_1', data=[]),   
        dcc.Store(id='internal-value_calculated_scenarios_1', data=[]),      
        dcc.Store(id='internal-value_remote_days_1', data=0),
        dcc.Store(id='internal-value_remote_workers_1', data=0),        
        dcc.Store(id='internal-value_eCar_adoption_1', data=0),
        dcc.Store(id='internal-value_eCar_co2_km_1', data=0),
        dcc.Store(id='internal-value_bus_number_1', data = 0), 
        dcc.Store(id='internal-value_trip_freq_1', data=30),
        dcc.Store(id='internal-value_trip_number_1', data=1),
        dcc.Store(id='internal-value_start_hour_1', data='8:00'),     
        dcc.Store(id='internal-value_co2_km_car_1', data=0.19),     
        dcc.Store(id='internal-value_co2_km_bus_1', data=1.46),     
        dcc.Store(id='internal-value_co2_km_train_1', data=0.019), 
        dcc.Store(id='internal-value_bus_train_ratio_1', data=0.8)        
        ],
        id='sidebar_1',
        style=SIDEBAR_STYLE)


#        dcc.Store(id='internal-value_username', data=app.config['username'])  

markers_all_1 = []
markers_remote_1 = []
markers_cow_1 = []
IndPark_marker = [dl.Marker(dl.Tooltip("Industrial Park"), position=IndPark_pos, icon=custom_icon_IndPark, id='IndPark_1')]


central_panel_1 = html.Div(
       [
          html.P(['Sustainable Commuting Platform (SCP): help your business transition towards a sustainable mobility '],id='title_SCP_1',style={'font-size': '24px',"font-weight": "bold"}),
          dls.Clock(
                    children=[ 
                                dl.Map(
                                [dl.ScaleControl(position="topright"),
                                 dl.LayersControl(
                                        [dl.BaseLayer(dl.TileLayer(), name='CO2', checked='CO2'),
                                         dl.BaseLayer(dl.TileLayer(), name='CO2/CO2_target', checked=False),
                                         #dl.BaseLayer(dl.TileLayer(), name='weighted_d', checked=False),
                                         dl.BaseLayer(dl.TileLayer(), name='Has a bus stop', checked=False),
                                         dl.BaseLayer(dl.TileLayer(), name='Family type', checked=False)]  +
                                        [dl.Overlay(dl.LayerGroup(markers_all_1), name="all", id='markers_all_1', checked=False),
                                         dl.Overlay(dl.LayerGroup(markers_remote_1), name="remote", id='markers_remote_1', checked=False),
                                         dl.Overlay(dl.LayerGroup(markers_cow_1), name="coworking", id='markers_cow_1', checked=False)], 
                                        id="lc_1"
                                        )
                                ] + IndPark_marker, 
                                center=center, 
                                zoom=12,
                                id="map_1",
                                style={'width': '100%', 'height': '75vh', 'margin': "auto", "display": "block"})
                    ],
                    color="#435278",
                    speed_multiplier=1.5,
                    width=80,
                    show_initially=False
                    ),
          html.Div([
             html.Img(src=image1,style={'width':'40%', "display": "inlineBlock", "verticalAlign": "top"}),
             #html.Img(src=image2,style={'width':'25%',"display": "inlineBlock", "verticalAlign": "top"}),
             #html.Img(src=image3,style={'width':'25%',"display": "inlineBlock", "verticalAlign": "top"})

             ],style= {'verticalAlign': 'top'})                    
    ],
    style=CONTENT_STYLE)

radius_max = 1

#d_tmp = {'counts': [100, 50, 2], 'distance_week': [100, 50, 2], 'Mode': ['Car','PT','Walk'], 'color': ['red','blue','green']}
d_tmp = {'counts': [30, 30, 30], 'distance_week': [1, 20, 50], 'Mode': ['Car','PT','Walk'], 'color': ['red','blue','green']}
df_tmp = pd.DataFrame(data=d_tmp)

cmap = cm.get_cmap('RdYlGn', 30)    # PiYG
interv = np.linspace(0,1,cmap.N)
j = 0
steps_gauge = []
for i in reversed(range(cmap.N-1)):
    rgba = cmap(i)
    t = {'range':[interv[j],interv[j+1]],'color': matplotlib.colors.rgb2hex(rgba)}
    j+=1
    steps_gauge.append(t)

fig1 = go.Indicator(mode = "gauge+number",
                        value = 0.0,
                       domain = {'x': [0, 1], 'y': [0, 1]},        
                        gauge= {
                                'steps':steps_gauge,
                                'axis':{'range':[0,1]},
                                'bar':{
                                        'color':'black',
                                        'thickness':0.5
                                      }
                                }

                    )


fig2 = go.Pie(labels=df_tmp["Mode"],
                  values=df_tmp["counts"],
                  showlegend=False,
                  textposition='inside',
                  textinfo='label+percent',
                  marker=dict(colors=df_tmp['color']))

headerColor = 'rgb(107, 174, 214)'
fig3 = go.Table(
            columnwidth = [40,60],
            header=dict(
                values=['<b>ton/week</b>','<b>kg/week/person</b>'],
                line_color='darkslategray',
                fill_color=headerColor,
                align=['center','center','center'],
                font=dict(color='white', size=14)
            ),
            cells=dict(
                values=[["{:.3f}".format(0.)],["{:.2f}".format(0.)]],
                fill_color=['rgb(107, 174, 214)'],
                line_color='darkslategray',
                align='center', font=dict(color='black', size=14)
            ))


rowEvenColor = 'rgb(189, 215, 231)'
rowOddColor = 'rgb(107, 174, 214)'
fig4 = go.Table(
            columnwidth = [70,70],
            cells=dict(
                values=[["<b>Number of routes</b>:{:.2f}".format(0.),
                         "<b>Coworking hubs</b>:{:.2f}".format(0.),
                         "<b>Remote workers (%)</b>:{:.2f}".format(0.),
                         "<b>Car electrification (%)</b>:{:.2f}".format(0.)],
                        ["<b>Number of stops</b>:{:.2f}".format(0.),
                         "<b>Coworking days</b>:{:.2f}".format(0.),
                         "<b>Remote days</b>:{:.2f}".format(0.),
                         "<b>CO2/km WRT combus.</b>:{:.2f}".format(0.)]],
                fill_color = [[rowOddColor,rowEvenColor,rowOddColor,rowEvenColor,rowOddColor]*2],
                line_color='darkslategray',
                align='center', font=dict(color='black', size=14)
            ))

fig5 = go.Bar(
            x=df_tmp['distance_week'],
            y=df_tmp['Mode'],
            orientation='h',
            marker_color=df_tmp['color'])

fig = make_subplots(rows=4, cols=2,
                    subplot_titles=("Fractional CO2 emissions", "Transport share (%)", 
                                    "Total CO2 emissions", "Interventions", 
                                    "Weekly distance share (km)"),
                    specs=[
                            [{"type": "indicator"},{"type": "pie"}],
                            [{"type": "table", "colspan": 2},None],
                            [{"type": "table", "colspan": 2},None],   
                            [{"type": "bar", "colspan": 2},None]                      
                            ],
                    row_heights=[0.5,0.3,1,0.4],
                    vertical_spacing=0.05
                    ) #-> row height is used to re-size plots of specific rows

fig.append_trace(fig1, 1, 1)
fig.append_trace(fig2, 1, 2)
fig.append_trace(fig3, 2, 1)
fig.append_trace(fig4, 3, 1) 
fig.append_trace(fig5, 4, 1)


#fig.update_yaxes(title_text="CO2 emissions", row=1, col=1)
#fig.update_yaxes(title_text="Transport share", row=2, col=1)
#fig.update_yaxes(title_text="Distance share", row=3, col=1)
fig.update_annotations(font_size=18)
fig.update_layout(showlegend=False)    
fig.update_layout(polar=dict(radialaxis=dict(visible=False)))
fig.update_polars(radialaxis=dict(range=[0, radius_max]))

# 
#            style={'width': '70vh', 'height': '100vh'})
indicators_1 = html.Div(
        [              
        dcc.Graph(
            figure=fig,
            id = 'Indicator_panel_1',
            style={'width': '65vh', 'height': '90vh'}) 
        ],
        style=INDICATORS_STYLE
        )



def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = None)
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_layout(
        autosize=False,
        width=10,
        height=150,
        margin=dict(
        l=0,
        ))    
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)

    return fig

#style={'width':'120vh', 'height':'120vh'}
indicators_2 = html.Div(
        [     
          html.Div([
              dcc.Graph(
                #figure="", 
                id='graph2', 
                style={'width':'120vh', 'height':'150vh'}
                )
           
            ], 
            #style={'width':'100%'}
            )
        ],
        style=INDICATORS_STYLE_2)


indicators_3 = html.Div(
        [              
        #dcc.Graph(
        #    #figure=fig,
        #    id = 'Indicator_panel_3',
        #    style={'width': '60vh', 'height': '100vh'}) 
        dcc.Graph(id='Indicator_panel_3', 
                  figure = blank_fig())

        ]
        )
indicators_4 = html.Div(
        [              
        #dcc.Graph(
        #    #figure=fig,
        #    id = 'Indicator_panel_3',
        #    style={'width': '60vh', 'height': '100vh'}) 
        dcc.Graph(id='Indicator_panel_4', 
                  figure = blank_fig())

        ]
        )

Tab_1 = dbc.Card(
    dbc.CardBody(
        [
        dbc.Row(
            [
                #dbc.Col(sidebar_1, width=2, className='bg-light'),
                dbc.Col(sidebar_1, md=2, className='bg-light'),
                #dbc.Col(central_panel_1, width=7),
                dbc.Col(central_panel_1, md=7),
                #dbc.Col(indicators_1, width=3)
                dbc.Col(indicators_1, md=3)
            ])
        ]
    ),
    className="mt-3",
)

Tab_2 = dbc.Card(
    dbc.CardBody(
        [
        dbc.Row(
            [
                dbc.Col(indicators_2, width='auto')
                #dbc.Col("", width=12)                
            ])
        ]
    ),
    className="mt-3",
)

Tab_3 = dbc.Card(
    dbc.CardBody(
        [
        dbc.Row(
                    html.Div(
                              dcc.Upload(id='add-scenario_1',
                                         children=html.Div([
                                         dbc.Button('Load scenario')
                                        ]),
                                        # Allow multiple files to be uploaded
                                        multiple=True
                                        )
                    ),
                    style={"margin-top": "15px"},
                    #width='auto'
              ),

        dbc.Row(
            [
                dbc.Col(indicators_3, width='auto'),
                #dbc.Col("", width='auto'),                
            ],
            id='Tab_3'
            )
        ]
    ),
    className="mt-3"
)



tabs = dbc.Tabs(
    [
        dbc.Tab(Tab_1, label="Calculate scenarios"),
        dbc.Tab(Tab_2, label="Detailed result visualization"),
        dbc.Tab(Tab_3, label="Scenarios comparison")       
    ]
)

#app.layout = html.Div(children=[tabs])
layout = html.Div(children=[tabs])