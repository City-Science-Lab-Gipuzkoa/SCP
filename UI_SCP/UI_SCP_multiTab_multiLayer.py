## #!/home/cslgipuzkoa/virtual_machine_disk/anaconda3/envs/SCP_test/bin/python
import dash
from dash import Dash
import dash_bootstrap_components as dbc
import dash_loading_spinners as dls
from dash import html, callback_context, ALL
from dash import dcc, Output, Input, State, callback, dash_table

from dash_extensions import Download
from dash_extensions.snippets import send_file
from dash_extensions.snippets import send_data_frame

import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_daq as daq

from flask import Flask
from flask import request

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

server = Flask(__name__)
#app = Dash(name = 'SCP_app', server = server, external_stylesheets=[dbc.themes.BOOTSTRAP],prevent_initial_callbacks=True,suppress_callback_exceptions = True)
app = Dash(name = 'SCP_app', server = server,
           external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc.icons.BOOTSTRAP],prevent_initial_callbacks=True,suppress_callback_exceptions = True)


# Generate a timestamp-based ID
timestamp_id = str(int(time.time()))
root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
#root_dir = '/home/cslgipuzkoa/virtual_machine_disk/UI_SCP/assets/'

print('Code restarted!')

#"/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/calcroutes_module.py"

#im1 = '/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/CSL_logo.PNG'
#im2 = '/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/DFG_logo.png'
#im1 = '/home/beppe23/mysite/assets/CSL_logo.PNG'
#im2 = '/home/beppe23/mysite/assets/DFG_logo.png'
im1 = root_dir +'images/CSL_logo.PNG'
#im2 = root_dir +'images/DFG_logo.png'
#im3 = root_dir +'images/MUBIL_logo.png'

#stops_file = "/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/GTFS_files_bus_stops_12_02_2024/all_stops_12_02_2024.csv"
#stops_file = "/home/beppe23/mysite/assets/all_stops_12_02_2024.csv"
#stops_file = "C:/Users/gfotidellaf/Desktop/CSL_Gipuzkoa/Accessibility/assets/all_stops_12_02_2024.csv"
stops_file = root_dir +'data/all_bus_stops.csv'


from PIL import Image
image1 = Image.open(im1)
#image2 = Image.open(im2)
#image3 = Image.open(im3)


stops_df = pd.read_csv(stops_file, encoding='latin-1')
stops_lat_lon = stops_df[['stop_lat','stop_lon']].to_numpy()

bus_icon = "https://i.ibb.co/HV0K5Fp/bus-stop.png" 
worker_icon = "https://i.ibb.co/W0H7nYM/meeting-point.png"
coworking_icon = "https://i.ibb.co/J2qXGKN/coworking-icon.png"

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

stops_actions = [{'label': 'Delete marker', 'value': 'DM'},
                 {'label': 'Set origin of bus routes', 'value': 'SO'},
                 {'label': 'Set coworking hub', 'value': 'SC'}                   
                ]

interventions = [{'label': 'Company transportation', 'value': 'CT'},
                 {'label': 'Remote working', 'value': 'RW'},
                 {'label': 'Coworking', 'value': 'CW'}                  
                ]

choose_transp_hour = [{'label': "{:02d}".format(i) + ':00' + '-' + "{:02d}".format(i+1) + ':00', 'value': i} for i in range(24)] 


Step_1_text="Step 1:\nLoad and visualize raw data "
Step_2_text="Step 2:\nRun baseline scenario "
Step_3_text="Step 3:\nSelect type of intervention "
Step_4_text="Step 4:\nSelect time for commuting "

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
                                'margin': '10px'
                            },
                            # Allow multiple files to be uploaded
                            multiple=True),
                            dbc.Button("Visualize clusters of workers", id="show_workers_1", n_clicks=0,style={"margin-top": "15px","font-weight": "bold"}),
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
                            value=19,
                            id='n_clusters_1',
                            marks=None,
                            tooltip={"placement": "bottom", "always_visible": True}
                            ),
                            #html.Br(),   
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
            html.P(['Select action for markers'],id='action_select_1',style={"margin-top": "15px", "font-weight": "bold"}),
            dcc.Dropdown(stops_actions, multi=False,style={"margin-top": "15px"}, id='choose_stop_action_1'),           
            html.Div(id='sidebar_intervention_1', style={"margin-top": "15px"})
            ],
           id="Intervention_type_panel_1",
           is_open=False,
           )
        ]),


        dbc.Row([
            dbc.Col([
                        html.P([Step_4_text],style={"font-weight": "bold","white-space": "pre"}),
                    ],
                    #style={'height': '80px'},width=8),
                    md=8),
            dbc.Col([        
                        collapse_button_4,
                    ],
                    #style={'height': '80px'},width=3
                    md=3
                    )                    
        ]),
        dbc.Row([
                dbc.Collapse([
                    html.P(['Choose time range'],style={"font-weight": "bold","white-space": "pre"}),
                    html.Div(dcc.Dropdown(choose_transp_hour, multi=False, id='choose_transp_hour_1'))            
                    ],
                    id='Select_time_panel_1',
                    is_open=False,
                ),
        ]),
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
                html.P(['Liters of gasoline per kilometer (car)'],id='gas_km_car_1',style={"margin-top": "15px","font-weight": "bold"}),
                dcc.Slider(0, 5,0.02,
                    value=1./12,
                    id='choose_gas_km_car_1',
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),                   
                #html.P([ html.Br(),'Liters of gasoline per kilometer (bus)'],id='gas_km_bus_1',style={"margin-top": "15px","font-weight": "bold"}),
                html.P(['Liters of gasoline per kilometer (bus)'],id='gas_km_bus_1',style={"margin-top": "15px","font-weight": "bold"}),
                dcc.Slider(0, 10,0.05,
                    value=1.12,
                    id='choose_gas_km_bus_1',
                    marks=None,
                    tooltip={"placement": "bottom", "always_visible": True}
                ),                    
                #html.P([ html.Br(),'CO2 Kg per lt'],id='CO2_lt_1',style={"margin-top": "15px","font-weight": "bold"}),
                html.P(['CO2 Kg per lt'],id='CO2_lt_1',style={"margin-top": "15px","font-weight": "bold"}),

                dcc.Slider(0, 10,0.05,
                    value=2.3,
                    id='choose_CO2_lt_1',
                    marks=None,
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
                            style={"white-space": "pre"}),
              
        dbc.Row(
                    html.Div(
                              dcc.Upload(id='button_load_scenario_1',
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
        dcc.Store(id='internal-value_route_opt_done_1', data=0),   
        dcc.Store(id='internal-value_stops_1', data=[]),
        dcc.Store(id='internal-value_coworking_1', data=[]),
        dcc.Store(id='internal-value_coworking_days_1', data=0),        
        dcc.Store(id='internal-value_routes_1', data=[]),        
        dcc.Store(id='internal-value_scenario_1', data=[]),       
        dcc.Store(id='internal-value_loaded_scenario_1', data=[]),   
        dcc.Store(id='internal-value_calculated_scenarios_1', data=[]),      
        dcc.Store(id='internal-value_remote_days_1', data=0),
        dcc.Store(id='internal-value_remote_workers_1', data=0),
        dcc.Store(id='internal-value_bus_number_1', data = 0) 
        ],
        id='sidebar_1',
        style=SIDEBAR_STYLE)


markers_all_1 = []
markers_remote_1 = []
markers_cow_1 = []
central_panel_1 = html.Div(
       [
          html.Div([
             html.Img(src=image1,style={'width':'40%', "display": "inlineBlock", "verticalAlign": "top"}),
             #html.Img(src=image2,style={'width':'25%',"display": "inlineBlock", "verticalAlign": "top"}),
             #html.Img(src=image3,style={'width':'25%',"display": "inlineBlock", "verticalAlign": "top"})

             ],style= {'verticalAlign': 'top'}),
          dls.Clock(
                    children=[ dl.Map(
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
                                ], 
                                center=center, 
                                zoom=12,
                                id="map_1",style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
                    ],
                    color="#435278",
                    speed_multiplier=1.5,
                    width=80,
                    show_initially=False
                    )
    ],
    style=CONTENT_STYLE)


#fig.update_layout(
#    margin=dict(l=100, r=100, t=5, b=5)
#)
#fig.update_layout(width=int(100))
# plot test data
#df = px.data.tips()
#fig = px.pie(df, values='tip', names='day')
#fig.update_layout(showlegend=False)
#fig.update_layout(title_text='Transport share', title_x=0.5)
d_tmp = {'counts': [100, 50, 2], 'distance_week': [100, 50, 2], 'Mode': ['Car','PT','Walk'], 'color': ['red','blue','green']}
df_tmp = pd.DataFrame(data=d_tmp)

radius_max = 1
x0 = 1
x1 = 30
x2 = 2
x3 = 2
x4 = 7  
x5 = 7                          
x0_max = 5
x1_max = 100
x2_max = 3
x3_max = 5
x4_max = 15
x5_max = 15
fig1 = go.Scatterpolar(
            r=[radius_max*x0/x0_max, radius_max*x1/x1_max, radius_max*x2/x2_max, radius_max*x3/x3_max, radius_max*x4/x4_max, radius_max*x5/x5_max],
            theta=['Remote working days',
                   'Remote working persons (%)',
                   'Coworking hubs', 
                   'Coworking days', 
                   'Bus routes',
                   'Bus stops'],
            hovertext= [str(x0),str(x1), str(x2), str(x3), str(x4), str(x5)],
            fill='toself'
        )


cmap = cm.get_cmap('RdYlGn', 30)    # PiYG
interv = np.linspace(0,1,cmap.N)
j = 0
steps_gauge = []
for i in reversed(range(cmap.N-1)):
    rgba = cmap(i)
    t = {'range':[interv[j],interv[j+1]],'color': matplotlib.colors.rgb2hex(rgba)}
    j+=1
    steps_gauge.append(t)

fig2 = go.Indicator(mode = "gauge+number",
                        value = 0.3,
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


fig3 = go.Pie(labels=df_tmp["Mode"],
                  values=df_tmp["counts"],
                  showlegend=False,
                  textposition='inside',
                  textinfo='label+percent',
                  marker=dict(colors=df_tmp['color']))


fig4 = go.Bar(
            x=df_tmp['distance_week'],
            y=df_tmp['Mode'],
            orientation='h',
            marker_color=df_tmp['color'])

row_titles = ("Interventions", "CO2 emissions", "Transport share (%)", "Weekly distance share (km)")
column_titles = ()

fig = make_subplots(rows=4, cols=1, 
                    specs=[
                            [{"type": "scatterpolar"}], [{"type": "indicator"}],
                            [{"type": "pie"}], [{"type": "bar"}]],
                    row_heights=[2,1,2,1],
                    subplot_titles=row_titles
                    ) #-> row height is used to re-size plots of specific rows
#fig.for_each_annotation(lambda a:  a.update(y = 1.05) if a.text in column_titles else a.update(x = -0.07) if a.text in row_titles else())
fig.for_each_annotation(lambda a:  a.update(x = 0.2) if a.text in row_titles else())
fig.append_trace(fig1, 1, 1)
fig.append_trace(fig2, 2, 1)
fig.append_trace(fig3, 3, 1)
fig.append_trace(fig4, 4, 1)   

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
            style={'width': '60vh', 'height': '100vh'}) 
        ],
        style=INDICATORS_STYLE
        )

central_panel2 = html.Div(
       [
          html.Div([
             html.Img(src=image1,style={'width':'40%', "display": "inlineBlock", "verticalAlign": "top"}),

             ],style= {'verticalAlign': 'top'}),
          dls.Clock(
                    children=[dl.Map([dl.TileLayer(),
                                      dl.ScaleControl(position="topright")], center=center, 
                                      zoom=12,
                                      id="map_2",style={'width': '90vh', 'height': '70vh', "margin": "auto", "display": "block"})
                    ],
                    color="#435278",
                    speed_multiplier=1.5,
                    width=80,
                    show_initially=False
                    )
    ],
    style=CONTENT_STYLE)


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

app.layout = html.Div(children=[tabs])

# Folder navigator ###############################################################
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    #df.to_csv(temp_file, index=False)
    gdf = geopandas.GeoDataFrame(df, 
                                 geometry = geopandas.points_from_xy(df.O_long, df.O_lat), 
                                 crs="EPSG:4326"
        )
      
    return gdf  


def parse_contents_load_scenario(contents, filename, date):
    content_type, content_string = contents.split(',')    
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    
    if 'scenario' in filename:
        gdf = geopandas.GeoDataFrame(df, 
                                 geometry = geopandas.points_from_xy(df.O_long, df.O_lat), 
                                 crs="EPSG:4326"
        )
        #out = plot_result(gdf)
        #gdf.columns = df.columns
        out = [gdf, gdf.columns]
    else:
        out =  df

    return out


def drawclusters(workers_df,n_clusters):
    from sklearn.cluster import KMeans
    from scipy.spatial import ConvexHull

    workers_lat_lon = workers_df[['O_lat', 'O_long']].values.tolist()
    workers_lat_lon = np.array(workers_lat_lon)
    model = KMeans(n_clusters=n_clusters, max_iter=500).fit(workers_lat_lon)
    clusters_poly = []
    #points_per_cluster = []
    for i in range(n_clusters):
        points = workers_lat_lon[model.labels_ == i]
        hull = ConvexHull(points)
        vert = np.append(hull.vertices, hull.vertices[0])  # close the polygon by appending the first point at the end
        clusters_poly.append(points[vert])
        #points_per_cluster.append(len(points))
    return clusters_poly

def suggest_clusters(wdf):
    #sil_score_max = -100 #this is the minimum possible score
    dist_max = 100
    wdf = wdf[['O_lat', 'O_long']].values.tolist()
    alpha = 0.65
    n_max_clusters = int(19.*len(wdf)/2507)
    #beta = (1-alpha)*19 + alpha*0.63
    sil_score_max = 1

    for n_clusters in range(2,31):
        #model = KMeans(n_clusters = n_clusters, init='k-means++', max_iter=100, n_init=1)
        model = KMeans(n_clusters = n_clusters)
        labels = model.fit_predict(wdf)
        #sil_score = silhouette_score(wdf, labels, sample_size=len(wdf), random_state=42, metric= 'mahalanobis')
        sil_score = silhouette_score(wdf, labels, metric= 'manhattan')
        #db_score = davies_bouldin_score(wdf, labels)
        #ar_score = adjusted_rand_score(wdf, labels)
        #sil_score = silhouette_score(wdf, labels)
        #aver_score = (1 - alpha)*n_clusters/n_max_clusters + alpha*sil_score
        #x = (1-alpha)*n_clusters + alpha*sil_score    
        #aver_score = - (x - beta)**2 + 1
        d0 = (1-alpha)*(n_max_clusters - n_clusters)/n_max_clusters
        d1 = alpha*(sil_score_max - sil_score) 
        dist_to_max = (d0**2 + d1**2)**0.5
        print("The average silhouette and db score for %i clusters are %0.2f; the average score is %0.2f" %(n_clusters,sil_score, dist_to_max))
        #if sil_score > sil_score_max:
        if dist_to_max < dist_max:   
           dist_max = dist_to_max
           best_n_clusters = n_clusters
    return best_n_clusters    

def generate_colors(n):
    import random
    colors = []
    for i in range(n):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = '#%02x%02x%02x'%(r, g, b)
        if color not in colors:
            colors.append(color)
    return colors 


def interpolate_color(color_start_rgb, color_end_rgb, t):
    """
    Interpolate between two RGB colors.
    
    Parameters:
    - color_start_rgb: Tuple of integers representing the starting RGB color.
    - color_end_rgb: Tuple of integers representing the ending RGB color.
    - t: Float representing the interpolation factor between 0 and 1.
    
    Returns:
    - A tuple representing the interpolated RGB color.
    """
    #print(color_start_rgb)
    #color_start_rgb = color_start_rgb.split('#')[1] 
    #color_end_rgb = color_end_rgb.split('#')[1]
    return tuple(int(start_val + (end_val - start_val) * t) for start_val, end_val in zip(color_start_rgb, color_end_rgb))

def hex_to_rgb(hex_color):
    """
    Convert hex to RGB.
    
    Parameters:
    - hex_color: String representing the hexadecimal color code.
    
    Returns:
    - A tuple of integers representing the RGB values.
    """
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

#def generate_color_gradient(CO2max,CO2_i, n_colors=256, n_min=0):
def generate_color_gradient(CO2max,CO2_i, label=0):
    #from  matplotlib.colors import ListedColormap, Normalize, LogNorm
    import matplotlib as mpl

    """
    cmap = mpl.colors.ListedColormap(['green', 'yellow', 'red'])
     #norm = mpl.colors.Normalize(vmin=0, vmax=100)
    norm = mpl.colors.LogNorm(vmin=0+1, vmax=CO2max+1) 
    # create a scalarmappable from the colormap
    #sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)  
    sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
    #color_hex= mpl.colors.to_hex(sm.to_rgba(idx), keep_alpha=False)
    color_hex= mpl.colors.to_hex(sm.to_rgba(CO2_i))
    """
    """
    ranges = [
        {"start": "2ECC71", "end": "F7DC6F"},
        {"start": "F7DC6F", "end": "E74C3C"}
    ]
    """
    if label==0:
        ranges = [
            {"start": "2ECC71", "end": "F4D03F"},
            {"start": "F4D03F", "end": "C0392B"}
        ]
        color_start_hex = ranges[0]["start"]
        color_end_hex = ranges[0]["end"]
        color_start_rgb = hex_to_rgb(color_start_hex)
        color_end_rgb = hex_to_rgb(color_end_hex)
        # Generate gradient
        gradient1 = [interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 256)]
        color_start_hex = ranges[1]["start"]
        color_end_hex = ranges[1]["end"]
        color_start_rgb = hex_to_rgb(color_start_hex)
        color_end_rgb = hex_to_rgb(color_end_hex)
        # Generate gradient
        gradient2 = [interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 256)]
        gradient = gradient1 + gradient2

    elif label== 'Car':
        ranges = [
            {"start": "F1948A", "end": "B03A2E"}
        ]
        color_start_hex = ranges[0]["start"]
        color_end_hex = ranges[0]["end"]
        color_start_rgb = hex_to_rgb(color_start_hex)
        color_end_rgb = hex_to_rgb(color_end_hex)
        # Generate gradient
        gradient = [interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 256)]
    
    elif label== 'PT':
        ranges = [
            {"start": "D6EAF8", "end": "21618C"}
        ]
        color_start_hex = ranges[0]["start"]
        color_end_hex = ranges[0]["end"]
        color_start_rgb = hex_to_rgb(color_start_hex)
        color_end_rgb = hex_to_rgb(color_end_hex)
        # Generate gradient
        gradient = [interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 256)]    

    else:
        return '#2ECC71'
    

    N = len(gradient)

    value = int((CO2_i/CO2max)*N)
    idx = np.argmin(np.abs(np.array(range(N))-value))
    color = [gradient[idx][0]/255,gradient[idx][1]/255,gradient[idx][2]/255]
    color_hex = mpl.colors.to_hex(color)
    #if value == N:
    #print(value,idx,color)

    return color_hex


def create_square_icon(color, border_color):
    import base64
    import io
    from PIL import Image, ImageDraw, ImageOps    
    # Create a square shape
    square_size = 20
    
    # Create a blank image
    image = Image.new('RGBA', (square_size, square_size), color=(0, 0, 0, 0))
    
    # Draw the square shape on the image
    draw = ImageDraw.Draw(image)
    draw.rectangle([(0, 0), (square_size, square_size)], fill=color)
    
    # Add a black border to the square
    border_size = 2
    border_image = ImageOps.expand(image, border=border_size, fill=border_color)
    
    # Convert the image to base64
    buffered = io.BytesIO()
    border_image.save(buffered, format="PNG")
    base64_icon = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return "data:image/png;base64," + base64_icon

def create_square_marker(color, border_color):
    square_icon = create_square_icon(color, border_color)
    return dict(type="custom", iconUrl=square_icon)

def create_diamond_icon(color, border_color):
    import base64
    import io
    from PIL import Image, ImageDraw, ImageOps     
    # Create a diamond shape
    diamond_size = 20
    diamond_path = "M0,0 L" + str(diamond_size) + ",0 L" + str(diamond_size) + "," + str(diamond_size) + " L0," + str(diamond_size) + " Z"
    
    # Create a blank image
    image = Image.new('RGBA', (diamond_size, diamond_size), color=(0, 0, 0, 0))
    
    # Draw the diamond shape on the image
    draw = ImageDraw.Draw(image)
    draw.polygon([(0, 0), (diamond_size, 0), (diamond_size, diamond_size), (0, diamond_size)], fill=color)
    
    # Rotate the diamond image by 90 degrees
    #rotated_image = image.rotate(45, expand=True)
    
    # Add a black border to the diamond
    border_size = 2
    #border_image = ImageOps.expand(rotated_image, border=border_size, fill=border_color)
    border_image = ImageOps.expand(image, border=border_size, fill=border_color)


    # Rotate the border image back by 45 degrees
    border_image = border_image.rotate(45, expand=True)
    
    # Convert the image to base64
    buffered = io.BytesIO()
    border_image.save(buffered, format="PNG")
    base64_icon = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return "data:image/png;base64," + base64_icon


def create_diamond_marker(color, border_color):
    diamond_icon = create_diamond_icon(color, border_color)
    return dict(type="custom", iconUrl=diamond_icon)

"""
def create_triangle_icon(color, border_color):
    import base64
    import io
    from PIL import Image, ImageDraw, ImageOps 
    # Create a triangle shape
    triangle_size = 30
    triangle_points = [(0, triangle_size), (triangle_size // 2, 0), (triangle_size, triangle_size)]
    
    # Create a blank image
    image = Image.new('RGBA', (triangle_size, triangle_size), color=(0, 0, 0, 0))
    
    # Draw the triangle shape on the image
    draw = ImageDraw.Draw(image)
    draw.polygon(triangle_points, fill=color)
    
    # Add a triangular border to the triangle
    border_size = 5
    border_image = Image.new('RGBA', (triangle_size + border_size * 2, triangle_size + border_size * 2), color=(0, 0, 0, 0))

    #border_image = ImageOps.expand(rotated_image, border=border_size, fill=border_color)
    border_image = ImageOps.expand(image, border=border_size, fill=border_color)
    border_draw = ImageDraw.Draw(border_image)
    #border_points = [(border_size, triangle_size + border_size), (triangle_size // 2 + border_size, border_size), (triangle_size + border_size, triangle_size + border_size)]
    #border_points = [(border_size, triangle_size + border_size), (triangle_size // 2 + border_size, border_size + border_size), (triangle_size + border_size, triangle_size + border_size - border_size)]
    border_points = [(border_size, triangle_size + border_size), (triangle_size // 2 + border_size, border_size + border_size), (triangle_size + border_size, border_size + border_size)]
    border_draw.polygon(border_points, outline=border_color)
    #border_draw.pieslice([(border_size, border_size), (triangle_size + border_size, triangle_size + border_size)], 0, 180, outline=border_color)
    #border_draw.pieslice([(border_size, triangle_size + border_size), (triangle_size // 2 + border_size, triangle_size + border_size)], 180, 360, outline=border_color)    
    #border_draw.pieslice([(border_size, border_size), (triangle_size + border_size, triangle_size + border_size)], 360, 540, outline=border_color)
    # Composite the triangle and border images
    result_image = Image.alpha_composite(border_image.resize(image.size), image)
    
    # Crop the result image to remove the extra border
    result_image = result_image.crop((border_size, border_size, triangle_size + border_size, triangle_size + border_size))

    # Convert the image to base64
    buffered = io.BytesIO()
    result_image.save(buffered, format="PNG")
    base64_icon = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return "data:image/png;base64," + base64_icon  
"""

def create_triangle_icon(color, border_color):
    import base64
    import io
    from PIL import Image, ImageDraw, ImageOps

    # Create a triangle shape
    triangle_size = 30
    #triangle_points = [(0, 0), (triangle_size, triangle_size // 2), (0, triangle_size)]
    triangle_points = [(0, 0), (triangle_size // 2, triangle_size), (triangle_size, 0)]

    # Create a blank image
    image = Image.new('RGBA', (triangle_size, triangle_size), color=(0, 0, 0, 0))

    # Draw the triangle shape on the image
    draw = ImageDraw.Draw(image)
    draw.polygon(triangle_points, fill=color)

    # Create a border around the triangle
    border_size = 1
    border_image = Image.new('RGBA', (triangle_size + border_size * 2, triangle_size + border_size * 2), color=(0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border_image)
    border_points = [(border_size, border_size), (triangle_size + border_size, border_size), (triangle_size // 2 + border_size, triangle_size + border_size)]
    border_draw.polygon(border_points, outline=border_color)
    # Resize the border image to match the size of the image
    border_image = border_image.resize((triangle_size, triangle_size))

    # Composite the triangle and border images
    result_image = Image.alpha_composite(image, border_image)

    buffered = io.BytesIO()
    result_image.save(buffered, format="PNG")
    base64_icon = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return "data:image/png;base64," + base64_icon


def create_triangle_marker(color, border_color):
    triangle_icon = create_triangle_icon(color, border_color)
    return dict(type="custom", iconUrl=triangle_icon)


def plot_result(result, NremDays, NremWork, CowDays, Nbuses, stored_scenarios, StopsCoords=[], CowFlags=[]):

    radius_max = 1
    x0 = NremDays
    x1 = NremWork
    x2 = sum(CowFlags)
    x3 = CowDays
    x4 = Nbuses
    x5 = len(StopsCoords) - sum(CowFlags)                           
    x0_max = 5
    x1_max = 100
    x2_max = 3
    x3_max = 5
    x4_max = 10
    x5_max = 15
    fig1 = go.Scatterpolar(
                r=[radius_max*x0/x0_max, radius_max*x1/x1_max, radius_max*x2/x2_max, radius_max*x3/x3_max, radius_max*x4/x4_max, radius_max*x5/x5_max],
                theta=['Remote working days',
                    'Remote working persons (%)',
                    'Coworking hubs',
                    'Coworking days', 
                    'Bus routes',
                    'Bus stops'],
                hovertext= [str(x0),str(x1), str(x2), str(x3), str(x4), str(x5)],
                fill='toself'
            )

    Total_CO2 = result['CO2'].sum()
    temp = result.loc[result['Rem_work'] == 1]
    Total_CO2_remote = temp['CO2'].sum() # this will be used later
    temp = result.loc[result['Coworking'] == 1]
    Total_CO2_cowork = temp['CO2'].sum() # this will be used later

    Total_CO2_worst_case = result['CO2_worst_case'].sum()
    
    cmap = cm.get_cmap('RdYlGn', 30)    # PiYG
    interv = np.linspace(0,1,cmap.N)
    j = 0
    steps_gauge = []
    for i in reversed(range(cmap.N-1)):
        rgba = cmap(i)
        t = {'range':[interv[j],interv[j+1]],'color': matplotlib.colors.rgb2hex(rgba)}
        j+=1
        steps_gauge.append(t)

    fig2 = go.Indicator(mode = "gauge+number",
                        value = Total_CO2/Total_CO2_worst_case,
                        domain = {'x': [0, 1], 'y': [0, 1]},        
                        gauge  = {
                                    'steps':steps_gauge,
                                    'axis':{'range':[0,1]},
                                    'bar':{
                                            'color':'black',
                                            'thickness':0.5
                                        }
                                    }
                        )

    predicted = result['prediction']
    unique_labels, counts = np.unique(predicted, return_counts=True)
    d = {'Mode': unique_labels, 'counts':counts}
    df = pd.DataFrame(data=d)
    df['Mode'] = df['Mode'].map({0:'Walk',1:'PT',2:'Car'})
    df['color'] = df['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
    fig3 = go.Pie(labels=df["Mode"],
                    values=df["counts"],
                    showlegend=False,
                    textposition='inside',
                    textinfo='label+percent',
                    marker=dict(colors=df['color']))

    temp = result.copy()
    temp['distance_km'] = temp['distance_week']/1000.
    temp = temp[['Mode','distance_km']]
    Contribs = temp.groupby(['Mode']).sum() 
    Contribs = Contribs.reset_index()
    Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
    fig4 = go.Bar(
                x=Contribs['distance_km'],
                y=Contribs['Mode'],
                orientation='h',
                marker_color=Contribs['color'])

    
    row_titles = ("Interventions", "CO2 emissions", "Transport share (%)", "Weekly distance share (km)")

    fig_total = make_subplots(rows=4, cols=1, 
                        specs=[
                                [{"type": "scatterpolar"}], [{"type": "indicator"}],
                                [{"type": "pie"}], [{"type": "bar"}]],
                        row_heights=[2,1,2,1],
                        subplot_titles=row_titles
                        ) #-> row height is used to re-size plots of specific rows
    #fig.for_each_annotation(lambda a:  a.update(y = 1.05) if a.text in column_titles else a.update(x = -0.07) if a.text in row_titles else())
    fig_total.for_each_annotation(lambda a:  a.update(x = 0.2) if a.text in row_titles else())
    fig_total.append_trace(fig1, 1, 1)
    fig_total.append_trace(fig2, 2, 1)
    fig_total.append_trace(fig3, 3, 1)
    fig_total.append_trace(fig4, 4, 1) 
    fig_total.update_annotations(font_size=18)
    fig_total.update_layout(showlegend=False)    
    fig_total.update_layout(polar=dict(radialaxis=dict(visible=False)))
    fig_total.update_polars(radialaxis=dict(range=[0, radius_max]))
    fig_total.update_layout(title_text='Calculated scenario')


    try:
        new_scenarios = json.loads(stored_scenarios)
        from datetime import datetime
        now = datetime.now() # current date and time
        date_time = now.strftime("%m/%d/%Y_%H:%M:%S")
        scenario_name = date_time
    except:
        new_scenarios = stored_scenarios
        scenario_name = 'baseline'

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj) 
   
    calculated_scenario = {
            'name': scenario_name,            
            'NremDays': NremDays,
            'NremWork': NremWork,
            'CowDays': CowDays,
            'Nbuses': Nbuses,
            'CowFlags': CowFlags,
            'StopsCoords': StopsCoords,
            'Total_CO2': Total_CO2,
            'Total_CO2_remote': Total_CO2_remote,
            'Total_CO2_cowork': Total_CO2_cowork,
            'Total_CO2_worst_case': Total_CO2_worst_case,
            'counts': df["counts"].tolist(), 
            'Transport_share_labels': df["Mode"].tolist(),
            'distance_km': Contribs['distance_km'].tolist(), 
            'Distance_share_labels': Contribs["Mode"].tolist()
        }
    new_scenarios.append(calculated_scenario)
    print()
    print('new scenarios: ')
    print(new_scenarios)

    new_stored_scenarios = json.dumps(new_scenarios, cls=NumpyEncoder)
    baseline_scenario = next(item for item in new_scenarios if item["name"] == "baseline")
    
    BS_TS_df = pd.DataFrame({'counts': baseline_scenario['counts']}, index = baseline_scenario['Transport_share_labels'])
    BS_DS_df = pd.DataFrame({'distance_km': baseline_scenario['distance_km']}, index = baseline_scenario['Distance_share_labels'])

    temp_df = df.copy()
    temp_Contribs = Contribs.copy()
    diff_TS_df = temp_df[['Mode','counts']].set_index('Mode').subtract(BS_TS_df)
    diff_DS_df = temp_Contribs[['Mode','distance_km']].set_index('Mode').subtract(BS_DS_df)


    #temp_df = pd.DataFrame({'counts': df['counts'].tolist()}, index=df['Mode'].tolist())
    #temp_Contribs = pd.DataFrame({'distance_km': Contribs['distance_km'].tolist()}, index=Contribs['Mode'].tolist())

    #TS_diff_perc = diff_TS_df['counts'].div(temp_df.loc[diff_TS_df.index, 'counts'])
    #DS_diff_perc = diff_DS_df['distance_km'].div(temp_Contribs.loc[temp_Contribs.index, 'distance_km'])
    BS_TS_df['Mode'] = BS_TS_df.index
    BS_DS_df['Mode'] = BS_DS_df.index
    TS_diff_perc = diff_TS_df.merge(BS_TS_df, on='Mode', suffixes=('_diff', '_baseline')).assign(
                    counts_ratio=lambda x: x['counts_diff'].div(x['counts_baseline']))
    DS_diff_perc = diff_DS_df.merge(BS_DS_df, on='Mode', suffixes=('_diff', '_baseline')).assign(
                    distance_km_ratio=lambda x: x['distance_km_diff'].div(x['distance_km_baseline']))



    y_diff = [Total_CO2_remote-baseline_scenario['Total_CO2_remote'], Total_CO2_cowork-baseline_scenario['Total_CO2_cowork'], Total_CO2-baseline_scenario['Total_CO2']]
    totals = [baseline_scenario['Total_CO2_remote']+1, baseline_scenario['Total_CO2_cowork']+1, baseline_scenario['Total_CO2']]
    y_perc = [100*i / j for i, j in zip(y_diff, totals)]
    colors = ['#f1948a' if x > 0 else '#abebc6' for x in y_diff]
    print()
    print('baseline:')
    print(totals)
    print('present calc.:')
    print([Total_CO2_remote, Total_CO2_cowork, Total_CO2])
    print('Diff:')
    print(y_diff)
    print()
    print('Baseline share:')
    print(BS_TS_df)
    print('Transport share:')
    print(temp_df)
    print('Transport share diff:')
    print(diff_TS_df)
    print()    
    print()
    print('Baseline distance share:')
    print(BS_DS_df)
    print('Distance share:')
    print(temp_Contribs)    
    print('Distance share diff:')
    print(diff_DS_df)
    print()
    print('TS_diff_perc')
    print(TS_diff_perc)
    print()
    print('DS_diff_perc')
    print(DS_diff_perc)

    fig2 = go.Bar(
                y=y_diff[:2],
                x=['Remote','Coworking'],
                marker_color=colors[:2])
    fig22 = go.Bar(
                y=[y_perc[2]],
                x=['Total'],                
                marker_color=colors[2])

    fig3 = go.Bar(
                y=100*TS_diff_perc['counts_ratio'],
                x=df['Mode'],
                marker_color=df['color'])

    fig4 = go.Bar(
                y=100*DS_diff_perc['distance_km_ratio'],
                x=Contribs['Mode'],
                marker_color=Contribs['color'])


    row_titles = ("Interventions","CO2 emissions difference WRT baseline","", "Transport share difference WRT baseline (%)", "Distance share difference WRT baseline (%)")

    fig_comp = make_subplots(
        rows=4, cols=2,
        specs=[[{"type": "scatterpolar","colspan": 2}, None],
               [{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar","colspan": 2}, None],
               [{"type": "bar","colspan": 2}, None]],
               row_heights=[2,1,1,1],
               subplot_titles=row_titles,
               horizontal_spacing=0.07,
                ) 

    fig_comp.add_trace(fig1, 1, 1)    
    fig_comp.add_trace(fig2, 2, 1)
    fig_comp.add_trace(fig22, 2, 2)
    fig_comp.add_trace(fig3, 3, 1)    
    fig_comp.add_trace(fig4, 4, 1)    

    fig_comp.update_annotations(font_size=18)
    fig_comp.update_layout(showlegend=False)    
    fig_comp.update_layout(polar=dict(radialaxis=dict(visible=False)))
    fig_comp.update_polars(radialaxis=dict(range=[0, radius_max]))
    fig_comp.update_layout(title_text='Calculated scenario')
    #fig_comp.update_yaxes(secondary_y=False, title_text="Remote, Coworking (kg/week)", row=2, col=1)  
    #fig_comp.update_yaxes(title_text="Remote, Coworking (kg/week)", row=2, col=1)  
    #fig_comp.update_yaxes(secondary_y=True, title_text="Total (%)", row=2, col=1)           

    fig_comp.update_xaxes(categoryorder='array', categoryarray= ['Walk','PT','Car'], row=3, col=1)
    fig_comp.update_xaxes(categoryorder='array', categoryarray= ['Walk','PT','Car'], row=4, col=1)
    #fig.for_each_annotation(lambda a:  a.update(y = 1.05) if a.text in column_titles else a.update(x = -0.07) if a.text in row_titles else())

    """
    fig_comp = make_subplots(rows=4, cols=2, 
                        specs=[[{"type": "scatterpolar", "colspan": 2},None], 
                               [{"type": "bar"},{"secondary_y": True}],
                               [{"colspan": 2},None],
                               [{"colspan": 2},None]],
                        row_heights=[2,1,1,1],
                        subplot_titles=row_titles,
                        horizontal_spacing=0.07,
                        ) 
    fig_comp = make_subplots(rows=4, cols=1, 
                        specs=[[{"type": "scatterpolar"}], 
                               [{"secondary_y": True}],
                               [{"type": "bar"}],
                               [{"type": "bar"}]],
                        row_heights=[2,1,1,1],
                        subplot_titles=row_titles,
                        horizontal_spacing=0.07,
                        ) #-> row height is used to re-size plots of specific rows
    #fig.for_each_annotation(lambda a:  a.update(y = 1.05) if a.text in column_titles else a.update(x = -0.07) if a.text in row_titles else())
    """
    """
    fig_comp.for_each_annotation(lambda a:  a.update(x = 0.5) if a.text in row_titles else())
    fig_comp.add_trace(fig1, 1, 1)
    #fig_comp.add_trace(fig2, 2, 1, secondary_y=False)
    #fig_comp.add_trace(fig22, 2, 1, secondary_y=True)
    fig_comp.add_trace(fig2, 2, 1)
    fig_comp.add_trace(fig22, 2, 2, secondary_y=True)
    fig_comp.add_trace(fig3, 3, 1)
    fig_comp.add_trace(fig4, 4, 1)


    fig_comp.update_annotations(font_size=18)
    fig_comp.update_layout(showlegend=False)    
    fig_comp.update_layout(polar=dict(radialaxis=dict(visible=False)))
    fig_comp.update_polars(radialaxis=dict(range=[0, radius_max]))
    fig_comp.update_layout(title_text='Calculated scenario')
    #fig_comp.update_yaxes(secondary_y=False, title_text="Remote, Coworking (kg/week)", row=2, col=1)  
    fig_comp.update_yaxes(title_text="Remote, Coworking (kg/week)", row=2, col=1)  
    fig_comp.update_yaxes(secondary_y=True, title_text="Total (%)", row=2, col=1)           

    fig_comp.update_xaxes(categoryorder='array', categoryarray= ['Walk','PT','Car'], row=3, col=1)
    fig_comp.update_xaxes(categoryorder='array', categoryarray= ['Walk','PT','Car'], row=4, col=1)
    """

    #Total_CO2_worst_case = result['CO2_worst_case'].sum()
    temp = result.loc[result['Rem_work'] == 1]
    Total_CO2_worst_case = temp['CO2_worst_case'].sum() + 0.000001 # to avoid div. by 0
    Total_CO2 = temp['CO2'].sum()
    fig1 = go.Indicator(mode = "gauge+number",
                        value = Total_CO2/Total_CO2_worst_case,
                       domain = {'x': [0, 1], 'y': [0, 1]},        
                        gauge= {
                                'steps':steps_gauge,
                                'axis':{'range':[0,1]},
                                'bar':{
                                        'color':'black',
                                        'thickness':0.5
                                      }
                                })

    temp = result.loc[result['Coworking'] == 1]
    Total_CO2_worst_case = temp['CO2_worst_case'].sum() + 0.000001 # to avoid div. by 0
    Total_CO2 = temp['CO2'].sum()
    fig2 = go.Indicator(mode = "gauge+number",
                       value = Total_CO2/Total_CO2_worst_case,
                       domain = {'x': [0, 1], 'y': [0, 1]},      
                        gauge= {
                                'steps':steps_gauge,
                                'axis':{'range':[0,1]},
                                'bar':{
                                        'color':'black',
                                        'thickness':0.5
                                      }
                                })
        
    temp = result.loc[(result['Rem_work'] == 0) & (result['Coworking'] == 0)]
    Total_CO2_worst_case = temp['CO2_worst_case'].sum() + 0.000001 # to avoid div. by 0
    Total_CO2 = temp['CO2'].sum()
    fig3 = go.Indicator(mode = "gauge+number",
                       value = Total_CO2/Total_CO2_worst_case,
                       domain = {'x': [0, 1], 'y': [0, 1]},        
                       gauge= {
                                'steps':steps_gauge,
                                'axis':{'range':[0,1]},
                                'bar':{
                                        'color':'black',
                                        'thickness':0.5
                                      }
                                })

    predicted = result.loc[result['Rem_work'] == 1, 'prediction']   
    unique_labels, counts = np.unique(predicted, return_counts=True)
    d = {'Mode': unique_labels, 'counts':counts}
    df = pd.DataFrame(data=d)
    df['Mode'] = df['Mode'].map({0:'Walk',1:'PT',2:'Car'}) 
    df['color'] = df['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'}) 
    fig4 = go.Pie(labels=df["Mode"],
                  values=df["counts"],
                  showlegend=False,
                  textposition='inside',
                  textinfo='label+percent',
                  marker=dict(colors=df['color']),
                  scalegroup = 'one')

    predicted = result.loc[result['Coworking'] == 1, 'prediction']
    unique_labels, counts = np.unique(predicted, return_counts=True)
    d = {'Mode': unique_labels, 'counts':counts}
    df = pd.DataFrame(data=d)
    df['Mode'] = df['Mode'].map({0:'Walk',1:'PT',2:'Car'}) 
    df['color'] = df['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})     
    fig5 = go.Pie(labels=df["Mode"],
                  values=df["counts"],
                  showlegend=False,
                  textposition='inside',
                  textinfo='label+percent',
                  marker=dict(colors=df['color']),
                  scalegroup = 'one')
 
    predicted = result.loc[(result['Rem_work'] == 0) & (result['Coworking'] == 0), 'prediction']  
    unique_labels, counts = np.unique(predicted, return_counts=True)
    d = {'Mode': unique_labels, 'counts':counts}
    df = pd.DataFrame(data=d)
    df['Mode'] = df['Mode'].map({0:'Walk',1:'PT',2:'Car'}) 
    df['color'] = df['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'}) 
    fig6 = go.Pie(labels=df["Mode"],
                  values=df["counts"],
                  showlegend=False,
                  textposition='inside',
                  textinfo='label+percent',
                  marker=dict(colors=df['color']),
                  scalegroup = 'one')


    temp = result.loc[result['Rem_work'] == 1]
    if not temp.empty:
        temp['distance_km'] = temp['distance_week']/1000.
        temp = temp[['Mode','distance_km']]
        Contribs = temp.groupby(['Mode']).sum() 
        Contribs = Contribs.reset_index()
        Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
    else:
        data = {'Mode': ['No mode'],
                'distance_km': [0],
                'color': ['#FF0000']}
        Contribs = pd.DataFrame(data)
        
    print(Contribs.head())
    fig7 = go.Bar(
            x=Contribs['distance_km'],
            y=Contribs['Mode'],
            orientation='h',
            marker_color=Contribs['color'])
    max_dist_1 = Contribs['distance_km'].max()

    temp = result.loc[result['Coworking'] == 1]    
    if not temp.empty:
        temp['distance_km'] = temp['distance_week']/1000.
        temp = temp[['Mode','distance_km']]
        Contribs = temp.groupby(['Mode']).sum() 
        Contribs = Contribs.reset_index()
        Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
    else:        
        data = {'Mode': ['No mode'],
                'distance_km': [0],
                'color': ['#FF0000']}
        Contribs = pd.DataFrame(data)
    fig8 = go.Bar(
            x=Contribs['distance_km'],
            y=Contribs['Mode'],
            orientation='h',
            marker_color=Contribs['color'])
    max_dist_2 = Contribs['distance_km'].max()

    temp = result.loc[(result['Rem_work'] == 0) & (result['Coworking'] == 0)]
    if not temp.empty:
        temp['distance_km'] = temp['distance_week']/1000.
        temp = temp[['Mode','distance_km']]
        Contribs = temp.groupby(['Mode']).sum() 
        Contribs = Contribs.reset_index()
        Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
    else:
        data = {'Mode': ['No mode'],
                'distance_km': [0],
                'color': ['#FF0000']}
        Contribs = pd.DataFrame(data)
    fig9 = go.Bar(
            x=Contribs['distance_km'],
            y=Contribs['Mode'],
            orientation='h',
            marker_color=Contribs['color'])
    max_dist_3 = Contribs['distance_km'].max()
    max_distance = max(max_dist_1,max_dist_2,max_dist_3)

    #family_types = ['Hogar de una persona', 'Otros hogares sin niños', '2 adultos',
    #                '2 adultos con niño(s)', '1 adulto con niño(s)',
    #                'Otros hogares con niños']    
    no_kids_df = result.loc[(result['Rem_work'] == 1) & (result['Tipo_familia'] <3) & (result['Mode'] == 'Car')]
    kids_df    = result.loc[(result['Rem_work'] == 1) &(result['Tipo_familia'] >2) & (result['Mode'] == 'Car')]
    fig10 = go.Bar(
            x=['No kids', 'Kids'],
            y=[len(no_kids_df['CO2'].index),len(kids_df['CO2'].index)],
            marker_color=['red','orange'],
            marker=dict(cornerradius="30%"))
    max_families_1 = max(len(no_kids_df['CO2'].index),len(kids_df['CO2'].index))

    no_kids_df = result.loc[(result['Coworking'] == 1) & (result['Tipo_familia'] <3) & (result['Mode'] == 'Car')]
    kids_df    = result.loc[(result['Coworking'] == 1) &(result['Tipo_familia'] >2) & (result['Mode'] == 'Car')]
    fig11 = go.Bar(
            x=['No kids', 'Kids'],
            y=[len(no_kids_df['CO2'].index),len(kids_df['CO2'].index)],
            marker_color=['red','orange'],
            marker=dict(cornerradius="30%"))
    max_families_2 = max(len(no_kids_df['CO2'].index),len(kids_df['CO2'].index))

    no_kids_df = result.loc[(result['Rem_work'] == 0) & (result['Coworking'] == 0) & (result['Tipo_familia'] <3) & (result['Mode'] == 'Car')]
    kids_df    = result.loc[(result['Rem_work'] == 0) & (result['Coworking'] == 0) & (result['Tipo_familia'] >2) & (result['Mode'] == 'Car')]
    fig12 = go.Bar(
            x=['No kids', 'Kids'],
            y=[len(no_kids_df['CO2'].index),len(kids_df['CO2'].index)],
            marker_color=['red','orange'],
            marker=dict(cornerradius="30%"))
    max_families_3 = max(len(no_kids_df['CO2'].index),len(kids_df['CO2'].index))

    max_families = max(max_families_1,max_families_2,max_families_3)

    column_titles = ['Remote working', 'Coworking', 'Rest']
    row_titles = ['CO2 emissions', 'Transport share', 'Distance share (km)', 'Using car']
    #fig = make_subplots(rows=1, cols=3)
    fig_decomp = make_subplots(rows=4, cols=3, 
                        specs=[
                               [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                               [{"type": "pie"}, {"type": "pie"}, {"type": "pie"}],
                               [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
                               [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]],
                        column_titles = column_titles,
                        row_titles = row_titles,
                        row_heights=[1, 2, 2, 2],
                        vertical_spacing = 0.1
                        ) #-> row height is used to re-size plots of specific rows
    
    #fig = make_subplots(rows=2, cols=3)
    fig_decomp.for_each_annotation(lambda a:  a.update(y = 1.05) if a.text in column_titles else a.update(x = -0.07) if a.text in row_titles else())
    fig_decomp.append_trace(fig1, 1, 1)
    fig_decomp.append_trace(fig2, 1, 2)
    fig_decomp.append_trace(fig3, 1, 3)
    fig_decomp.append_trace(fig4, 2, 1)
    fig_decomp.append_trace(fig5, 2, 2)
    fig_decomp.append_trace(fig6, 2, 3)
    fig_decomp.append_trace(fig7, 3, 1)
    fig_decomp.append_trace(fig8, 3, 2)
    fig_decomp.append_trace(fig9, 3, 3)
    fig_decomp.append_trace(fig10, 4, 1)
    fig_decomp.append_trace(fig11, 4, 2)
    fig_decomp.append_trace(fig12, 4, 3)      

    #fig.update_xaxes(title_text="Total weekly distance (km)", showgrid=True, row=3, col=1)
    #fig.update_xaxes(title_text="Total weekly distance (km)", showgrid=True, row=3, col=2)
    #fig.update_xaxes(title_text="Total weekly distance (km)", showgrid=True, row=3, col=3)        
    fig_decomp.update_annotations(font_size=28)
    fig_decomp.update_layout(showlegend=False)    
    fig_decomp.update_xaxes(showgrid=True, row=3, col=1, range=[0, max_distance])
    fig_decomp.update_xaxes(showgrid=True, row=3, col=2, range=[0, max_distance])
    fig_decomp.update_xaxes(showgrid=True, row=3, col=3, range=[0, max_distance])
    fig_decomp.update_yaxes(showgrid=True, row=4, col=1, range=[0, max_families])
    fig_decomp.update_yaxes(showgrid=True, row=4, col=2, range=[0, max_families])
    fig_decomp.update_yaxes(showgrid=True, row=4, col=3, range=[0, max_families])


    Total_CO2 = result['CO2'].sum()
    Total_CO2_worst_case = result['CO2_worst_case'].sum()
    markers_all_1 = []
    markers_remote_1 = []
    markers_cow_1 = []
    markers_remote_cow_1 = []
    markers_comm_1 = []


    custom_icon_coworking_big = dict(
        iconUrl= "https://i.ibb.co/J2qXGKN/coworking-icon.png",
        iconSize=[50,50],
        iconAnchor=[0, 0]
        )
    custom_icon_coworking = dict(
        iconUrl= "https://i.ibb.co/jMgmc4W/cowork-small-icon.png",
        iconSize=[20,20],
        iconAnchor=[10, 10]
        )  
    custom_icon_home = dict(
        iconUrl= "https://i.ibb.co/0ZqM4PG/home-icon.png",
        iconSize=[20,20],
        iconAnchor=[10, 10]
        )


    for i_pred in result.itertuples():
        #print(i_pred.geometry.y, i_pred.geometry.x)
        #color = generate_color_gradient(maxCO2,i_pred.CO2) 
        #color = generate_color_gradient(i_pred.CO2_worst_case,i_pred.CO2) 
        
        maxCO2 = result.groupby("Mode")['CO2'].max()[i_pred.Mode]
        color = generate_color_gradient(maxCO2,i_pred.CO2, i_pred.Mode) 
        #color = generate_color_gradient(maxCO2_worst_case,i_pred.CO2, i_pred.Mode) 
        #print(color)
        #text = i_pred.Mode
        text = 'CO2: ' + '{0:.2f}'.format(i_pred.CO2) + ' Kg ' + '(' + i_pred.Mode + ')' + '<br>' +  'Weekly distance: ' + '{0:.2f}'.format(i_pred.distance_week/1000) + ' Km'
        #text = text + '<br>' + 'Remote working: ' + str(i_pred.Rem_work)
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

        #try:
        if  i_pred.Rem_work > 0.0 and i_pred.Coworking == 0.0:
                #marker_i = dl.Marker(children=[dl.Tooltip(content=text)], 
                #                     position=[i_pred.geometry.y, i_pred.geometry.x], 
                #                     icon=custom_icon_home, 
                #                     id=str(i_pred))
                marker_i = dl.Marker(
                    id=str(i_pred),
                    children=[dl.Tooltip(content=text, offset={"x": 5, "y": 10})],
                    position=[i_pred.geometry.y, i_pred.geometry.x],
                    icon=create_diamond_marker(color, (0, 0, 0))
                )
                markers_remote_1.append(marker_i)
        #except:
        #    pass
        #try:
        if  i_pred.Coworking > 0.0 and i_pred.Rem_work == 0.0:
                #marker_i = dl.Marker(children=[dl.Tooltip(content=text)], 
                #                     position=[i_pred.geometry.y, i_pred.geometry.x], 
                #                     icon=custom_icon_coworking, 
                #                     id=str(i_pred))
                marker_i = dl.Marker(
                        id=str(i_pred),
                        children=[dl.Tooltip(content=text, offset={"x": 5, "y": 10})],
                        position=[i_pred.geometry.y, i_pred.geometry.x],
                        icon=create_square_marker(color, (0, 0, 0))
                )                     
                markers_cow_1.append(marker_i)
        #except:
        #    pass  

        #try:
        if  i_pred.Coworking > 0.0 and i_pred.Rem_work > 0.0:
                #marker_i = dl.Marker(children=[dl.Tooltip(content=text)], 
                #                     position=[i_pred.geometry.y, i_pred.geometry.x], 
                #                     icon=custom_icon_coworking, 
                #                     id=str(i_pred))
                marker_i = dl.Marker(
                        id=str(i_pred),
                        children=[dl.Tooltip(content=text, offset={"x": 5, "y": 10})],
                        position=[i_pred.geometry.y, i_pred.geometry.x],
                        icon=create_triangle_marker(color, (0, 0, 0))
                )                     
                markers_remote_cow_1.append(marker_i)
        #except:
        #    pass 

        markers_all_1.append(marker_i)  

    markers_comm_1 = list(set(markers_all_1) - set(markers_remote_1) - set(markers_cow_1) )
    
    Legend =  html.Div(
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
                    html.Span('Remote and coworking', style={'color': 'blue', 'font-size': '14px', 'font-weight': 'bold'})
                ]
            ),

        ]
    )

    #children.append(dl.ScaleControl(position="topright"))
    children = [ 
                Legend,
                dl.TileLayer(),
                dl.ScaleControl(position="topright"),
                dl.LayersControl(
                                [dl.BaseLayer(dl.TileLayer(), name='CO2', checked=False),
                                 dl.BaseLayer(dl.TileLayer(), name='CO2/CO2_target', checked=False),
                                 #dl.BaseLayer(dl.TileLayer(), name='weighted_d', checked=False),
                                 dl.BaseLayer(dl.TileLayer(), name='Has a bus stop', checked=False),
                                 dl.BaseLayer(dl.TileLayer(), name='Family type', checked=False)] +
                                [dl.Overlay(dl.LayerGroup(markers_all_1), name="all", id= 'markers_all_1', checked=True),
                                 dl.Overlay(dl.LayerGroup(markers_remote_1), name="remote",id= 'markers_remote_1', checked=True),
                                 dl.Overlay(dl.LayerGroup(markers_cow_1), name="coworking",id= 'markers_cow_1', checked=True), 
                                 dl.Overlay(dl.LayerGroup(markers_comm_1), name="home-headquarters",id= 'markers_comm_1', checked=True),
                                 dl.Overlay(dl.LayerGroup(markers_remote_cow_1), name="remote+coworking",id= 'markers_remote_cow_1', checked=True),
                                 ], 
                                id="lc_1"
                                )                      
                ]

    if CowFlags:
        Cow_markers = []
        for i, pos in enumerate(StopsCoords): 
            if CowFlags[i]==1:
                tmp = dl.Marker(dl.Tooltip("Coworking hub"), position=pos, icon=custom_icon_coworking_big, id={'type': 'marker', 'index': i})    
                Cow_markers.append(tmp)  
        children = children + Cow_markers

    new_map = dl.Map(children, center=center,
                                     zoom=12,                        
                                     id="map_1",style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})

    #return [Total_CO2/Total_CO2_worst_case, fig_total, fig_decomp, new_map]
    return [fig_total, new_map, fig_decomp, fig_comp, new_stored_scenarios]


def categorize_Mode(code):
    if 'Andando' in code:
        return 'Walk'
    elif 'Coche' in code:
        return 'Car'
    else:
        return 'PT'
    
def run_MCM(trips_ez, root_Dir, Transh, routeOptDone, gkm_car=1./12, gkm_bus=1.1, co2lt=2.3, NremDays=0, NremWork=0, CowCoords=[], CowDays=0):
    import pandas as pd
    import sys    
    root_dir = root_Dir
    sys.path.append(root_dir + 'modules')
    import pp
    import prediction
    import pandas as pd
 
    if Transh == None:
        Transh = 8
        print('Transport hour not selected. Using default (08:00)')
    else:
        print('Chosen transport hour: ',Transh)
    workers_data_dir = 'data/'
    MCM_data_dir = 'data/input_data_MCM/'    
    model_dir = 'modules/models/'
    #trips_ez = pd.read_csv(root_dir + data_dir + 'workers_eskuzaitzeta_2k.csv')
    #trips_ez = pd.read_csv(root_dir + workers_data_dir + 'temp_workers_data.csv')    
    #if baseline == 1:    
    #    trips_ez['Modo'].apply(categorize_Mode)    
    #    trips_ez['Mode'] = trips_ez['Modo']
  
    eliminar = ['Unnamed: 0', 'Com_Ori', 'Com_Des', 'Modo', 'Municipio',
                'Motos','Actividad','Año','Recur', 'Income', 'Income_Percentile'] 
    try:
        trips_ez = trips_ez.drop(columns=eliminar)
    except:
        pass
    #trips_ez.head(10).to_csv(root_dir + workers_data_dir + 'template_workers_data.csv',index=False)
    trips_ez=pp.pp(Transh,trips_ez, routeOptDone, CowCoords, CowDays, NremWork, NremDays, root_dir, MCM_data_dir) 
    #trips_ez['transit_tt'] = trips_ez['transit_tt'].apply(lambda x: x*0.2)
    #trips_ez['drive_tt'] = trips_ez['drive_tt'].apply(lambda x: x*1)
    prediction=prediction.predict(trips_ez, gkm_car, gkm_bus, co2lt, root_dir + model_dir)  
    return prediction
 

@app.callback(
    [Output('user_ip', 'data'),
     Output('root_dir_1','data')],
    [Input('url', 'pathname'), Input('user_ip', 'data')],
    [State('user_ip', 'modified_timestamp')]
)
def update_user_ip(pathname, user_ip, modified_timestamp):
    #if not modified_timestamp:
    #user_ip = request.remote_addr
    #user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    user_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    #user_ip2 = request.environ.get('REMOTE_ADDR')
    #user_ip3 = request.access_route[0]
    print()
    print()
    print('user IP: ', user_ip)   
    print()
    print()
    """
    print(request.__dict__)
    print()
    print('selected items:')
    print(request.headers)
    print(request.cookies)
    print(request.data)
    print(request.args)
    print(request.form)
    print(request.endpoint)
    print(request.method)
    print(request.remote_addr)

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        print('no proxy?: ',request.environ['REMOTE_ADDR'])
    else:
        print('with proxy?: ',request.environ['HTTP_X_FORWARDED_FOR']) # if behind a proxy

    #user_ip2 = request.environ.get('REMOTE_ADDR')
    #user_ip3 = request.access_route[0]
    print()
    print()
    print('user IP: ', user_ip)
    print()
    print()

    import netifaces as nif

    def mac_for_ip(ip):
        'Returns a list of MACs for interfaces that have given IP, returns None if not found'
        for i in nif.interfaces():
            addrs = nif.ifaddresses(i)
            try:
               if_mac = addrs[nif.AF_LINK][0]['addr']
               if_ip = addrs[nif.AF_INET][0]['addr']
            except (IndexError, KeyError): #ignore ifaces that dont have MAC or IP
               if_mac = if_ip = None
            if if_ip == ip:
               return if_mac
        return None

    print('MAC addr.?: ',mac_for_ip(user_ip))
    """


    root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
    #root_dir = '/home/cslgipuzkoa/virtual_machine_disk/UI_SCP/assets/'
    #new_root_dir = root_dir[:-1] + '_' + timestamp_id + '/'
    #new_root_dir = root_dir[:-1] + '_' + user_id + '/'
    new_root_dir = root_dir[:-1] + '_' + user_ip + '/'

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

    #sys.path.append('/content/drive/MyDrive/Colab Notebooks')
    sys.path.append(root_dir + 'modules')
    #"/content/drive/MyDrive/Colab Notebooks/calcroutes_module.py"
    #import calcroutes_module -> import inside callback function
    #import generate_GTFS_module -> import inside callback function

    print()
    print('Cleaning folders...')
    shutil.rmtree(root_dir + 'data/input_data_MCM/GTFS_feeds')
    shutil.rmtree(root_dir + 'data/input_data_MCM/transit_together_24h')
    shutil.copytree(root_dir + 'data/input_data_MCM/GTFS_feeds_backup', root_dir + 'data/input_data_MCM/GTFS_feeds')
    shutil.copytree(root_dir + 'data/input_data_MCM/transit_together_24h_backup', root_dir + 'data/input_data_MCM/transit_together_24h')
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


@callback(
    [Output("Tab_3", "children",allow_duplicate=True),
    Output("internal-value_calculated_scenarios_1","data",allow_duplicate=True)],
    [Input('add-scenario_1', 'contents'),
    State('add-scenario_1', 'filename'),
    State('add-scenario_1', 'last_modified'),
    State('Tab_3', 'children'),
    State('internal-value_calculated_scenarios_1','data')],
    prevent_initial_call=True)
def add_scenario(list_of_contents, list_of_names, list_of_dates, Tab3, stored_scenarios):

    if list_of_contents is not None:
        print()
        print('list of names:')
        print(list_of_names)
        inputs = [
            parse_contents_load_scenario(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates) if 'inputs' in n]
        stops_CowHubs = [
            parse_contents_load_scenario(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates) if 'StopsCowHubs' in n]
        #scenario = []
        scenario = [
            parse_contents_load_scenario(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates) if 'scenario' in n]

        scenario_name = [n.split('/')[-1] for n in list_of_names if 'scenario' in n][0]

        #out = plot_result(result, NremDays, NremWork, CowDays, Nbuses, StopsCoords, CowoFlags)

        try:
            print('inputs:')
            print(inputs)    
            inputs = np.array(inputs[0][:])[0]
            #print(inputs)         
            #print(inputs[0])
            #print(inputs[1])
            NremDays = inputs[0] 
            NremWork = inputs[1]
            CowDays = inputs[2]
            Nbuses = inputs[3]
            print()
        except:
            pass


        try:
            stops_CowHubs = np.array(stops_CowHubs[0][:])[:]           
            lats = stops_CowHubs[:,0]
            lons = stops_CowHubs[:,1]
            CowFlags = stops_CowHubs[:,2]
            #StopsCoords = map(list, zip(lats,lons))
            StopsCoords = list(zip(lats,lons))
            print('Stops:')
            print(StopsCoords)

        except:
            StopsCoords = []
            CowFlags = []


        print()
        print('loaded scenario:')
        print(scenario)
        col_names = scenario[0][:][1].tolist() 
        print(len(col_names))
        scenario = np.array(scenario[0][:][0])
        scenario = pd.DataFrame(scenario)
        print(len(scenario.columns))
        print(col_names)
        scenario.columns = col_names
        #scenario = geopandas.GeoDataFrame(scenario, 
        #                         geometry = geopandas.points_from_xy(scenario.O_long, scenario.O_lat), 
        #                         crs="EPSG:4326"
        #)
        scenario = geopandas.GeoDataFrame(scenario)  
        print(scenario.columns.tolist())     

    radius_max = 1
    x0 = NremDays
    x1 = NremWork
    x2 = sum(CowFlags)
    x3 = CowDays
    x4 = Nbuses
    x5 = len(StopsCoords) - sum(CowFlags)   

    x0_max = 5
    x1_max = 100
    x2_max = 3
    x3_max = 5
    x4_max = 10
    x5_max = 15
    fig1 = go.Scatterpolar(
                r=[radius_max*x0/x0_max, radius_max*x1/x1_max, radius_max*x2/x2_max, radius_max*x3/x3_max, radius_max*x4/x4_max, radius_max*x5/x5_max],
                theta=['Remote working days',
                    'Remote working persons (%)',
                    'Coworking hubs',
                    'Coworking days', 
                    'Bus routes',
                    'Bus stops'],
                hovertext= [str(x0),str(x1), str(x2), str(x3), str(x4), str(x5)],
                fill='toself'
            )


    Total_CO2 = scenario['CO2'].sum()
    temp = scenario.loc[scenario['Rem_work'] == 1]
    Total_CO2_remote = temp['CO2'].sum() # this will be used later
    temp = scenario.loc[scenario['Coworking'] == 1]
    Total_CO2_cowork = temp['CO2'].sum() # this will be used later

    Total_CO2_worst_case = scenario['CO2_worst_case'].sum()
    
    
    cmap = cm.get_cmap('RdYlGn', 30)    # PiYG
    interv = np.linspace(0,1,cmap.N)
    j = 0
    steps_gauge = []
    for i in reversed(range(cmap.N-1)):
        rgba = cmap(i)
        t = {'range':[interv[j],interv[j+1]],'color': matplotlib.colors.rgb2hex(rgba)}
        j+=1
        steps_gauge.append(t)

    fig2 = go.Indicator(mode = "gauge+number",
                        value = Total_CO2/Total_CO2_worst_case,
                        domain = {'x': [0, 1], 'y': [0, 1]},        
                        gauge  = {
                                    'steps':steps_gauge,
                                    'axis':{'range':[0,1]},
                                    'bar':{
                                            'color':'black',
                                            'thickness':0.5
                                        }
                                    }
                        )

    predicted = scenario['prediction']
    unique_labels, counts = np.unique(predicted, return_counts=True)
    d = {'Mode': unique_labels, 'counts':counts}
    df = pd.DataFrame(data=d)
    df['Mode'] = df['Mode'].map({0:'Walk',1:'PT',2:'Car'})
    df['color'] = df['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
    fig3 = go.Pie(labels=df["Mode"],
                    values=df["counts"],
                    showlegend=False,
                    textposition='inside',
                    textinfo='label+percent',
                    marker=dict(colors=df['color']))

    temp = scenario.copy()
    temp['distance_km'] = temp['distance_week']/1000.
    temp = temp[['Mode','distance_km']]
    Contribs = temp.groupby(['Mode']).sum() 
    Contribs = Contribs.reset_index()
    Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
    fig4 = go.Bar(
                x=Contribs['distance_km'],
                y=Contribs['Mode'],
                orientation='h',
                marker_color=Contribs['color'])

    try:
        new_scenarios = json.loads(stored_scenarios)
        from datetime import datetime
        now = datetime.now() # current date and time
        date_time = now.strftime("%m/%d/%Y_%H:%M:%S")
        scenario_name = date_time
    except:
        new_scenarios = stored_scenarios
        scenario_name = 'baseline'

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super().default(obj) 
   
    calculated_scenario = {
            'name': scenario_name,            
            'NremDays': NremDays,
            'NremWork': NremWork,
            'CowDays': CowDays,
            'Nbuses': Nbuses,
            'CowFlags': CowFlags,
            'StopsCoords': StopsCoords,
            'Total_CO2': Total_CO2,
            'Total_CO2_remote': Total_CO2_remote,
            'Total_CO2_cowork': Total_CO2_cowork,
            'Total_CO2_worst_case': Total_CO2_worst_case,
            'counts': df["counts"].tolist(), 
            'Transport_share_labels': df["Mode"].tolist(),
            'distance_km': Contribs['distance_km'].tolist(), 
            'Distance_share_labels': Contribs["Mode"].tolist()
        }
    new_scenarios.append(calculated_scenario)
    print()
    print('new scenarios: ')
    print(new_scenarios)

    new_stored_scenarios = json.dumps(new_scenarios, cls=NumpyEncoder)
    baseline_scenario = next(item for item in new_scenarios if item["name"] == "baseline")
    
    BS_TS_df = pd.DataFrame({'counts': baseline_scenario['counts']}, index = baseline_scenario['Transport_share_labels'])
    BS_DS_df = pd.DataFrame({'distance_km': baseline_scenario['distance_km']}, index = baseline_scenario['Distance_share_labels'])

    temp_df = df.copy()
    temp_Contribs = Contribs.copy()
    diff_TS_df = temp_df[['Mode','counts']].set_index('Mode').subtract(BS_TS_df)
    diff_DS_df = temp_Contribs[['Mode','distance_km']].set_index('Mode').subtract(BS_DS_df)


    temp_df = pd.DataFrame({'counts': df['counts'].tolist()}, index=df['Mode'].tolist())
    temp_Contribs = pd.DataFrame({'distance_km': Contribs['distance_km'].tolist()}, index=Contribs['Mode'].tolist())

    TS_diff_perc = 100*diff_TS_df.loc[diff_TS_df.index, ['counts']] / temp_df.loc[temp_df.index, ['counts']]
    DS_diff_perc = 100*diff_DS_df.loc[diff_DS_df.index, ['distance_km']] / temp_Contribs.loc[temp_Contribs.index, ['distance_km']]

    y_diff = [Total_CO2_remote-baseline_scenario['Total_CO2_remote'], Total_CO2_cowork-baseline_scenario['Total_CO2_cowork'], Total_CO2-baseline_scenario['Total_CO2']]
    totals = [baseline_scenario['Total_CO2_remote']+1, baseline_scenario['Total_CO2_cowork']+1, baseline_scenario['Total_CO2']]
    y_perc = [100*i / j for i, j in zip(y_diff, totals)]
    colors = ['#f1948a' if x > 0 else '#abebc6' for x in y_diff]
    fig2 = go.Bar(
                y=y_perc[:2],
                x=['Remote','Coworking'],
                marker_color=colors[:2])
    fig22 = go.Bar(
                y=[y_perc[2]],
                x=['Total'],                
                marker_color=colors[2])

    fig3 = go.Bar(
                y=TS_diff_perc['counts'],
                x=df['Mode'],
                marker_color=df['color'])

    fig4 = go.Bar(
                y=DS_diff_perc['distance_km'],
                x=Contribs['Mode'],
                marker_color=Contribs['color'])


    row_titles = ("Interventions","CO2 emissions difference WRT baseline (%)","Transport share difference WRT baseline (%)", "Distance share difference WRT baseline (%)")

    fig_comp = make_subplots(rows=4, cols=1, 
                        specs=[[{"type": "scatterpolar"}], 
                               [{"secondary_y": True}],
                               [{"type": "bar"}],
                               [{"type": "bar"}]],
                        row_heights=[2,1,1,1],
                        subplot_titles=row_titles
                        ) #-> row height is used to re-size plots of specific rows
    #fig.for_each_annotation(lambda a:  a.update(y = 1.05) if a.text in column_titles else a.update(x = -0.07) if a.text in row_titles else())
    fig_comp.for_each_annotation(lambda a:  a.update(x = 0.5) if a.text in row_titles else())
    fig_comp.add_trace(fig1, 1, 1)
    fig_comp.add_trace(fig2, 2, 1, secondary_y=False)
    fig_comp.add_trace(fig22, 2, 1, secondary_y=True)
    fig_comp.add_trace(fig3, 3, 1)
    fig_comp.add_trace(fig4, 4, 1)
    fig_comp.update_annotations(font_size=18)
    fig_comp.update_layout(showlegend=False)    
    fig_comp.update_layout(polar=dict(radialaxis=dict(visible=False)))
    fig_comp.update_polars(radialaxis=dict(range=[0, radius_max]))
    fig_comp.update_layout(title_text='Calculated scenario')
    fig_comp.update_yaxes(secondary_y=False, title_text="Remote, Coworking", row=2, col=1)  
    fig_comp.update_yaxes(secondary_y=True, title_text="Total", row=2, col=1)      
    fig_comp.update_xaxes(categoryorder='array', categoryarray= ['Walk','PT','Car'], row=3, col=1)
    fig_comp.update_xaxes(categoryorder='array', categoryarray= ['Walk','PT','Car'], row=4, col=1)


    indicators_n = html.Div(
            [              
            dcc.Graph(
                figure=fig_comp,
                style={'width': '60vh', 'height': '100vh'}) 
            ]
            )

    return [Tab3 + [dbc.Col(indicators_n, width='auto')], new_stored_scenarios]


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



# Output('internal-value_scenario','data',allow_duplicate=True),
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
           Output('internal-value_coworking_days_1', 'data',allow_duplicate=True)
          ],
          Input('choose_coworking_days_1','value'),
          prevent_initial_call=True)
def update_coworking(cow_days):
    return [cow_days]

"""
@callback([Output('CO2_gauge_1', 'value',allow_duplicate=True),
           Output('Transport_share','figure',allow_duplicate=True),
           Output('Km_share','figure',allow_duplicate=True),
"""
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
          State('internal-value_route_opt_done_1','data'),
          State('internal-value_stops_1','data'),
          State('internal-value_coworking_1','data'),
          State('internal-value_coworking_days_1','data'),
          State('internal-value_bus_number_1','data'),
          State('choose_transp_hour_1','value'),
          State('choose_gas_km_car_1','value'),
          State('choose_gas_km_bus_1','value'),
          State('choose_CO2_lt_1','value'),
          State('Tab_3', 'children')
          ],
          [Input('run_baseline_1','n_clicks'),
           Input('run_MCM_1', 'n_clicks')],
          prevent_initial_call=True)
def run_MCM_callback(root_dir, workerData, stored_scenarios, NremDays, NremWork, RouteOptDone, StopsCoords, CowoFlags, CowDays, Nbuses, TransH, gkm_car, gkm_bus, co2lt, Tab3, Nclicks_base, Nclicks):
    print('Cow. Flags:')
    print(CowoFlags)
    CowoIn = np.nonzero(CowoFlags)[0]
    print('Indices:')
    print(CowoIn)
    print('All coords:')
    print(StopsCoords)
    CowoCoords = np.array(StopsCoords)[CowoIn]
    print('Cow coords:')
    print(CowoCoords)
    
    df = pd.DataFrame.from_dict(workerData)    
    result = run_MCM(df, root_dir, TransH, RouteOptDone, gkm_car, gkm_bus, co2lt, NremDays, NremWork, CowoCoords, CowDays)     
    out = plot_result(result, NremDays, NremWork, CowDays, Nbuses, stored_scenarios, StopsCoords, CowoFlags)

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

    #return [fig_total, fig_decomp, new_map, Tab3 + [dbc.Col(indicators_n, width='auto')]]
    #return [out[0], out[1], out[2], out[0], Tab3 + [dbc.Col(indicators_n, width='auto')], scenario_json, new_stored_scenarios]
    return [out[0], out[1], out[2], out[3], Tab3 + [dbc.Col(indicators_n, width='auto')], scenario_json, out[4]]
    #      fig_total, fig_comp, fig_decomp, new_map, new_stored_scenarios

@callback([
           Output('map_1','children',allow_duplicate=True)],
           State('internal-value_scenario_1','data'),
           Input('lc_1', "baseLayer"),
           prevent_initial_call=True)
def switch_layer(Scen, layer):

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
                    html.Span('Remote and coworking', style={'color': 'blue', 'font-size': '14px', 'font-weight': 'bold'})
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
                            'backgroundColor': '#cb4335',
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
                color = generate_color_gradient(maxCO2,i_pred.CO2, i_pred.Mode)
                if i_pred.Mode == 'PT':
                    print('maxCO2: ',maxCO2)
                    print('CO2: ',i_pred.CO2)
                text = 'CO2: ' + '{0:.2f}'.format(i_pred.CO2) + ' Kg ' + '(' + i_pred.Mode + ')' + '<br>' +  'Weekly distance: ' + '{0:.2f}'.format(i_pred.distance_week/1000) + ' Km'

            elif layer == "CO2/CO2_target":
                #maxCO2 = scen_df.groupby("Mode")['CO2_over_aver'].max()[i_pred.Mode]
                #color = generate_color_gradient(maxCO2,i_pred.CO2_over_aver, i_pred.Mode)
                color = generate_color_gradient(1,i_pred.CO2_over_target, i_pred.Mode)  
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
                colors = generate_colors(len(family_types))
                color = colors[i_pred.Tipo_familia-1]
                if i_pred.Tipo_familia in range(3) and i_pred.Mode == 'Car':
                    color = '#C0392B'
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
                        icon=create_diamond_marker(color, (0, 0, 0))
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
                            icon=create_square_marker(color, (0, 0, 0))
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
                            icon=create_triangle_marker(color, (0, 0, 0))
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
          State('choose_transp_hour_1','value'),
          State('choose_gas_km_car_1','value'),
          State('choose_gas_km_bus_1','value'),
          State('choose_CO2_lt_1','value')],
          Input('button_download_scenario_1', 'n_clicks'),
          prevent_initial_call=True)
def download_inputs(NremDays, NremWork, CowDays, Nbuses, TransH, gkm_car, gkm_bus, co2lt, Nclicks):
    inputs_dict = {'NremDays': NremDays, 'NremWork':NremWork, 
                   'CowDays': CowDays,                    
                   'Nbuses': Nbuses,
                   'TransH': TransH, 'gkm_car': gkm_car, 
                   'gkm_bus': gkm_bus, 'co2lt': co2lt
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
            State('upload-data_1', 'last_modified')],
              prevent_initial_call=True)
def load_worker_data(list_of_contents, list_of_names, list_of_dates):       
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        works_data = children[0]
        #temp_file = root_dir + 'data/' + 'temp_workers_data.csv'
        #df = pd.read_csv(temp_file) 
        #suggested_N_clusters = suggest_clusters(df)
        suggested_N_clusters = suggest_clusters(works_data)
        #print('workers dataframe?', works_data)
        workers = pd.DataFrame(works_data.drop(columns='geometry'))
        workers_dict = workers.to_dict('records') 
        
        return [workers_dict,suggested_N_clusters]
############################################################################################

#           Output('internal-value_stops','data',allow_duplicate=True),
       
@callback([Output('Indicator_panel_1', 'figure',allow_duplicate=True),
           Output('graph2','figure',allow_duplicate=True),
           Output('Indicator_panel_3', 'figure',allow_duplicate=True),
           Output('map_1','children',allow_duplicate=True),
           Output('internal-value_remote_days_1', 'data',allow_duplicate=True),
           Output('internal-value_remote_workers_1', 'data',allow_duplicate=True),
           Output('internal-value_coworking_days_1', 'data',allow_duplicate=True),
           Output('internal-value_bus_number_1', 'data',allow_duplicate=True),
           Output('choose_transp_hour_1', 'value',allow_duplicate=True),
           Output('choose_gas_km_car_1', 'value',allow_duplicate=True),
           Output('choose_gas_km_bus_1', 'value',allow_duplicate=True),
           Output('choose_CO2_lt_1', 'value',allow_duplicate=True),
           Output('internal-value_stops_1', 'data',allow_duplicate=True),
           Output('internal-value_coworking_1', 'data',allow_duplicate=True),
           Output('internal-value_scenario_1','data',allow_duplicate=True)],
           [Input('button_load_scenario_1', 'contents'),
            State('button_load_scenario_1', 'filename'),
            State('button_load_scenario_1', 'last_modified')],
            prevent_initial_call=True)
def load_scenario(contents, names, dates):
    if contents is None:
        #return [dash.no_update]*14
        return []

    print('inside callback!')
    inputs = [parse_contents_load_scenario(c, n, d) for c, n, d in zip(contents, names, dates)
              if 'inputs' in n]
    stops_cow_hubs = [parse_contents_load_scenario(c, n, d) for c, n, d in zip(contents, names, dates)
                      if 'StopsCowHubs' in n]
    scenario = [parse_contents_load_scenario(c, n, d) for c, n, d in zip(contents, names, dates)
                if 'scenario' in n]

    inputs = np.array(inputs[0][:])[0]
    NremDays = inputs[0] 
    NremWork = inputs[1]
    CowDays = inputs[2]
    Nbuses = inputs[3] 
    try:   
        stops_cow_hubs = np.array(stops_cow_hubs[0][:])[:]
        lats = stops_cow_hubs[:, 0]
        lons = stops_cow_hubs[:, 1]
        cow_flags = stops_cow_hubs[:, 2]
        stops_coords = list(zip(lats, lons))
    except:
        stops_coords = []
        cow_flags = []

    print()
    print('loaded scenario:')
    print(scenario)
    col_names = scenario[0][:][1].tolist() 
    print(len(col_names))
    scenario = np.array(scenario[0][:][0])
    scenario = pd.DataFrame(scenario)
    print(len(scenario.columns))
    print(col_names)
    scenario.columns = col_names

    scenario = geopandas.GeoDataFrame(scenario)  
    print(scenario.columns.tolist())     

    print(scenario['CO2_worst_case'].sum())
    print(scenario['CO2_worst_case'].head(20))    
    out = plot_result(scenario, NremDays, NremWork, CowDays, Nbuses, stops_coords, cow_flags)

    scenario = pd.DataFrame(scenario.drop(columns='geometry'))
    scenario_json = scenario.to_dict('records') # not working?
    #return [out[0],out[1],out[2],out[3], out[4], scenario_json]
    #return [out[0],out[2], *inputs, scenario_json]
    #fig_total, fig_decomp, new_map
    return [out[0],out[1],out[0],out[2], *inputs, stops_coords, cow_flags, scenario_json]


#           Output('internal-value_stops','data',allow_duplicate=True),


#@app.callback([Output("clickdata", "children")],
#Output("outdata", "children", allow_duplicate=True),
@app.callback([Output('internal-value_stops_1','data',allow_duplicate=True),
               Output('internal-value_coworking_1','data',allow_duplicate=True),
               Output('map_1','children',allow_duplicate=True)],
              State("n_clusters_1", "value"),
              State('worker_data_1', 'data'),
              State('root_dir_1','data'),
              Input("propose_stops_1", "n_clicks"),
              prevent_initial_call=True
              )
def propose_stops(n_clusters,workerData, root_dir, Nclick):
    if Nclick > 0:  
        sys.path.append(root_dir + 'modules')      
        import find_stops_module   
        n_clusters  = int(n_clusters)
        cutoff = 0.8 # cutoff for maximum density: take maxima which are at least cutoff*max  
        workers_DF = pd.DataFrame.from_dict(workerData)
        stops_DF = pd.read_csv(root_dir + 'data/'+ "all_bus_stops.csv", encoding='latin-1')
        bus_stops_df,model,yhat = find_stops_module.FindStops(workers_DF, stops_DF, n_clusters, cutoff)
        #df = pd.read_csv(filename)
        #out=St.loc[:'Lat']
        #for i in range(len(St)):
        #    out = out + str(St.loc[i,['Lat']]) + ', ' + str(St.loc[i,['Lon']]) + '; '
        out = ''
        St = []
        Cow = []
        for ind in bus_stops_df.index:
            out = out + str(bus_stops_df['Lat'][ind]) + ',' + str(bus_stops_df['Lon'][ind]) +';'
            St.append((bus_stops_df['Lat'][ind],bus_stops_df['Lon'][ind]))
            Cow.append(0)
        markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
        newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                        center=center, zoom=12, id="map_1",
                        style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
        #return [out,St,newMap]
        #return [out,St,Cow,newMap]
        return [St,Cow,newMap]    

@app.callback([Output('map_1','children',allow_duplicate=True)],
                State("n_clusters_1", "value"),
                State('worker_data_1', 'data'),
               [Input("show_workers_1", "n_clicks")],
              prevent_initial_call=True
              )
def show_workers(n_clusters,workerData, N):
    workers_DF = pd.DataFrame.from_dict(workerData)
    """
    St = []
    for ind in workers_DF.index:
         St.append((workers_DF['O_lat'][ind],workers_DF['O_long'][ind]))
    markers = [dl.Marker(dl.Tooltip("Do something?"), position=pos, icon=custom_icon_worker, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
    newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
    """ 
    clusters = drawclusters(workers_DF,n_clusters)
    n_max = max(len(x) for x in clusters ) # find maximum size of the clusters
    n_min = min(len(x) for x in clusters ) # find maximum size of the clusters
    #colors = generate_colors(n_clusters)
    n_colors = n_max
    #n_colors = 255
    colors = [generate_color_gradient(n_max, len(clusters[i])) for i in range(len(clusters))]
    #colors = [generate_color_gradient(n_max, len(clusters[i])) for i in range(len(clusters))]
    cluster_shapes = [dl.Polygon(children = dl.Tooltip('Number of workers: '+str(len(clusters[i]))), positions=clusters[i], fill=True, fillColor = colors[i], fillOpacity=0.9) for i in range(n_clusters)]
    newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + cluster_shapes,
                     center=center, zoom=12, id="map_1",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})

    return [newMap]


@app.callback([Output('sidebar_intervention_1','children',allow_duplicate=True)],
              State('internal-value_stops_1','data'),
              State('internal-value_coworking_1','data'),
              State('internal-value_coworking_days_1','data'),        
              State('internal-value_remote_days_1', 'data'),
              State('internal-value_remote_workers_1', 'data'),
              State('internal-value_bus_number_1', 'data'),
              State('internal-value_calculated_scenarios_1', 'data'),
              Input('choose_intervention_1',"value"),
              prevent_initial_call=True
              )
def choose_intervention(St,Cow,CowDays, RemDays, RemWorkers, Nbuses, stored_scenarios, interv):
    print('chosen interv.: ', interv)
           
    if interv == 'CT':
        sidebar_transport = html.Div(
            [           
            dbc.Button("Propose stops", id="propose_stops_1", n_clicks=0,style={"margin-top": "15px","font-weight": "bold"}),
            #html.Br(),
            dbc.Popover(dcc.Markdown(mouse_over_mess_stops, dangerously_allow_html=True),
                      target="propose_stops_1",
                      body=True,
                      trigger="hover",style = {'font-size': 12, 'line-height':'2px'}),


            dbc.Button("Match stops", id="match_stops_1", n_clicks=0, style={"margin-top": "15px", "font-weight": "bold"}),
            dbc.Popover(dcc.Markdown(mouse_over_mess, dangerously_allow_html=True),
                      target="match_stops_1",
                      body=True,
                      trigger="hover",style = {'font-size': 12, 'line-height':'2px'}),
            #html.P([ html.Br(),'Choose number of buses'],id='bus_num_1',style={"margin-top": "15px","font-weight": "bold"}),
            html.P(['Choose number of buses'],id='bus_num_1',style={"margin-top": "15px","font-weight": "bold"}),
            #dcc.Input(id="choose_buses", type="text", value='3'),
            dcc.Slider(0, 10, 1,
                   value=Nbuses,
                   id='choose_buses_1'
            ),
            dbc.Button("Calculate routes", id="calc_routes_1",n_clicks=0, style={"margin-top": "15px"}),
            #html.P([ html.Br(),'Select route to visualize'],id='route_select_1',style={"margin-top": "15px", "font-weight": "bold"}),
            html.P(['Select route to visualize'],id='route_select_1',style={"margin-top": "15px", "font-weight": "bold"}),
            dcc.Dropdown(routes, multi=False,style={"margin-top": "15px"},id='choose_route_1'),
            dbc.Button("Visualize routes", id="visualize_routes_1", n_clicks=0,style={"margin-top": "15px"}),
            #html.Br(),               
            html.Div(id='outdata_1', style={"margin-top": "15px"}),
            dcc.Store(id='internal-value_stops_1', data=St),
            dcc.Store(id='internal-value_coworking_1', data=Cow),
            dcc.Store(id='internal-value_coworking_days_1', data=CowDays),
            dcc.Store(id='internal-value_remote_days_1', data=RemDays),
            dcc.Store(id='internal-value_remote_workers_1', data=RemWorkers),
            dcc.Store(id='internal-value_bus_number_1', data=Nbuses),
            dcc.Store(id='internal-value_routes_1', data=[]),        
            dcc.Store(id='internal-value_scenario_1', data=[]),        
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
                dcc.Store(id='internal-value_bus_number_1', data=Nbuses),
                dcc.Store(id='internal-value_routes_1', data=[]),        
                dcc.Store(id='internal-value_scenario_1', data=[]),        
                dcc.Store(id='internal-value_calculated_scenarios_1', data=stored_scenarios)
                ])        
        return [sidebar_remote_work]

    if interv == 'CW':         
        
        sidebar_cowork = html.Div(
                [
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
                dcc.Store(id='internal-value_bus_number_1', data=Nbuses),
                dcc.Store(id='internal-value_routes_1', data=[]),        
                dcc.Store(id='internal-value_scenario_1', data=[]),        
                dcc.Store(id='internal-value_calculated_scenarios_1', data=stored_scenarios)
                ])   
        return [sidebar_cowork]



@app.long_callback([Output("outdata_1", "children",allow_duplicate=True),
               Output("internal-value_route_opt_done_1", 'data',allow_duplicate=True),
               Output('internal-value_routes_1','data',allow_duplicate=True),
               Output('internal-value_bus_number_1','data',allow_duplicate=True),
               Output("choose_route_1", "options",allow_duplicate=True),
               Output('map_1','children',allow_duplicate=True)],
               State('choose_buses_1',"value"),
               State('internal-value_stops_1','data'),
               State('internal-value_coworking_1','data'),
               State('choose_CO2_lt_1','value'),
               State('root_dir_1','data'),
               Input("calc_routes_1", "n_clicks"),
               manager=long_callback_manager,
              prevent_initial_call=True
              )
def calc_routes(Nroutes,St,Cow,CO2km, root_Dir, Nclick):
    print()
    print('inside calc_routes!')
    if Nclick > 0:
      root_dir = root_Dir
      sys.path.append(root_dir + 'modules')
      print()
      print('Cleaning folders...')
      shutil.rmtree(root_dir + 'data/input_data_MCM/GTFS_feeds')
      shutil.rmtree(root_dir + 'data/input_data_MCM/transit_together_24h')
      shutil.copytree(root_dir + 'data/input_data_MCM/GTFS_feeds_backup', root_dir + 'data/input_data_MCM/GTFS_feeds')
      shutil.copytree(root_dir + 'data/input_data_MCM/transit_together_24h_backup', root_dir + 'data/input_data_MCM/transit_together_24h')
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
    
      center = (43.26852347667122, -1.9741372404905988)
    
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
      routes, routes_points_coords, Graph = calcroutes_module.CalcRoutes_module(Stops,int(Nroutes),float(CO2km))
      print('Routes calculated!')
      #print(routes_points_coords)
      gGTFS.gGTFS(routes, Stops, Graph, root_dir)
      route_opt = 1
      # We don't really need to update the map here. We do it just to make the Spinner work: ############ 
      #markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(Stops)]
      newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map_1",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"}) 
      ###################################################################################################   
      #return ["Calculation completed!", routes_coords, new_menu, newMap]
      return ["Calculation completed for: "+str(len(Stops)), route_opt, routes_points_coords, Nroutes, new_menu, newMap]


@app.callback([Output('map_1','children',allow_duplicate=True)],
              [State('choose_route_1',"value"),
              State('internal-value_stops_1','data'),
              State('internal-value_coworking_1','data'),
              State('internal-value_routes_1','data')],
              [Input("visualize_routes_1", "n_clicks")],
              prevent_initial_call=True
              )
def visualize_route(Route,St,Cow,RoutesCoords,Nclick):
    if Nclick > 0:
      print('Start route visualization...')
      #Route = int(Route.split(' ')[1])-1
      Route = int(Route)-1    
      RoutesCoords = RoutesCoords[Route]
      markers = []
      for i, pos in enumerate(St): 
        if Cow[i]==1:
             custom_icon = custom_icon_coworking
        else:
             custom_icon = custom_icon_bus
        tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
        markers.append(tmp)     
      #markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(Stops)]
      newMap = dl.Map([dl.TileLayer(), dl.ScaleControl(position="topright"), dl.Polyline(positions=RoutesCoords, pathOptions={'weight':10})] + markers,
                     center=center, zoom=12, id="map_1",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
      return [newMap]


@app.callback([Output("outdata_1", "children",allow_duplicate=True), 
               Output('internal-value_stops_1','data',allow_duplicate=True),
               Output('map_1','children',allow_duplicate=True)],
              [State('internal-value_stops_1','data'),
               State('internal-value_coworking_1','data')],
              Input("match_stops_1", "n_clicks"),
              prevent_initial_call=True
              )
def match_stops(St,Cow,Nclick):
    print('inside callback')
    if Nclick > 0:
      print('inside if...')
      print('matching stops...')  
      bus_stops = []
      out = ''
      for i_st in range(len(St)):
        if Cow[i_st] == 0:  
          #ref = np.array([lat,lon])
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
      newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map_1",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
      return [len(St),St,newMap]

#              [Input('map_1','clickData')],
@app.callback([Output("outdata_1", "children",allow_duplicate=True), 
               Output('internal-value_stops_1','data',allow_duplicate=True),
               Output('internal-value_coworking_1','data',allow_duplicate=True),
               Output('map_1','children',allow_duplicate=True)],
              [State('internal-value_stops_1','data'),
               State('internal-value_coworking_1','data')],
              [Input('map_1','dblclickData')],
              prevent_initial_call=True
              )
def add_marker(St,Cow,clickd):
       print('adding marker...')
       print(clickd)
       marker_lat = clickd['latlng']['lat']
       marker_lon = clickd['latlng']['lng']
       St.append((marker_lat,marker_lon))
       Cow.append(0)
       out=''
       for i in range(len(St)):
           out = out + str(St[i][0]) + ', ' + str(St[i][1]) + '; '
       markers = []
       for i, pos in enumerate(St): 
           if Cow[i] == 1:
               custom_icon = custom_icon_coworking
               #print('setting coworking icon...')
           else:
               custom_icon = custom_icon_bus
           tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
           markers.append(tmp)    

       newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map_1",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
       return [out,St,Cow,newMap]


@app.callback([Output("outdata_1", "children",allow_duplicate=True),
               Output('internal-value_stops_1','data',allow_duplicate=True),
               Output('internal-value_coworking_1','data',allow_duplicate=True),
               Output("choose_stop_action_1", "value",allow_duplicate=True),
               Output('map_1','children',allow_duplicate=True)],
              [State('internal-value_stops_1','data'), 
               State('internal-value_coworking_1','data'), 
               State('choose_stop_action_1',"value")],
              [Input({"type": "marker", "index": ALL},"n_clicks")],
              prevent_initial_call=True)
def change_marker(St, Cow, stop_operation, *args):

    marker_id = callback_context.triggered[0]["prop_id"].split(".")[0].split(":")[1].split(",")[0]
    n_clicks = callback_context.triggered[0]["value"]

    print('changing marker...')
    #print('marker id?:', marker_id)
    print('requested Marker Operation:')
    print(stop_operation)
    
    if stop_operation == "DM":      
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
        newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                        center=center, zoom=12, id="map_1",
                        style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
        #markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
        #newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
        #              center=center, zoom=12, id="map",
        #              style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
        return ['Stop deleted!',St,Cow,' ',newMap]

    if stop_operation == "SO":
        print()
        print()
        tmp = St[int(marker_id)]
        St.pop(int(marker_id))
        Cow.pop(int(marker_id))
        St.insert(0, tmp)
        Cow.insert(0, 0)
        print('list modified!')
        print()
        
        markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
        newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map_1",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
        return ['Origin set!',St,Cow,' ',newMap]
        
    if stop_operation == "SC":
       markers = []
       for i, pos in enumerate(St): 
           if i == int(marker_id) or Cow[i]==1:
               custom_icon = custom_icon_coworking
               Cow[i] = 1               
           else:
               custom_icon = custom_icon_bus
           tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
           markers.append(tmp)    
       newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map_1",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
       return ['Stop deleted!',St,Cow,' ',newMap]



if __name__ == '__main__':
    #app.run(debug=True,port=80)
    #app.run_server(debug=True, dev_tools_hot_reload=False, use_reloader=False, host='0.0.0.0', port=80)
    #app.run_server(debug=True, use_reloader=False, host='0.0.0.0', port=80)
    app.run_server(use_reloader=False, host='0.0.0.0', port=80)
