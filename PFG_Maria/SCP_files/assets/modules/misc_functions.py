## #!/home/cslgipuzkoa/virtual_machine_disk/anaconda3/envs/SCP_test/bin/python
import dash
from dash import Dash
import dash_bootstrap_components as dbc
import dash_loading_spinners as dls
from dash import html, callback_context, ALL
from dash import dcc, Output, Input, State, callback, dash_table

from dash_extensions.snippets import send_data_frame

import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_daq as daq
import dash_html_components as html

from flask import Flask, render_template, request, send_from_directory

# plot test data
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import base64
import io

#import re
import json
import pandas as pd
import numpy as np
import geopandas

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, adjusted_rand_score

from pylab import cm
import matplotlib

from os import listdir


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
class MiscFunctions:
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
        points_per_cluster = []
        for i in range(n_clusters):
            points = workers_lat_lon[model.labels_ == i]
            hull = ConvexHull(points)
            vert = np.append(hull.vertices, hull.vertices[0])  # close the polygon by appending the first point at the end
            clusters_poly.append(points[vert])
            points_per_cluster.append(len(points))
        return clusters_poly, points_per_cluster

    def suggest_clusters(wdf, startHour):
        #sil_score_max = -100 #this is the minimum possible score
        dist_max = 100
        try:
            # select specific hour #####################################################
            wdf['Hora_Ini_E'] = wdf['Hora_Ini'].copy()
            wdf['Hora_Ini'] = pd.to_datetime(wdf['Hora_Ini_E'], format='%H:%M')
            wdf['Hora_Ini_E'] = ((wdf['Hora_Ini'] - pd.to_datetime('00:00', format='%H:%M')).dt.total_seconds() / 300).astype(int) + 1
            wdf['Hora_Ini'] = wdf['Hora_Ini'].dt.strftime('%H:%M')
            convertido=((startHour*60*60)/300)+1
            # Get 1-hour interval between "convertido" and "convertido+1hour"? #######
            wdf=wdf[wdf['Hora_Ini_E'] <= (convertido+11)]
            wdf=wdf[wdf['Hora_Ini_E'] >= convertido]
            ############################################################################
        except:
            pass
        wdf = wdf[['O_lat', 'O_long']].values.tolist()
        """
        #alpha = 0.65
        alpha = 0.75    
        #n_max_clusters = int(19.*len(wdf)/2507)
        n_max_clusters = 30 
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
            print(d0,d1)
            print("The average silhouette and db score for %i clusters are %0.2f; the average score is %0.2f" %(n_clusters,sil_score, dist_to_max))
            #if sil_score > sil_score_max:
            if dist_to_max < dist_max:   
            dist_max = dist_to_max
            best_n_clusters = n_clusters
        """
        best_n_clusters = min(18, int(len(wdf)*0.05))
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
            """
            ranges = [
                {"start": "2ECC71", "end": "F4D03F"},
                {"start": "F4D03F", "end": "C0392B"}
            ]
            """
            ranges = [
                {"start": "ABEBC6", "end": "2ECC71"},
                {"start": "FCF3CF", "end": "F1C40F"},
                {"start": "f1948a", "end": "E74C3C"}
            ]
            
            color_start_hex = ranges[0]["start"]
            color_end_hex = ranges[0]["end"]
            color_start_rgb = MiscFunctions.hex_to_rgb(color_start_hex)
            color_end_rgb = MiscFunctions.hex_to_rgb(color_end_hex)
            # Generate gradient
            #gradient1 = [interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 256)]
            #gradient1 = [interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 32)]
            gradient1 = [MiscFunctions.interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 4)]
            
            color_start_hex = ranges[1]["start"]
            color_end_hex = ranges[1]["end"]
            color_start_rgb = MiscFunctions.hex_to_rgb(color_start_hex)
            color_end_rgb = MiscFunctions.hex_to_rgb(color_end_hex)
            # Generate gradient
            #gradient2 = [interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 256)]
            gradient2 = [MiscFunctions.interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 4)]

            color_start_hex = ranges[2]["start"]
            color_end_hex = ranges[2]["end"]
            color_start_rgb = MiscFunctions.hex_to_rgb(color_start_hex)
            color_end_rgb = MiscFunctions.hex_to_rgb(color_end_hex)
            # Generate gradient
            #gradient3 = [interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 256)]
            gradient3 = [MiscFunctions.interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 4)]

            gradient = gradient1 + gradient2 +  gradient3
            #gradient = gradient1 + gradient2 


        elif label== 'Car':
            ranges = [
                {"start": "F1948A", "end": "B03A2E"}
            ]
            color_start_hex = ranges[0]["start"]
            color_end_hex = ranges[0]["end"]
            color_start_rgb = MiscFunctions.hex_to_rgb(color_start_hex)
            color_end_rgb = MiscFunctions.hex_to_rgb(color_end_hex)
            # Generate gradient
            gradient = [MiscFunctions.interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 256)]
        
        elif label== 'PT':
            ranges = [
                {"start": "D6EAF8", "end": "21618C"}
            ]
            color_start_hex = ranges[0]["start"]
            color_end_hex = ranges[0]["end"]
            color_start_rgb = MiscFunctions.hex_to_rgb(color_start_hex)
            color_end_rgb = MiscFunctions.hex_to_rgb(color_end_hex)
            # Generate gradient
            gradient = [MiscFunctions.interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 256)]    

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
        square_icon = MiscFunctions.create_square_icon(color, border_color)
        return dict(type="custom", iconUrl=square_icon)


    def create_square_icon_2(color1, color2, border_color):
        import base64
        import io
        from PIL import Image, ImageDraw, ImageOps  
        # Create a square shape
        square_size = 20

        # Create a blank image
        image = Image.new('RGBA', (square_size, square_size), color=(0, 0, 0, 0))

        # Draw the square shape on the image
        draw = ImageDraw.Draw(image)
        draw.rectangle([(0, 0), (square_size // 2, square_size)], fill=color1)
        draw.rectangle([(square_size // 2, 0), (square_size, square_size)], fill=color2)

        # Add a black border to the square
        border_size = 2
        border_image = ImageOps.expand(image, border=border_size, fill=border_color)

        # Convert the image to base64
        buffered = io.BytesIO()
        border_image.save(buffered, format="PNG")
        base64_icon = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return "data:image/png;base64," + base64_icon

    def create_square_marker_2(color1, color2, border_color):
        square_icon = MiscFunctions.create_square_icon_2(color1, color2, border_color)
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
        diamond_icon = MiscFunctions.create_diamond_icon(color, border_color)
        return dict(type="custom", iconUrl=diamond_icon)

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
        triangle_icon = MiscFunctions.create_triangle_icon(color, border_color)
        return dict(type="custom", iconUrl=triangle_icon)


    def generate_map(result, CowFlags, StopsCoords, additional_markers=[]):

        print('generating map...')
        #Total_CO2 = result['CO2'].sum()
        #Total_CO2_worst_case = result['CO2_worst_case'].sum()
        markers_all_1 = []
        markers_remote_1 = []
        markers_cow_1 = []
        markers_remote_cow_1 = []
        markers_comm_1 = []

        custom_icon_coworking = dict(
            iconUrl= coworking_icon,
            iconSize=[40,40],
            iconAnchor=[22, 40]
        )    
    
        for i_pred in result.itertuples():
            #print(i_pred.geometry.y, i_pred.geometry.x)
            #color = generate_color_gradient(maxCO2,i_pred.CO2) 
            #color = generate_color_gradient(i_pred.CO2_worst_case,i_pred.CO2) 
            #maxCO2 = result.groupby("Mode")['CO2'].max()[i_pred.Mode]
            maxCO2 = result.loc[:, 'CO2_worst_case'].mean()
            color = MiscFunctions.generate_color_gradient(maxCO2,i_pred.CO2, i_pred.Mode) 
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
                        icon= MiscFunctions.create_diamond_marker(color, (0, 0, 0))
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

                    text = 'CO2: ' + '{0:.2f}'.format(i_pred.CO2) + ' Kg ' + '(' + i_pred.Mode_base + ' and ' + i_pred.Mode + ')' 
                    text = text + '<br>' +  'Weekly distance: ' + '{0:.2f}'.format(i_pred.distance_week/1000) + ' Km'
                    #text = text + '<br>' + 'Remote working: ' + str(i_pred.Rem_work)
                    n_rw = int(i_pred.Rem_work)
                    text = text + '<br>' + 'Remote working: ' + (['Yes']*n_rw + ['No'])[n_rw-1] 
                    try:
                        n_cw = int(i_pred.Coworking)
                    except:
                        n_cw = 0    
                    text = text + '<br>' + 'Coworking: ' + (['Yes']*n_cw + ['No'])[n_cw-1]

                    color2 = MiscFunctions.generate_color_gradient(maxCO2,i_pred.CO2, i_pred.Mode_base)

                    marker_i = dl.Marker(
                            id=str(i_pred),
                            children=[dl.Tooltip(content=text, offset={"x": 5, "y": 10})],
                            position=[i_pred.geometry.y, i_pred.geometry.x],
                            #icon=create_square_marker(color, (0, 0, 0))
                            icon= MiscFunctions.create_square_marker_2(color2,color, (0, 0, 0))
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
                            icon= MiscFunctions.create_triangle_marker(color, (0, 0, 0))
                    )                     
                    markers_remote_cow_1.append(marker_i)
            #except:
            #    pass 

            markers_all_1.append(marker_i)  

        markers_comm_1 = list(set(markers_all_1) - set(markers_remote_1) - set(markers_cow_1) )
        
        print('markers generated!')

        Legend =  html.Div(
            style={
                'position': 'absolute',
                'bottom': '20px',
                'left': '700px',
                'zIndex': 1000,  # Adjust the z-index as needed
                },
            children=[
                html.Div(
                    style={
                        'display': 'inline-block',
                        'margin-right': '50px'
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
                        'margin-right': '35px'
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
                        'margin-right': '20px',
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
                        html.Span('Remote + Coworking', style={'color': 'blue', 'font-size': '14px', 'font-weight': 'bold'})
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
                    #tmp = dl.Marker(dl.Tooltip("Coworking hub"), position=pos, icon=custom_icon_coworking_big, id={'type': 'marker', 'index': i})    
                    tmp = dl.Marker(dl.Tooltip("Coworking hub"), position=pos, icon=custom_icon_coworking, id={'type': 'marker', 'index': i})    
                    Cow_markers.append(tmp)  
            children = children + Cow_markers

        #Eskuz_marker = [dl.Marker(dl.Tooltip("Eskuzaitzeta Industrial Park"), position=Eskuz_pos, icon=custom_icon_Eskuz, id='Eskuz_1')]
        #IndPark_marker = [dl.Marker(dl.Tooltip("Industrial Park"), position=IndParkCoord, icon=custom_icon_IndPark, id='IndPark_1')]

        children = children + additional_markers

        new_map = dl.Map(children, center=center,
                                        zoom=12,                        
                                        id="map_1",style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
        
        return new_map

    def plot_result(result, NremDays, NremWork, CowDays, NeCar, Nbuses, additional_co2, eCar_co2_km,stored_scenarios, IndParkCoord, StopsCoords=[], CowFlags=[]):

        Nworkers = len(result)

        radius_max = 1
        x0 = NremDays
        x1 = NremWork
        x2 = sum(CowFlags)
        x3 = CowDays
        x4 = Nbuses
        x5 = len(StopsCoords) - sum(CowFlags)
        x6 = NeCar  
        x7 = eCar_co2_km                         
        x0_max = 5
        x1_max = 100
        x2_max = 3
        x3_max = 5
        x4_max = 10
        x5_max = 15
        x6_max = 100
        x7_max = 1

        Total_CO2 = result['CO2'].sum() + additional_co2
        # Correct CO2 calculation 
        
        temp = result.loc[result['Rem_work'] > 0]
        Total_CO2_remote = temp['CO2'].sum() # this will be used later
        temp = result.loc[result['Coworking'] == 1]
        Total_CO2_cowork = temp['CO2'].sum() # this will be used later

        Total_CO2_worst_case = result['CO2_worst_case'].sum() 
        #Total_CO2_worst_case = result['CO2_worst_case'].sum() + additional_co2
        
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
        df0 = pd.DataFrame(data=d)
        df0['Mode'] = df0['Mode'].map({0:'Walk',1:'PT',2:'Car'})
        df0['color'] = df0['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
        fig2 = go.Pie(labels=df0["Mode"],
                        values=df0["counts"],
                        showlegend=False,
                        textposition='inside',
                        textinfo='label+percent',
                        marker=dict(colors=df0['color']))


        headerColor = 'rgb(107, 174, 214)'
        fig3 = go.Table(
                    columnwidth = [40,60],
                    header=dict(
                        values=['<b>ton/week</b>','<b>kg/week/person</b>'],
                        line_color='darkslategray',
                        fill_color=headerColor,
                        align=['center','center'],
                        font=dict(color='white', size=14)
                    ),
                    cells=dict(
                        values=[["{:.3f}".format(Total_CO2/1000.)],["{:.2f}".format(Total_CO2/Nworkers)]],
                        fill_color=['rgb(107, 174, 214)'],
                        line_color='darkslategray',
                        align='center', font=dict(color='black', size=14)
                    ))

        data = {'Number_routes' : [Nbuses], 'Number_stops' : len(StopsCoords) - sum(CowFlags),
                'Coworking_days' : CowDays, 'Coworking_hubs' : sum(CowFlags), 
                'Remote_days' : NremDays, 'Remote_workers' : NremWork, 
                'eCar_co2_km' : eCar_co2_km, 'eCar_adoption' : NeCar}
        df1 = pd.DataFrame(data)
        rowEvenColor = 'rgb(189, 215, 231)'
        rowOddColor = 'rgb(107, 174, 214)'
        fig4 = go.Table(
                    columnwidth = [70,70],
                    cells=dict(
                        values=[["<b>Number of routes</b>:{:.2f}".format(int(df1.Number_routes)),
                                "<b>Coworking hubs</b>:{:.2f}".format(int(df1.Coworking_hubs)),
                                "<b>Remote workers (%)</b>:{:.2f}".format(int(df1.Remote_workers)),
                                "<b>Car electrification (%)</b>:{:.2f}".format(int(df1.eCar_adoption))],
                                ["<b>Number of stops</b>:{:.2f}".format(int(df1.Number_stops)),
                                "<b>Coworking days</b>:{:.2f}".format(int(df1.Coworking_days)),
                                "<b>Remote days</b>:{:.2f}".format(int(df1.Remote_days)),
                                "<b>CO2/km WRT combus.</b>:{:.2f}".format(int(df1.eCar_co2_km))]],
                        fill_color = [[rowOddColor,rowEvenColor,rowOddColor,rowEvenColor,rowOddColor]*2],
                        line_color='darkslategray',
                        align='center', font=dict(color='black', size=14)
                    ))


        temp = result.copy()
        #temp['distance_km'] = temp['distance_week']/1000.
        temp['distance_km'] = temp['distance_week_interv']/1000.
        temp['distance_km_no_interv'] = temp['distance_week_no_interv']/1000.
        temp1 = temp[['Mode','distance_km']]
        temp2 = temp[['Mode_base','distance_km_no_interv']]    
        Contribs1 = temp1.groupby(['Mode']).sum() 
        Contribs1 = Contribs1.reset_index()
        Contribs2 = temp2.groupby(['Mode_base']).sum() 
        Contribs2 = Contribs2.reset_index()
        Contribs2['Mode'] = Contribs2['Mode_base']
        Contribs2['distance_km'] = Contribs2['distance_km_no_interv']
        Contribs2.drop(['Mode_base','distance_km_no_interv'], axis=1, inplace=True)
        Contribs = pd.concat([Contribs1,Contribs2]).groupby(['Mode']).sum().reset_index()
        Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
        print()
        print('Contribs:')  
        print(Contribs)
        fig5 = go.Bar(
                    x=Contribs['distance_km'],
                    y=Contribs['Mode'],
                    orientation='h',
                    marker_color=Contribs['color'])

        fig_total = make_subplots(rows=4, cols=2, 
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

        fig_total.append_trace(fig1, 1, 1)
        fig_total.append_trace(fig2, 1, 2)
        fig_total.append_trace(fig3, 2, 1)
        fig_total.append_trace(fig4, 3, 1) 
        #fig.append_trace(fig41, 5, 1)
        #fig.append_trace(fig42, 6, 1)
        #fig.append_trace(fig43, 7, 1)
        fig_total.append_trace(fig5, 4, 1)



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
                'eCar_adoption': NeCar,
                'eCar_co2_km': eCar_co2_km,
                'StopsCoords': StopsCoords,
                'Total_CO2': Total_CO2,
                'Total_CO2_remote': Total_CO2_remote,
                'Total_CO2_cowork': Total_CO2_cowork,
                'Total_CO2_worst_case': Total_CO2_worst_case,
                'counts': df0["counts"].tolist(), 
                'Transport_share_labels': df0["Mode"].tolist(),
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

        temp_df = df0.copy()
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

        try:
            x0/x0_max
            x1/x1_max
        except:
            x0 = 0
            x1 = 0

        try:
            x2/x2_max
            x3/x3_max
        except:
            x2 = 0
            x3 = 0

        try:
            x4/x4_max
            x5/x5_max
        except:
            x4= 0
            x5 = 0

        try:
            x6/x6_max
            x7/x7_max
        except:
            x6= 0
            x7 = 0

        fig1 = go.Scatterpolar(
                    r=[radius_max*x0/x0_max, radius_max*x1/x1_max, radius_max*x2/x2_max, 
                    radius_max*x3/x3_max, radius_max*x4/x4_max, radius_max*x5/x5_max, 
                    radius_max*x7/x7_max, radius_max*x7/x7_max],
                    theta=['Remote working days',
                        'Remote working persons (%)',
                        'Coworking hubs',
                        'Coworking days', 
                        'Bus routes',
                        'Bus stops',
                        'Car electrification',
                        'eCar CO2'],
                    hovertext= [str(x0),str(x1), str(x2), str(x3), str(x4), str(x5), str(x6), str(x7)],
                    fill='toself'
                )

        fig2 = go.Bar(
                    y= [float(val) / 1000 for val in y_diff[:2]],
                    x=['Remote','Coworking'],
                    marker_color=colors[:2])
        fig22 = go.Bar(
                    y=[y_perc[2]],
                    x=['Total'],                
                    marker_color=colors[2])

        diff_TS_df = diff_TS_df.reset_index()
        diff_TS_df['color'] = diff_TS_df['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
        fig3 = go.Bar(
                    y=diff_TS_df['counts'],
                    x=diff_TS_df['Mode'],
                    marker_color=diff_TS_df['color'])

        diff_DS_df = diff_DS_df.reset_index()
        diff_DS_df['color'] = diff_DS_df['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
        fig4 = go.Bar(
                    y=diff_DS_df['distance_km'],
                    x=diff_DS_df['Mode'],
                    marker_color=diff_DS_df['color'])

        row_titles = ("Interventions", 
                    "CO2 emissions difference WRT baseline",
                    "",  
                    "Transport choice difference WRT baseline",
                    "Distance difference WRT baseline (km/week)")
        fig_comp = make_subplots(
                    rows=4, cols=2,
                    specs=[[{"type": "scatterpolar","colspan": 2}, None],
                        [{"type": "bar"}, {"secondary_y": True}],
                        [{"type": "bar","colspan": 2}, None],
                        [{"type": "bar","colspan": 2}, None]],
                    row_heights=[2,1,1,1],
                    subplot_titles=row_titles,
                    #horizontal_spacing=0.5,
                    )  
        fig_comp.add_trace(fig1, 1, 1)    
        fig_comp.add_trace(fig2, 2, 1)
        fig_comp.add_trace(fig22, 2, 2)
        fig_comp.add_trace(fig3, 3, 1)    
        fig_comp.add_trace(fig4, 4, 1)    

        fig_comp.update_annotations(font_size=18)
        fig_comp.layout.annotations[0].update(y=1.04)
        fig_comp.update_layout(showlegend=False)    
        fig_comp.update_layout(polar=dict(radialaxis=dict(visible=False)))
        fig_comp.update_polars(radialaxis=dict(range=[0, radius_max]))
        fig_comp.update_layout(title_text='Calculated scenario')
        #fig_comp.update_yaxes(secondary_y=False, title_text="Remote, Coworking (kg/week)", row=2, col=1)  
        fig_comp.update_yaxes(title_text="(tons/week)", row=2, col=1)  
        #fig_comp.update_yaxes(secondary_y=True, title_text="(%)", row=2, col=2) 
        fig_comp.update_yaxes(title_text="(%)", row=2, col=2)   

        for annotation in fig_comp['layout']['annotations']: 
            if annotation['text'] == 'CO2 emissions difference WRT baseline':
                annotation['x'] = annotation['x'] + 0.285 # 0.47000000000000003
        
        #fig_comp.update_xaxes(domain=[0, 1], row=3, col=1)
        #fig_comp.update_xaxes(domain=[0, 1], row=4, col=1)
        fig_comp.update_xaxes(categoryorder='array', categoryarray= ['Walk','PT','Car'], row=3, col=1)
        fig_comp.update_xaxes(categoryorder='array', categoryarray= ['Walk','PT','Car'], row=4, col=1)
        #fig.for_each_annotation(lambda a:  a.update(y = 1.05) if a.text in column_titles else a.update(x = -0.07) if a.text in row_titles else())

        #Total_CO2_worst_case = result['CO2_worst_case'].sum()
        #temp = result.loc[(result['Rem_work'] == 1) & (result['Coworking'] == 0)]
        temp = result.loc[(result['Rem_work'] > 0) & (result['Coworking'] == 0)]
        #Total_CO2_worst_case = temp['CO2_worst_case'].sum() + 0.000001 # to avoid div. by 0
        Total_CO2_worst_case = result['CO2_worst_case'].sum() 
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

        temp = result.loc[(result['Rem_work'] == 0) & (result['Coworking'] == 1)]
        #Total_CO2_worst_case = temp['CO2_worst_case'].sum() + 0.000001 # to avoid div. by 0
        Total_CO2_worst_case = result['CO2_worst_case'].sum() 
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

        temp = result.loc[(result['Rem_work'] > 0 ) & (result['Coworking'] == 1)]
        #Total_CO2_worst_case = temp['CO2_worst_case'].sum() + 0.000001 # to avoid div. by 0
        Total_CO2_worst_case = result['CO2_worst_case'].sum() 
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


        temp = result.loc[(result['Rem_work'] == 0) & (result['Coworking'] == 0)]
        #Total_CO2_worst_case = temp['CO2_worst_case'].sum() + 0.000001 # to avoid div. by 0
        #Total_CO2_worst_case = result['CO2_worst_case'].sum() + additional_co2
        Total_CO2_worst_case = result['CO2_worst_case'].sum() 
        Total_CO2 = temp['CO2'].sum() + additional_co2
        fig4 = go.Indicator(mode = "gauge+number",
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

        #predicted = result.loc[result['Rem_work'] == 1, 'prediction'] 
        predicted = result.loc[(result['Rem_work'] > 0 ) & (result['Coworking'] == 0), 'prediction']       
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

        #predicted = result.loc[result['Coworking'] == 1, 'prediction']
        predicted = result.loc[(result['Rem_work'] == 0) & (result['Coworking'] == 1), 'prediction'] 
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
    
        predicted = result.loc[(result['Rem_work'] > 0) & (result['Coworking'] == 1), 'prediction'] 
        unique_labels, counts = np.unique(predicted, return_counts=True)
        d = {'Mode': unique_labels, 'counts':counts}
        df = pd.DataFrame(data=d)
        df['Mode'] = df['Mode'].map({0:'Walk',1:'PT',2:'Car'}) 
        df['color'] = df['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})     
        fig7 = go.Pie(labels=df["Mode"],
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
        fig8 = go.Pie(labels=df["Mode"],
                    values=df["counts"],
                    showlegend=False,
                    textposition='inside',
                    textinfo='label+percent',
                    marker=dict(colors=df['color']),
                    scalegroup = 'one')


        #temp = result.loc[result['Rem_work'] == 1]
        temp = result.loc[(result['Rem_work'] > 0 ) & (result['Coworking'] == 0)] 
        if not temp.empty:
            """
            temp['distance_km'] = temp['distance_week']/1000.
            temp = temp[['Mode','distance_km']]
            Contribs = temp.groupby(['Mode']).sum() 
            Contribs = Contribs.reset_index()
            Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
            """    
            temp['distance_km'] = temp['distance_week_interv']/1000.
            temp['distance_km_no_interv'] = temp['distance_week_no_interv']/1000.
            temp1 = temp[['Mode','distance_km']]
            temp2 = temp[['Mode_base','distance_km_no_interv']]    
            Contribs1 = temp1.groupby(['Mode']).sum() 
            Contribs1 = Contribs1.reset_index()
            Contribs2 = temp2.groupby(['Mode_base']).sum() 
            Contribs2 = Contribs2.reset_index()
            Contribs2['Mode'] = Contribs2['Mode_base']
            Contribs2['distance_km'] = Contribs2['distance_km_no_interv']
            Contribs2.drop(['Mode_base','distance_km_no_interv'], axis=1, inplace=True)
            Contribs = pd.concat([Contribs1,Contribs2]).groupby(['Mode']).sum().reset_index()
            Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
        else:
            data = {'Mode': ['No mode'],
                    'distance_km': [0],
                    'color': ['#FF0000']}
            Contribs = pd.DataFrame(data)
            
        print(Contribs.head())
        fig9 = go.Bar(
                x=Contribs['distance_km'],
                y=Contribs['Mode'],
                orientation='h',
                marker_color=Contribs['color'])
        max_dist_1 = Contribs['distance_km'].max()

        #temp = result.loc[result['Coworking'] == 1] 
        temp = result.loc[(result['Rem_work'] == 0) & (result['Coworking'] == 1)]    
        if not temp.empty:
            """
            temp['distance_km'] = temp['distance_week']/1000.
            temp = temp[['Mode','distance_km']]
            Contribs = temp.groupby(['Mode']).sum() 
            Contribs = Contribs.reset_index()
            Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
            """
            temp['distance_km'] = temp['distance_week_interv']/1000.
            temp['distance_km_no_interv'] = temp['distance_week_no_interv']/1000.
            temp1 = temp[['Mode','distance_km']]
            temp2 = temp[['Mode_base','distance_km_no_interv']]    
            Contribs1 = temp1.groupby(['Mode']).sum() 
            Contribs1 = Contribs1.reset_index()
            Contribs2 = temp2.groupby(['Mode_base']).sum() 
            Contribs2 = Contribs2.reset_index()
            Contribs2['Mode'] = Contribs2['Mode_base']
            Contribs2['distance_km'] = Contribs2['distance_km_no_interv']
            Contribs2.drop(['Mode_base','distance_km_no_interv'], axis=1, inplace=True)
            Contribs = pd.concat([Contribs1,Contribs2]).groupby(['Mode']).sum().reset_index()
            Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})        
        else:        
            data = {'Mode': ['No mode'],
                    'distance_km': [0],
                    'color': ['#FF0000']}
            Contribs = pd.DataFrame(data)
        fig10 = go.Bar(
                x=Contribs['distance_km'],
                y=Contribs['Mode'],
                orientation='h',
                marker_color=Contribs['color'])
        max_dist_2 = Contribs['distance_km'].max()


        temp = result.loc[(result['Rem_work'] > 0 ) & (result['Coworking'] == 1)]    
        if not temp.empty:
            """
            temp['distance_km'] = temp['distance_week']/1000.
            temp = temp[['Mode','distance_km']]
            Contribs = temp.groupby(['Mode']).sum() 
            Contribs = Contribs.reset_index()
            Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
            """
            temp['distance_km'] = temp['distance_week_interv']/1000.
            temp['distance_km_no_interv'] = temp['distance_week_no_interv']/1000.
            temp1 = temp[['Mode','distance_km']]
            temp2 = temp[['Mode_base','distance_km_no_interv']]    
            Contribs1 = temp1.groupby(['Mode']).sum() 
            Contribs1 = Contribs1.reset_index()
            Contribs2 = temp2.groupby(['Mode_base']).sum() 
            Contribs2 = Contribs2.reset_index()
            Contribs2['Mode'] = Contribs2['Mode_base']
            Contribs2['distance_km'] = Contribs2['distance_km_no_interv']
            Contribs2.drop(['Mode_base','distance_km_no_interv'], axis=1, inplace=True)
            Contribs = pd.concat([Contribs1,Contribs2]).groupby(['Mode']).sum().reset_index()
            Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})        
        else:        
            data = {'Mode': ['No mode'],
                    'distance_km': [0],
                    'color': ['#FF0000']}
            Contribs = pd.DataFrame(data)
        fig11 = go.Bar(
                x=Contribs['distance_km'],
                y=Contribs['Mode'],
                orientation='h',
                marker_color=Contribs['color'])
        max_dist_3 = Contribs['distance_km'].max()

        temp = result.loc[(result['Rem_work'] == 0) & (result['Coworking'] == 0)]
        if not temp.empty:
            """
            temp['distance_km'] = temp['distance_week']/1000.
            temp = temp[['Mode','distance_km']]
            Contribs = temp.groupby(['Mode']).sum() 
            Contribs = Contribs.reset_index()
            Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
            """
            temp['distance_km'] = temp['distance_week_interv']/1000.
            temp['distance_km_no_interv'] = temp['distance_week_no_interv']/1000.
            temp1 = temp[['Mode','distance_km']]
            temp2 = temp[['Mode_base','distance_km_no_interv']]    
            Contribs1 = temp1.groupby(['Mode']).sum() 
            Contribs1 = Contribs1.reset_index()
            Contribs2 = temp2.groupby(['Mode_base']).sum() 
            Contribs2 = Contribs2.reset_index()
            Contribs2['Mode'] = Contribs2['Mode_base']
            Contribs2['distance_km'] = Contribs2['distance_km_no_interv']
            Contribs2.drop(['Mode_base','distance_km_no_interv'], axis=1, inplace=True)
            Contribs = pd.concat([Contribs1,Contribs2]).groupby(['Mode']).sum().reset_index()
            Contribs['color'] = Contribs['Mode'].map({'Walk': 'green','PT': 'blue','Car':'red'})
        else:
            data = {'Mode': ['No mode'],
                    'distance_km': [0],
                    'color': ['#FF0000']}
            Contribs = pd.DataFrame(data)
        fig12 = go.Bar(
                x=Contribs['distance_km'],
                y=Contribs['Mode'],
                orientation='h',
                marker_color=Contribs['color'])
        max_dist_4 = Contribs['distance_km'].max()
        max_distance = max(max_dist_1,max_dist_2,max_dist_3,max_dist_4)


        #family_types = ['Hogar de una persona', 'Otros hogares sin niños', '2 adultos',
        #                '2 adultos con niño(s)', '1 adulto con niño(s)',
        #                'Otros hogares con niños']    
        no_kids_df = result.loc[(result['Rem_work'] > 0) & (result['Coworking'] == 0) & (result['Tipo_familia'] <3) & (result['Mode'] == 'Car')]
        kids_df    = result.loc[(result['Rem_work'] > 0) & (result['Coworking'] == 0) &(result['Tipo_familia'] >2) & (result['Mode'] == 'Car')]
        fig13 = go.Bar(
                x=['No kids', 'Kids'],
                y=[len(no_kids_df['CO2'].index),len(kids_df['CO2'].index)],
                #marker_color=['red','orange'],
                marker_color=['#2b62c0','orange'],
                marker=dict(cornerradius="30%"))
        max_families_1 = max(len(no_kids_df['CO2'].index),len(kids_df['CO2'].index))

        no_kids_df = result.loc[(result['Coworking'] == 1) & (result['Rem_work'] == 0) & (result['Tipo_familia'] <3) & (result['Mode'] == 'Car')]
        kids_df    = result.loc[(result['Coworking'] == 1) & (result['Rem_work'] == 0) & (result['Tipo_familia'] >2) & (result['Mode'] == 'Car')]
        fig14 = go.Bar(
                x=['No kids', 'Kids'],
                y=[len(no_kids_df['CO2'].index),len(kids_df['CO2'].index)],
                #marker_color=['red','orange'],
                marker_color=['#2b62c0','orange'],
                marker=dict(cornerradius="30%"))
        max_families_2 = max(len(no_kids_df['CO2'].index),len(kids_df['CO2'].index))

        no_kids_df = result.loc[(result['Coworking'] == 1) & (result['Rem_work'] > 0) & (result['Tipo_familia'] <3) & (result['Mode'] == 'Car')]
        kids_df    = result.loc[(result['Coworking'] == 1) & (result['Rem_work'] > 0) & (result['Tipo_familia'] >2) & (result['Mode'] == 'Car')]
        fig15 = go.Bar(
                x=['No kids', 'Kids'],
                y=[len(no_kids_df['CO2'].index),len(kids_df['CO2'].index)],
                #marker_color=['red','orange'],
                marker_color=['#2b62c0','orange'],
                marker=dict(cornerradius="30%"))
        max_families_3 = max(len(no_kids_df['CO2'].index),len(kids_df['CO2'].index))

        no_kids_df = result.loc[(result['Rem_work'] == 0) & (result['Coworking'] == 0) & (result['Tipo_familia'] <3) & (result['Mode'] == 'Car')]
        kids_df    = result.loc[(result['Rem_work'] == 0) & (result['Coworking'] == 0) & (result['Tipo_familia'] >2) & (result['Mode'] == 'Car')]
        fig16 = go.Bar(
                x=['No kids', 'Kids'],
                y=[len(no_kids_df['CO2'].index),len(kids_df['CO2'].index)],
                #marker_color=['red','orange'],
                marker_color=['#2b62c0','orange'],
                marker=dict(cornerradius="30%"))
        max_families_4 = max(len(no_kids_df['CO2'].index),len(kids_df['CO2'].index))
        max_families = max(max_families_1,max_families_2,max_families_3,max_families_4)

        column_titles = ['Remote working', 'Coworking', 'Remote + Coworking','Rest']
        row_titles = ['CO2 emissions', 'Transport share', 'Distance share (km)', 'Using car']
        #fig = make_subplots(rows=1, cols=3)
        fig_decomp = make_subplots(rows=4, cols=4, 
                            specs=[
                                [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
                                [{"type": "pie"}, {"type": "pie"}, {"type": "pie"}, {"type": "pie"}],
                                [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
                                [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}, {"type": "bar"}]],
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
        fig_decomp.append_trace(fig4, 1, 4)
        fig_decomp.append_trace(fig5, 2, 1)
        fig_decomp.append_trace(fig6, 2, 2)
        fig_decomp.append_trace(fig7, 2, 3)
        fig_decomp.append_trace(fig8, 2, 4)
        fig_decomp.append_trace(fig9,  3, 1)
        fig_decomp.append_trace(fig10, 3, 2)
        fig_decomp.append_trace(fig11, 3, 3)
        fig_decomp.append_trace(fig12, 3, 4)
        fig_decomp.append_trace(fig13, 4, 1)
        fig_decomp.append_trace(fig14, 4, 2)
        fig_decomp.append_trace(fig15, 4, 3)
        fig_decomp.append_trace(fig16, 4, 4)      

        #fig.update_xaxes(title_text="Total weekly distance (km)", showgrid=True, row=3, col=1)
        #fig.update_xaxes(title_text="Total weekly distance (km)", showgrid=True, row=3, col=2)
        #fig.update_xaxes(title_text="Total weekly distance (km)", showgrid=True, row=3, col=3)        
        fig_decomp.update_annotations(font_size=28)
        fig_decomp.update_layout(showlegend=False)    
        fig_decomp.update_xaxes(showgrid=True, row=3, col=1, range=[0, max_distance])
        fig_decomp.update_xaxes(showgrid=True, row=3, col=2, range=[0, max_distance])
        fig_decomp.update_xaxes(showgrid=True, row=3, col=3, range=[0, max_distance])
        fig_decomp.update_xaxes(showgrid=True, row=3, col=4, range=[0, max_distance])
        fig_decomp.update_yaxes(showgrid=True, row=4, col=1, range=[0, max_families])
        fig_decomp.update_yaxes(showgrid=True, row=4, col=2, range=[0, max_families])
        fig_decomp.update_yaxes(showgrid=True, row=4, col=3, range=[0, max_families])
        fig_decomp.update_yaxes(showgrid=True, row=4, col=4, range=[0, max_families])


        #Total_CO2 = result['CO2'].sum()
        #Total_CO2_worst_case = result['CO2_worst_case'].sum()
        IndPark_marker = [dl.Marker(dl.Tooltip("Industrial Park"), position=IndParkCoord, icon=custom_icon_IndPark, id='IndPark_1')]

        new_map = MiscFunctions.generate_map(result, CowFlags,StopsCoords, IndPark_marker)
        #return [Total_CO2/Total_CO2_worst_case, fig_total, fig_decomp, new_map]
        return [fig_total, new_map, fig_decomp, fig_comp, new_stored_scenarios]


    def categorize_Mode(code):
        if 'Andando' in code:
            return 'Walk'
        elif 'Coche' in code:
            return 'Car'
        else:
            return 'PT'
    
    #def run_MCM(trips_ez, root_Dir, Transh, routeOptDone, gkm_car=1./12, gkm_bus=1.1, co2lt=2.3, NremDays=0, NremWork=0, CowCoords=[], CowDays=0):
    def run_MCM(trips_ez, root_Dir, Transh, routeOptDone, co2km_car=0.15, co2km_eCar= 0.01081, co2km_bus=1.3, co2km_train=0.049, bus_train_ratio=0.8, NremDays=0, NremWork=0, NeCar=0, CowCoords=[], CowDays=0):
        import pandas as pd
        import sys    
        root_dir = root_Dir
        #sys.path.append(root_dir + 'modules')
        sys.path.append(root_dir + 'components')
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
