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

import time
import getpass

from dash.long_callback import DiskcacheLongCallbackManager
## Diskcache
import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

#root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
#root_dir = '/home/cslgipuzkoa/virtual_machine_disk/UI_SCP/assets/'
root_dir = 'C:/Users/gfotidellaf/repositories/test_UI_SCP/app/'

sys.path.append(root_dir + 'callbacks')
sys.path.append(root_dir + 'layout')

print('Code restarted!')

server = Flask(__name__)

app = Dash(name = 'SCP_app', server = server, url_base_pathname='/dash/',
           external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc.icons.BOOTSTRAP],prevent_initial_callbacks=False,suppress_callback_exceptions = True)


from callbacks import register_callbacks
import layout

app.layout = layout.layout

register_callbacks(app)

# Define the login route

@server.route('/reports/<path:path>')
def serve_static(filename):
    #return send_from_directory('static', filename)
    return send_from_directory(root_dir + 'assets/images/login', filename)


MCM_data_dir = 'assets/data/input_data_MCM/'
with open(root_dir + MCM_data_dir + "user_data.csv") as f:
       r = csv.reader(f)
       user_data = [row for row in r]

@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Perform login authentication
        username = request.form['username']
        password = request.form['password']

        # Add your authentication logic here
        correct_login = 0
        for name, pw in user_data:
            if username == name and password == pw:
                DateTime = datetime.datetime.now()
                DateTime = DateTime.strftime("%m/%d/%Y_%H:%M:%S")
                print('writing login info into file...')
                f=open(root_dir + 'assets/data' + '/' + 'login_data.txt','a+')
                f.write(username + ' ')
                f.write(password + ' ')
                f.write(DateTime + '\n')
                f.close()
                correct_login = 1
                return app.index()

        if correct_login == 0:
            return 'Invalid username or password'

    # If the request method is GET, render the login template
    return render_template('login.html')

@server.route("/test1", endpoint='webpage1')
#@exception_handler
def webpage1():
    print('trying to serve page 1')
    #return render_template(path + "/Nere_webpage/index.html")
    return render_template("index1.html")

@server.route("/test2", endpoint='webpage2')
def webpage2():
    print('trying to serve page 2')
    #return render_template(path + "/Nere_webpage_copy/index.html")
    return render_template("index2.html")

if __name__ == '__main__':
    server.run(debug=True, use_reloader=False, host='0.0.0.0', port=80)