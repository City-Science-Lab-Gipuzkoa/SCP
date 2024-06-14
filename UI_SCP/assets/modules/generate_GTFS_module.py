import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
from geopy.point import Point
import datetime

directory = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/data/GTFS_routes/'


def gGTFS(ruta_EZ0, puntos, G):
    print()
    print('start generating GTFS file...')
    cont_stops = 0
    trip_num = '0'
    stops_coord_written = []
    #ruta_EZ0 = list(ruta_EZ0.values())
    for i_route in range(len(ruta_EZ0)): # loop over routes (= m_buses)
        ruta_stops_coord = []
        for i in range(len(ruta_EZ0[i_route])):
            ruta_stops_coord.append(puntos[ruta_EZ0[i_route][i]])
            #print(i_route, i, ruta_EZ0[i_route][i], puntos[ruta_EZ0[i_route][i]])
            print(i_route, ruta_EZ0[i_route][i], puntos[ruta_EZ0[i_route][i]])
    
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
        if i_route == 0:
           with open(directory + 'agency.txt', 'w') as f:
               f.write(header + "\n")
               f.write('CSL_01, CSL@Gipuzkoa, https://www.media.mit.edu/groups/city-science/overview/, CET')
           f.close()
    
        # stops.txt
        # stop_id,stop_name,stop_lat,stop_lon, location_type, parent_station
        # parent_station = ID of principal station/stop? = origin of buses?
        # key = stop_id
        stop_ids = []
        header = "stop_id,stop_name,stop_lat,stop_lon, location_type, parent_station"
        geolocator = Nominatim(user_agent="coordinateconverter")
        if i_route == 0:
           parent_station = 'S0'
           with open(directory + 'stops.txt', 'w') as f:
               f.write(header + "\n")
               f.close()
        with open(directory + 'stops.txt', 'a') as f:
               for i in range(len(ruta_stops_coord)):
                   stop_id = 'S' + str(cont_stops)
                   lat = ruta_stops_coord[i][0]
                   lon = ruta_stops_coord[i][1]
                   stop_name = geolocator.reverse(Point(lat,lon))
                   stop_name0 = str(stop_name).split(',')[0]
                   stop_name1 = str(stop_name).split(',')[1][1:]
                   stop_name = stop_name0 + '_' + stop_name1
                   if [lat, lon] not in stops_coord_written:
                      if i_route == 0 and i == 0:
                         f.write(stop_id + ', ' + stop_name + ', ' + str(lat) + ', ' + str(lon) + ', 0, ' + ' ' + "\n")
                      else:
                         f.write(stop_id + ', ' + stop_name + ', ' + str(lat) + ', ' + str(lon) + ', 0, ' + parent_station + "\n")
                      stops_coord_written.append([lat,lon])
                      stop_ids.append(stop_id)
                      #print('stop_id: ',stop_id)
                      cont_stops+=1
        f.close()
    
        # routes.txt
        # route_id,route_short_name,route_long_name,route_desc,route_type
        # key = route_id
        route_id = 'EZ' + str(i_route)
        route_type = '3' # bus
        header = "route_id,route_short_name,route_long_name,route_desc,route_type"
        if i_route == 0:
           with open(directory + 'routes.txt', 'w') as f:
               f.write(header + "\n")
               f.close()
        with open(directory + 'routes.txt', 'a') as f:
               f.write(route_id + ', ' + 'Esku_' + route_id + ', Eskuzaitzeta ' + str(i_route) + ', ' + 'The "Eskuzaitzeta" route serves workers of the industrial park,' + route_type + '\n')
               f.close()
    
        # trips.txt
        # route_id,service_id,trip_id,trip_headsign,block_id
        # key = trip_id
        trip_id = 'EZ_rou' + str(i_route) + '_tr' + trip_num #'EZ0'
        service_id = '1'
        header = 'route_id, trip_id, service_id'
        if i_route == 0:
           with open(directory + 'trips.txt', 'w') as f:
               f.write(header + "\n")
               f.close()
        with open(directory + 'trips.txt', 'a') as f:
            f.write(route_id + ', ' + trip_id + ', ' + service_id + '\n' )
        f.close()
    
        # stop_times.txt
        # key = stop_sequence
        header = "trip_id,arrival_time,departure_time,stop_id,stop_sequence"
        if i_route == 0:
           date_and_time = datetime.datetime.now()+datetime.timedelta(hours=1)
           with open(directory + 'stop_times.txt', 'w') as f:
               f.write(header + "\n")
               #t0 = date_and_time.strftime("%H:%M:%S")
               #f.write(trip_id + ", " + t0 + ', ' + t0 + ', ' + 'S0' + ', ' + '1' + "\n")
               f.close()
    
        with open(directory + 'stop_times.txt', 'a') as f:
            for i in range(len(times)):
                time_change = datetime.timedelta(minutes=2)
                new_time = date_and_time + time_change
                t0 = date_and_time.strftime("%H:%M:%S")
                t1 = new_time.strftime("%H:%M:%S")
                if i_route == 0 and i == 0:
                      f.write(trip_id + ", " + t0 + ', ' + t0 + ', ' + stop_ids[0] + ', ' + '1' + "\n")
                      if len(times) == 1:
                         time_change = datetime.timedelta(minutes=times[i])
                         new_time = date_and_time + time_change
                         t0 = new_time.strftime("%H:%M:%S")
                         time_change = datetime.timedelta(minutes=2)
                         new_time = new_time + time_change
                         t1 = new_time.strftime("%H:%M:%S")
                         f.write(trip_id + ", " + t0 + ', ' + t1 + ', ' + stop_ids[1] + ', ' + '2' + "\n")
                else:
                   f.write(trip_id + ", " + t0 + ', ' + t1 + ', ' + stop_ids[i] + ', ' + str(i+2) + "\n")
                time_change = datetime.timedelta(minutes=times[i])
                date_and_time = new_time + time_change
                #print('stop times, stop_id: ', i_route, i, stop_ids[i])
        f.close()

