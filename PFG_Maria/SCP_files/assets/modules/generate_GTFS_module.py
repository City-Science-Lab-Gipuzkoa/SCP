import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
from geopy.point import Point
import datetime
from datetime import date, timedelta
import re
import os
import pandana as pdn
import pandas as pd

#directory = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/data/input_data_MCM/GTFS_feeds/routes_EZ_companies/'

def gGTFS(ruta_EZ0, puntos, G, root_dir, n_trips = 6, freq = 10, start_hour = '8:00'):
    print()
    print('start generating GTFS file...')
    directory = root_dir + 'data/input_data_MCM/GTFS_feeds/routes_EZ_companies/'
    isExist = os.path.exists(directory)
    print('routes directory:')
    print(directory)
    if not isExist:
       # Create a new directory because it does not exist
       os.makedirs(directory)


    network = pdn.network.Network.from_hdf5(root_dir + 'data/input_data_MCM/' + f'networks/drive_net.h5')


    cont_stops = 0
    cont_all_stops = 0
    trip_num = '0'
    stops_coord_written = []
    #ruta_EZ0 = list(ruta_EZ0.values())
    for i_route in range(len(ruta_EZ0)): # loop over routes (= m_buses)
        ruta_stops_coord = []
        for i in range(len(ruta_EZ0[i_route])):
            ruta_stops_coord.append(puntos[ruta_EZ0[i_route][i]])
            #print(i_route, i, ruta_EZ0[i_route][i], puntos[ruta_EZ0[i_route][i]])
            print(i_route, ruta_EZ0[i_route][i], puntos[ruta_EZ0[i_route][i]])
    
        """"
        ori_coord = ruta_stops_coord[0]
        origin = ori_coord
        origin_node = ox.distance.nearest_nodes(G, [origin[1]], [origin[0]])[0]
        times = []
        for i in range(1,len(ruta_stops_coord)-1):           
           destination = ruta_stops_coord[i]
           destination_node = ox.distance.nearest_nodes(G, [destination[1]], [destination[0]])[0]
           #route = nx.shortest_path(G, origin_node, destination_node)
           #print(G.nodes[origin_node])
           #print(G.nodes[destination_node])
    
           # replace the previous code with the following:
           route = nx.shortest_path(G, origin_node, destination_node, weight='length') # Returns a list of nodes comprising the route
           path_length = 0
           path_time = 0
           for u, v in zip(route, route[1:]):
               edge_length = G.get_edge_data(u,v)[0]['length']   # Returns length in meters, e.g. 50.26
               path_length += edge_length
               edge_travel_time = G.get_edge_data(u,v)[0]['travel_time'] # Returns travel time in secs
               path_time += edge_travel_time
           print('length (km): ',path_length/1000)
           print('time (min): ',path_time/60)
           times.append(path_time/60)
        """
        

        # modified after modification of calc_routes with pandana ##################
        ori_coord = ruta_stops_coord[0]
        origin = ori_coord
        #origin_node = ox.distance.nearest_nodes(G, [origin[1]], [origin[0]])[0]
        # origin_node moved down
        ##############################################################################

        hours = []
        new_t = datetime.datetime.strptime(str(start_hour), "%H:%M")
        hours.append(new_t.strftime("%H:%M"))
        for i in range(n_trips):
            new_t = new_t + timedelta(minutes=freq)
            hours.append(new_t.strftime("%H:%M"))
        #hours = ["08:00","08:10","08:20","08:30","08:40","08:50","09:00"] # hours of the service. Each route has a trip at these hours 
        times = []
        print(hours)
        for i in range(0,len(ruta_stops_coord)-1):           
           destination = ruta_stops_coord[i+1]
           # modified after modification of calc_routes with pandana ##################
           #destination_node = ox.distance.nearest_nodes(G, [destination[1]], [destination[0]])[0]
           ##############################################################################
           ##route = nx.shortest_path(G, origin_node, destination_node)
           ##print(G.nodes[origin_node])
           ##print(G.nodes[destination_node])
           data = [[origin[1], origin[0], destination[1], destination[0]]]
           # Create the pandas DataFrame
           df_coords = pd.DataFrame(data, columns=['O_Long', 'O_Lat', 'D_Long', 'D_Lat'])
           origin_node = network.get_node_ids(df_coords.O_Long,df_coords.O_Lat)
           destination_node = network.get_node_ids(df_coords.D_Long,df_coords.D_Lat)
           # replace the previous code with the following:
           # modified after modification of calc_routes with pandana ##################
           #route = nx.shortest_path(G, origin_node, destination_node, weight='length') # Returns a list of nodes comprising the route
           #############################################################################
           route = network.shortest_paths(origin_node, destination_node, imp_name='distance')[0] 
           path_length = 0
           path_time = 0

           """
           for u, v in zip(route, route[1:]):
               edge_length = G.get_edge_data(u,v)[0]['length']   # Returns length in meters, e.g. 50.26
               path_length += edge_length
               edge_travel_time = G.get_edge_data(u,v)[0]['travel_time'] # Returns travel time in secs
               path_time += edge_travel_time
           print('length (km): ',path_length/1000)
           print('time (min): ',path_time/60)
           """
        
           for u, v in zip(route, route[1:]):
               #edge_travel_time = network.get_edge_data(u,v)[0]['drive_time_s'] # Returns travel time in secs
               edge_travel_time = network.edges_df[(network.edges_df['from'] == u) & (network.edges_df['to'] == v)]['speed_m_s'].values[0]
               path_time += edge_travel_time
           print('time (min): ',path_time/60)


           times.append(path_time/60)        
    
        #test = nx.shortest_path(G, origin_node, destination_node)
        #for edge in G.out_edges(test, data=True):
        #    print("\n=== Edge ====")
        #    print("Source and target node ID:", edge[:2])
        #    edge_attributes = edge[2]
        #    # remove geometry object from output
        #    edge_attributes_wo_geometry = {i:edge_attributes[i] for i in edge_attributes if i!='geometry'}
        #    print("Edge attributes:", json.dumps(edge_attributes_wo_geometry, indent=4))
        #fig, ax = ox.plot_graph_route(G, test)
        #plt.show()
    
    
        # agency.txt
        # agency_id,agency_name,agency_url,agency_timezone
        header = "agency_id,agency_name,agency_url,agency_timezone"
        agency_id = 'CSL_01'
        if i_route == 0:
           with open(directory + 'agency.txt', 'w') as f:
               f.write(header + "\n")
               f.write(agency_id + ',' + 'CSL@Gipuzkoa, https://www.media.mit.edu/groups/city-science/overview/, CET')
           f.close()      

        # stops.txt
        # stop_id,stop_name,stop_lat,stop_lon, location_type, parent_station
        # parent_station = ID of principal station/stop? = origin of buses?
        # key = stop_id
        stop_id_0 = '123'
        #zone_id = '1'
        #location_type = '0'
        stop_ids = []
        stop_ids_unique = []
        header = "stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station"
        geolocator = Nominatim(user_agent="coordinateconverter")
        if i_route == 0:
           parent_station = "" #'S0'
           with open(directory + 'stops.txt', 'w') as f:
               f.write(header + "\n")
               f.close()       
        with open(directory + 'stops.txt', 'a') as f:
               for i in range(len(ruta_stops_coord)):
                   stop_id = stop_id_0 + str(cont_stops)
                   if i == 0:
                      stop_ids.append(stop_id_0+'0')
                   if i>0 and i < len(ruta_stops_coord)-1: # exclude last point which is the origin (point 0)
                      stop_ids.append(stop_id_0 + str(cont_all_stops))                       
                   lat = ruta_stops_coord[i][0]
                   lon = ruta_stops_coord[i][1]
                   stop_name = geolocator.reverse(Point(lat,lon))
                   stop_name0 = str(stop_name).split(',')[0]
                   stop_name1 = str(stop_name).split(',')[1][1:]
                   stop_name0 = re.sub(r'[^\x00-\x7f]',r'', stop_name0) # remove non non-ascii characters
                   stop_name1 = re.sub(r'[^\x00-\x7f]',r'', stop_name1) # remove non non-ascii characters
                   stop_name = stop_name0 + '_' + stop_name1
                   if [lat, lon] not in stops_coord_written:
                      if i_route == 0 and i == 0:
                         f.write(stop_id + ', ' + stop_name + ', ' + str(lat) + ', ' + str(lon) + ', 0, ' + ' ' + "\n")
                      else:
                         f.write(stop_id + ', ' + stop_name + ', ' + str(lat) + ', ' + str(lon) + ', 0, ' + parent_station + "\n")
                      stops_coord_written.append([lat,lon])
                      stop_ids_unique.append(stop_id)
                      cont_stops+=1   
                      cont_all_stops+=1
        f.close()

    
        # routes.txt
        # route_id,route_short_name,route_long_name,route_desc,route_type
        # key = route_id
        route_id = 'EZ' + str(i_route)
        route_type = '3' # bus
        header = "route_id,agency_id,route_short_name,route_long_name,route_desc,route_type,route_url,route_color,route_text_color"
        route_color = 'FFFFFF'
        route_text_color = '8DC63F'
        route_url = ''
        if i_route == 0:
           with open(directory + 'routes.txt', 'w') as f:
               f.write(header + "\n")
               f.close()
        with open(directory + 'routes.txt', 'a') as f:
               #f.write(agency_id + ',' + route_id + ', ' + 'Esku_' + route_id + ', Eskuzaitzeta ' + str(i_route) + ', ' + 'The "Eskuzaitzeta" route serves workers of the industrial park, ' + route_type + '\n')
               #f.write(route_id + ',' + agency_id + ', ' + 'Esku_' + route_id + ', Eskuzaitzeta ' + str(i_route) + ',' + ',' + route_type + ',' + route_url + ',' + route_color +  ',' + route_text_color + '\n')
               f.write(route_id + ',' + agency_id + ',' + '' + ',Eskuzaitzeta' + str(i_route) + ',' + ',' + route_type + ',' + route_url + ',' + route_color +  ',' + route_text_color + '\n')
               
               f.close()

        # trips.txt
        # key = trip_id
        trip_id = 'EZ_rou' + str(i_route) + '_tr' + trip_num #'EZ0'
        service_id = 'EZ'
        header = 'route_id,trip_id,service_id'
        if i_route == 0:
           with open(directory + 'trips.txt', 'w') as f:
               f.write(header + "\n")
               f.close()
        with open(directory + 'trips.txt', 'a') as f:
            for i_h in range(len(hours)):
                f.write(route_id + ',' + trip_id + '_' + str(i_h) + ',' + service_id + '\n' )
        f.close()
    
        # calendar.txt
        header = "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date"
        today = date.today()
        this_year = str(today.strftime("%Y"))
        first_MonthDay = "0101"
        last_MonthDay = "1231"
        if i_route == 0:
           with open(directory + 'calendar.txt', 'w') as f:
               f.write(header + "\n")
               f.write(service_id +',' +'1,1,1,1,1,0,0,' + this_year+first_MonthDay + ',' + this_year+last_MonthDay)
           f.close()

        # calendar_dates.txt
        header = "service_id,date,exception_type"
        service_off = "2"
        service_on = "1" 
        substitute = service_id + "_sub"
        MonthDays = [this_year+"0101",this_year+"0106",this_year+"0401",this_year+"0501"]              
        if i_route == 0:
           with open(directory + 'calendar_dates.txt', 'w') as f:
               f.write(header + "\n")
               for i_OffOn in MonthDays: 
                   f.write( service_id + ',' + i_OffOn + ','+ service_off + "\n") 
                   f.write( substitute + ',' + i_OffOn + ','+ service_on + "\n") 
           f.close()


        # stop_times.txt
        # key = stop_sequence
        timepoint = '0' # arrival/departure times are approximate
        pickup_type = '0'
        drop_off_type = '0'
        header = "trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type,timepoint"
        if i_route == 0:
           #date_and_time = datetime.datetime.now()+datetime.timedelta(hours=1)
           with open(directory + 'stop_times.txt', 'w') as f:
               f.write(header + "\n")
               f.close()


        for i_h in range(len(hours)):
            today = datetime.datetime.now() 
            hour = int(hours[i_h].split(':')[0])
            minutes = int(hours[i_h].split(':')[1])
            date_and_time = datetime.datetime(today.year, today.month, today.day, hour, minutes)
            with open(directory + 'stop_times.txt', 'a') as f:
                for i in range(len(times)):
                    time_change = datetime.timedelta(minutes=1./6)
                    new_time = date_and_time + time_change
                    t0 = date_and_time.strftime("%H:%M:%S")
                    t1 = new_time.strftime("%H:%M:%S")
                    print('route, i, stop_ids')
                    print(i_route, i, stop_ids, stop_ids_unique)
                    #print('route, len(times), len(stops_id), stop times, stop_id: ', i_route, len(times), len(stop_id), i, stop_ids[i + i_route*(cont_all_stops-1)])
                    f.write(trip_id + '_' + str(i_h) + "," + t0 + ',' + t1 + ',' + stop_ids[i] + ',' + str(i+1) + ',' + pickup_type + ',' + drop_off_type +',' + timepoint + "\n")
                    time_change = datetime.timedelta(minutes=times[i])
                    date_and_time = new_time + time_change
        f.close()

