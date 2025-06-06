import numpy as np
from docplex.mp.model import Model
import random
from numpy.random import randint

import osmnx as ox
import networkx as nx
import json

import itertools
from itertools import permutations

import pandas as pd
import geopandas
from geopy import distance # Biblioteca para calculos geograficos
from geopy.geocoders import Nominatim
from geopy.point import Point
from shapely.geometry import Polygon  

import pandana as pdn

import datetime
import time


# directory where GTFS files will be saved
#directory = '/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/Proyecto Piloto_Eskuzaitzeta/GTFS_files/'

# Read the GTFS files
#stops = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/Proyecto Piloto_Eskuzaitzeta/DATOS_GIPUZKOA/gtfs_Zubieta/gtfs/stops.txt', delimiter=',')
#stop_times = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/Proyecto Piloto_Eskuzaitzeta/DATOS_GIPUZKOA/gtfs_Zubieta/gtfs/stop_times.txt', delimiter=',')
#trips = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/Proyecto Piloto_Eskuzaitzeta/DATOS_GIPUZKOA/gtfs_Zubieta/gtfs/trips.txt', delimiter=',')
#routes = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/Proyecto Piloto_Eskuzaitzeta/DATOS_GIPUZKOA/gtfs_Zubieta/gtfs/routes.txt', delimiter=',')

#root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
#root_dir = '/home/cslgipuzkoa/virtual_machine_disk/UI_SCP/assets/'


"""
# INPUTS
m_buses = 3 # number of available buses-> affects quality of solution for the Asymm. mTSP
#selec_trip_id = 32394  # 23 pts
#selec_trip_id =  32566 # 8 pts
selec_trip_id =  32402 # 13 pts -> just as an example, select the set of stops
#selec_trip_id =  32404 # 18 pts -> just as an example, select the set of stops
"""

tol = 1.5
tol_dist = 0.7 # % difference between longest and shortest route
cont_limit = 300 # max number of iterations for convergence

#CO2km = 1.12

def routes_list(A,m_b):
  ruta = {}
  for i in range(0, m_b):
    ruta['Bus_' + str(i+1)] = [0]
    j = i
    a = 10e10
    while a != 0:
        a = A[j,1]
        ruta['Bus_' + str(i+1)].append(a)
        #print(ruta['Bus_' + str(i+1)])
        j = np.where(A[:,0] == a)
        j = j[0][0]
        a = j
  return ruta

#def extract_RoutesMat(Xmat, Vec, n, pt, mb):
def extract_RoutesMat(Xmat, Vec, n, mb):
     paths0 = []
     out = np.zeros((n,n))
     #for (i, j) in zip(Vec, Vec):
     indeces = list(itertools.product(Vec, Vec))
     for ii in indeces:
        i = ii[0]
        j = ii[1]
        if Xmat[i][j] > 0:
           out[i][j] = Xmat[i][j]
           paths0.append([i,j])
     routes0 = routes_list(np.array(paths0),mb)
     return routes0, out

def check_Nbuses(Xmat):
  print('N buses going out from origin ={:3d}'.format(int(sum(Xmat[0,:]))))
  print('N buses returning to origin ={:3d}'.format(int(sum(Xmat[:,0]))))
  return

def check_UniqueStops(Xmat):
  for i in range(1,np.shape(Xmat)[0]):
     print('N routes out stop {:3d}: {:3d}'.format(i+1,int(sum(Xmat[i,:]))))
     print('N routes in stop {:3d}: {:3d}'.format(i+1,int(sum(Xmat[:,i]))))
  #print('Check all (should be 1):')
  #print((Xmat[1:,:].sum())/(np.shape(Xmat)[0]-1))
  return


def remove_oneway_ends(Gr):
    G2 = Gr.copy()
    spn = ox.stats.count_streets_per_node(G2)
    nx.set_node_attributes(G2, values=spn, name="street_count")
    completed = 0
    while(completed==0):
        nodes2rem = []
        for u,v,a in G2.edges(data=True):
            if G2.nodes[u]['street_count'] == 1:
                if a['oneway'] == True:
                    nodes2rem.append(u) 
            if G2.nodes[v]['street_count'] == 1:
                if a['oneway'] == True:
                    nodes2rem.append(v)
        G2.remove_nodes_from(nodes2rem)
        # count again the number of streets per node #######################
        spn = ox.stats.count_streets_per_node(G2)
        nx.set_node_attributes(G2, values=spn, name="street_count")
        ####################################################################
        if len(nodes2rem) == 0:
            completed = 1
    return G2
def check_conn_dirty_fix(Gr,pts,bbox):
    n = len(pts)
    drive_speed = 50
    no = bbox[0]
    so = bbox[1]
    ea = bbox[2]
    we = bbox[3]
    G_walk = ox.graph_from_bbox(no, so, ea, we, network_type="walk", simplify=False) 
    for i in range(n):
        origin = pts[i]
        origin_node = ox.distance.nearest_nodes(Gr, [origin[1]], [origin[0]])[0]
        coords_1 = (origin[0],origin[1])
        coords_2 = (Gr.nodes[origin_node]['y'], Gr.nodes[origin_node]['x'])
        distance_points = distance.geodesic(coords_1, coords_2).km*1000         
        if distance_points > 50 :
            o_node = ox.distance.nearest_nodes(G_walk, [coords_1[1]],[coords_1[0]])[0]
            Gr.add_node(o_node,x=G_walk.nodes[o_node]['x'],y=G_walk.nodes[o_node]['y'])
            walk_length = nx.shortest_path_length(G_walk, o_node, origin_node, weight='length')
            Gr.add_edge(o_node,origin_node,length=walk_length, oneway= False, highway='residential', lanes=2, reversed=False,speed_kph=drive_speed,weight=0, travel_time=walk_length*60/drive_speed)  
            Gr.add_edge(origin_node,o_node,length=walk_length, oneway= False, highway='residential', lanes=2, reversed=False,speed_kph=drive_speed,weight=0, travel_time=walk_length*60/drive_speed)  
            origin_node = o_node

        for j in range(n):
            destination = pts[j]
            destination_node = ox.distance.nearest_nodes(Gr, [destination[1]], [destination[0]])[0]
            coords_1 = (destination[0],destination[1])
            coords_2 = (Gr.nodes[destination_node]['y'], Gr.nodes[destination_node]['x'])
            distance_points = distance.geodesic(coords_1, coords_2).km*1000
            if distance_points > 50 :
                d_node = ox.distance.nearest_nodes(G_walk, [coords_1[1]],[coords_1[0]])[0]
                Gr.add_node(d_node,x=G_walk.nodes[d_node]['x'],y=G_walk.nodes[d_node]['y'])
                walk_length = nx.shortest_path_length(G_walk, d_node, destination_node, weight='length')
                Gr.add_edge(d_node,destination_node,length=walk_length, oneway= False, highway='residential', lanes=2, reversed=False,speed_kph=drive_speed,weight=0, travel_time=walk_length*60/drive_speed)  
                Gr.add_edge(destination_node,d_node,length=walk_length, oneway= False, highway='residential', lanes=2, reversed=False,speed_kph=drive_speed,weight=0, travel_time=walk_length*60/drive_speed)  
                destination_node = d_node
    return Gr

def CalcRoutes_module(puntos,m_buses,root_dir,CO2km):
      network = pdn.network.Network.from_hdf5(root_dir + 'data/input_data_MCM/' + f'networks/drive_net.h5')
      ################################################
      # Calculando la matriz de distancias
      ################################################
      n = len(puntos)
      C = np.zeros((n,n))

      print(puntos)
      df = pd.DataFrame(puntos, columns=['lat', 'lon'])
      df.to_csv(root_dir + 'data/input_data_MCM/' + 'coords_stops.csv', index=False)

      """
      for i in range(0, n):
          for j in range(0, len(puntos)):
              C[i,j] = distance.distance(puntos[i], puntos[j]).km
      """

      ori_coord = puntos[0]
      print('points:')
      print(puntos)
      print()
      print()
      print('Generating graph...')
      lats, lons = map(list, zip(*puntos))
      max_lat = max(lats)
      min_lat = min(lats)      
      max_lon = max(lons)
      min_lon = min(lons)
      t0 = time.time()      
      """
      df = pd.DataFrame({'lat':lats, 'lon':lons})
      gdf = geopandas.GeoDataFrame(
          df, geometry=geopandas.points_from_xy(lons, lats), crs="EPSG:4326"
      )
      poly_convex_hull = gdf['geometry'].unary_union.convex_hull 
      G = ox.graph_from_polygon(poly_convex_hull, network_type="drive", simplify=True, retain_all=False)
      """
      print('bbox:')
      rel_margins_north = 0.5
      rel_margins_south = 0.8
      rel_margins_east = 0.6
      rel_margins_west = 0.8
      north = max_lat + (max_lat - min_lat) * rel_margins_north
      south = min_lat - (max_lat - min_lat) * rel_margins_south
      east = max_lon + (max_lon - min_lon) * rel_margins_east
      west = min_lon - (max_lon - min_lon) * rel_margins_west
      print(north, south, east, west)
      print()
      cf = '["highway"~"motorway|trunk|primary|secondary|residential|motorway_link|trunk_link|primary_link|secondary_link"]'
      #cf = '["highway"~"motorway"]'
      #cf = '["highway"~"motorway|motorway_link|primary"]'
      #cf = '["bus"="yes"]'
      #G = ox.graph_from_point(ori_coord, dist=40000, network_type="drive", simplify=True, retain_all=False)
      #G = ox.graph_from_bbox(north, south, east, west, network_type="drive", simplify=False) 
      G = ox.graph_from_bbox(north, south, east, west, network_type="drive", simplify=False, custom_filter=cf) 
      #fig, ax = ox.plot_graph(G,edge_linewidth=0.2)
      #fig.show()


      t1 = time.time()

      print('Graph completed!')
      print('time: ', (t1-t0)/60)
      print()
      print('Adding edge speeds, lengths and travelling speeds...')
      #hwy_speeds = {"residential": 30, "secondary": 30, "tertiary": 30}
      #hwy_speeds = {"residential": 20, "unclassified": 30, "maxspeed": 100 }
      #hwy_speeds = {"residential": 80, "unclassified": 60, "maxspeed": 100 }
      #hwy_speeds = {"primary": 100, "residential": 60, "unclassified": 50, "maxspeed": 100 }
      hwy_speeds = {"motorway": 100, "trunk": 100, "primary": 100, "residential": 60, "unclassified": 50, "maxspeed": 100 }
      #hwy_speeds = {"motorway": 120, "trunk": 100, "primary": 100, "residential": 50, "unclassified": 50, "maxspeed": 120 }
      G = ox.add_edge_speeds(G, hwy_speeds)
      #G = ox.add_edge_speeds(G)
      G = ox.add_edge_travel_times(G)
      G = ox.distance.add_edge_lengths(G)
      print('Adding edge speeds, lengths and travelling speeds completed!')

      """
      print('Removing oneway ends...')
      G = remove_oneway_ends(G)
      print('Removing oneway ends done!')
      print('Adding missing connections...')
      G = check_conn_dirty_fix(G,puntos,[north,south,east,west])
      print('Adding missing connections done!')    
      """
      n = len(puntos)
      C = np.zeros((n,n))
      
      permut = list(permutations(puntos, 2))
      permut_index = list(permutations(range(n), 2))

      print()
      print('Calculating distance matrix...')
      t0=time.time()
      #lista=[]
      
      # The following loop is somewhat faster than the old one (below) ##############################
      index_old = 1
      for i in range(len(permut)):
        pi = permut_index[i]
        origin, destination = permut[i]
        if pi[0] != index_old:
           origin_node = ox.distance.nearest_nodes(G, [origin[1]], [origin[0]])[0]
        destination_node = ox.distance.nearest_nodes(G, [destination[1]], [destination[0]])[0]
        print('origin: ', origin[0],origin[1])
        print('destination: ', destination[0],destination[1])
        try:        
            path_length = nx.shortest_path_length(G, origin_node, destination_node, weight='length')
        except:
            data = [[origin[1], origin[0], destination[1], destination[0]]]
            # Create the pandas DataFrame
            df_coords = pd.DataFrame(data, columns=['O_Long', 'O_Lat', 'D_Long', 'D_Lat'])
            path_length = network.shortest_path_lengths(
                            network.get_node_ids(df_coords.O_Long,df_coords.O_Lat),
                            network.get_node_ids(df_coords.D_Long,df_coords.D_Lat),
                            imp_name='distance'
                        )
            path_length = path_length[0]


        C[pi[0]][pi[1]] = path_length/1000
        #lista.append([origin_node,destination_node,pi[0],pi[1]])
        index_old = pi[0]
      ##################################################################################################  
        
      """
      for i in range(n):
        origin = puntos[i]
        origin_node = ox.distance.nearest_nodes(G, [origin[1]], [origin[0]])[0]
        for j in range(n):
          destination = puntos[j]
          destination_node = ox.distance.nearest_nodes(G, [destination[1]], [destination[0]])[0]
          #Get the shortest path
          print('origin: ', origin[0],origin[1])
          print('destination: ', destination[0],destination[1])
          path_length = nx.shortest_path_length(G, origin_node, destination_node, weight='length')
          C[i][j] = path_length/1000
          #lista.append([origin_node,destination_node,i,j])
      """
      
      print('Distance matrix calculated!')
      t1=time.time()
      print('Total time: ', (t1-t0)/60)
      print()
      #df = pd.DataFrame(lista)
      #df.to_csv('C:/Users/gfotidellaf/repositories/UI_SCP/assets/data/test_0.csv',index=False)
      # Mostrando la matriz de distancias
      print('Distance matrix is:\n')
      print(np.round(C,4))
      n = np.shape(C)[0]

      model=Model('mTSP')

      ## Variable xij
      stops=range(n)
      x=model.binary_var_matrix(keys1=stops,keys2=stops,name='x')
      ## Varible ui
      u=model.integer_var_list(keys=stops, lb=0, ub=n,name='u')

      model.minimize(model.sum(C[i,j] * x[i,j] for i in stops for j in stops))
      model.add_constraint(model.sum(x[0 , j] for j in stops if j>0)==m_buses)
      model.add_constraint(model.sum(x[i , 0] for i in stops if i>0)==m_buses)

      for i in stops[1:]:
              model.add_constraint(model.sum(x[i , j] for j in stops )==1)

      for j in stops[1:]:
              model.add_constraint(model.sum(x[i , j] for i in stops )==1)

      for i in stops:
              model.add_constraint(x[i,i] == 0)

      #Ms = int(n/m_buses) # Ms = max number of stops visited by each bus.
                          # Choose Ms = n/m_buses for a balanced load distribution among buses
      #Ms = n
      Ms = int(n/m_buses) + 1 
      for i in stops[1:]:
          for j in stops[1:]:
              if i != j:
                model.add_constraint(u[i]-u[j]+ Ms * x[i,j] <= Ms -1)
                #model.add_constraint(u[i]-u[j] + 1 <= (Ms -1)*(1-x[i,j]) )

      model.add_constraint(u[0] == 1)
      for i in stops[1:]:
            model.add_constraint(u[i] >= 2)
      for i in stops[1:]:
            model.add_constraint(u[i] <= n) #---> Ms or n? With Ms algorithm keeps searching...


      # ## Solve
      solution = model.solve(log_output=False)
      print('Objective function:')
      print(solution.get_objective_value())
      #solution.display()
      X_sol = np.zeros((n,n))
      for index, dvar in enumerate(solution.iter_variables()):
          if dvar.to_string().split('_')[0] == 'x':
            row, col = dvar.to_string().split('_')[1:]
            X_sol[int(row),int(col)] = solution[dvar]
            #print(index, dvar, dvar.to_string().split('_'), solution[dvar], solution.get_var_value(dvar))
      ruta_EZ0, Xout = extract_RoutesMat(X_sol, stops, n, m_buses)
      check_Nbuses(Xout)
      check_UniqueStops(Xout)

      print(ruta_EZ0)
      #print(Xout)

      ruta_EZ0 = list(ruta_EZ0.values())
      cumul_dist_routes = []
      for ii in range(len(ruta_EZ0)):
          dist_temp = []
          for jj in range(len(ruta_EZ0[ii])-1):
              i0 = ruta_EZ0[ii][jj]
              i1 = ruta_EZ0[ii][jj+1]
              dist_temp.append(C[i0][i1])
          cumul_dist_routes.append(sum(dist_temp))
      print('Route cumulative lengths:')
      print(cumul_dist_routes)
      ind_max = cumul_dist_routes.index(max(cumul_dist_routes))
      ind_min = cumul_dist_routes.index(min(cumul_dist_routes))
      print()

      stop = 0
      cont = 0
      converged = 0
      objective = []
      # generate 1D list:
      ruta_EZ0_old = [0 for row in ruta_EZ0 for item in row]
      while not stop:
          if solution:
              X_sol = np.zeros((n,n))
              for index, dvar in enumerate(solution.iter_variables()):
                  if dvar.to_string().split('_')[0] == 'x':
                    row, col = dvar.to_string().split('_')[1:]
                    X_sol[int(row),int(col)] = solution[dvar]
                    #print(index, dvar, dvar.to_string().split('_'), solution[dvar], solution.get_var_value(dvar))
              ruta_EZ0, Xout = extract_RoutesMat(X_sol, stops, n, m_buses)
              print('new routes:')
              print(ruta_EZ0)

              # find index of route with max cumulative length #######################
              # find index of route with min cumulative length
              ruta_EZ0 = list(ruta_EZ0.values())
              cumul_dist_routes = []
              for ii in range(len(ruta_EZ0)):
                  dist_temp = []
                  for jj in range(len(ruta_EZ0[ii])-1):
                      i0 = ruta_EZ0[ii][jj]
                      i1 = ruta_EZ0[ii][jj+1]
                      dist_temp.append(C[i0][i1])
                  cumul_dist_routes.append(sum(dist_temp))
              print('Route cumulative lengths:')
              print(cumul_dist_routes)
              ind_max = cumul_dist_routes.index(max(cumul_dist_routes))
              ind_min = cumul_dist_routes.index(min(cumul_dist_routes))
              ########################################################################

              if cont < cont_limit and not converged:
                C_max_list = []
                x_max_list = []
                for ii in range(len(ruta_EZ0[ind_max])-1):
                    i0 = ruta_EZ0[ind_max][ii]
                    i1 = ruta_EZ0[ind_max][ii+1]
                    C_max_list.append(C[i0][i1])
                    x_max_list.append((i0,i1))

                C_min_list = []
                x_min_list = []
                for ii in range(len(ruta_EZ0[ind_min])-1):
                    i0 = ruta_EZ0[ind_min][ii]
                    i1 = ruta_EZ0[ind_min][ii+1]
                    C_min_list.append(C[i0][i1])
                    x_min_list.append((i0,i1))

                model.add_constraint(  ( (model.sum(C_max_list[ii]*x[x_max_list[ii][0],x_max_list[ii][1]] for ii in range(len(x_max_list))) - model.sum(C_min_list[ii]*x[x_min_list[ii][0],x_min_list[ii][1]] for ii in range(len(x_min_list)))) <= tol_dist*model.sum(C_max_list[ii]*x[x_max_list[ii][0],x_max_list[ii][1]] for ii in range(len(x_max_list))) ) )
                #model.add_constraint(model.sum(C_max_list[ii]*x[x_max_list[ii][0],x_max_list[ii][1]] for ii in range(len(x_max_list))) <= 60 )
                #model.add_constraint(model.sum(C_min_list[ii]*x[x_min_list[ii][0],x_min_list[ii][1]] for ii in range(len(x_min_list))) >= 1 )
                #print('indices max:')
                #print(x_max_list)
                #print('indices min:')
                #print(x_min_list)

                try:
                    solution0 = model.solve(log_output=False)
                    #solution = model.solve(clean_before_solve=True,log_output=False) #---> try this
                    print('Objective function:')
                    print(solution0.get_objective_value())
                    objective.append(solution0.get_objective_value())
                    solution = solution0
                    constr_exists = 1
                    cont_constr = 0
                    """
                    # does the following show the number of cumulated constraints?
                    while(constr_exists is not None):
                        print('constraint: ')
                        constr_exists = model.get_constraint_by_index(cont_constr)
                        print(constr_exists)
                        cont_constr+=1
                    """
                    dmax = np.sum(np.array(C_max_list))
                    print('Cumulative distance of route covering Max dist:')
                    print(dmax)
                    dmin = np.sum(np.array(C_min_list))
                    print('Cumulative distance of route covering Min dist:')
                    print(dmin)
                    print()

                    # flatten list of routes to 1D list:
                    ruta_EZ0 = [item for row in ruta_EZ0 for item in row]
                    # check whether calculation has reached convergence
                    if ruta_EZ0 == ruta_EZ0_old:
                      converged = 1
                    ruta_EZ0_old = ruta_EZ0

                except:
                    print('Solution not found!!!')
                    stop = 1

              else:
                print('Solution converged or maximum number of iteration reached!')
                stop = 1

              cont+=1

          else:
              print('Solution not found at iteration: ', cont+1)
              stop = 1
      #solution.display()
      #solution.get_objective_value()

      """
      # CO2 calc and route visualization #############################################
      routes = []
      total_CO2 = 0.0
      coords_routes = []
      for ii in range(len(ruta_EZ0)):
          dist_temp = []
          length_route_i = 0
          coords_route_i = []
          for jj in range(len(ruta_EZ0[ii])-1):
                i0 = ruta_EZ0[ii][jj]
                i1 = ruta_EZ0[ii][jj+1]
                origin = puntos[i0]
                destination = puntos[i1]
                origin_node      = ox.distance.nearest_nodes(G, [origin[1]], [origin[0]])[0]
                destination_node = ox.distance.nearest_nodes(G, [destination[1]], [destination[0]])[0]
                route_i = nx.shortest_path(G, origin_node, destination_node, weight='length')
                length_route_i_temp = nx.shortest_path_length(G, origin_node, destination_node, weight='length')
                dist_temp.append(route_i)
                length_route_i = length_route_i + length_route_i_temp
                for node_id in route_i:
                    Lon = G.nodes[node_id]['x'] #lon
                    Lat = G.nodes[node_id]['y'] #lat
                    coords_route_i.append((Lat,Lon))
          routes.append(dist_temp)
          coords_routes.append(coords_route_i)
          print('Length route (m) '+str(ii)+':',length_route_i)
          print('CO2 emissions of route '+str(ii)+':',(1./1000)*length_route_i*CO2km)
          total_CO2 = total_CO2 + (1./1000)*length_route_i*CO2km
          print()
      print()
      print('Total CO2 emissions: ',total_CO2)
      """

      print('Start calculation routes with Pandana...')
      # Implementation with Pandana ################################################
      network = pdn.network.Network.from_hdf5(root_dir + 'data/input_data_MCM/' + f'networks/drive_net.h5')
      routes = []
      total_CO2 = 0.0
      coords_routes = []
      length_routes = []
      for ii in range(len(ruta_EZ0)):
          dist_temp = []
          length_route_i = 0
          coords_route_i = []
          for jj in range(len(ruta_EZ0[ii])-1):
                i0 = ruta_EZ0[ii][jj]
                i1 = ruta_EZ0[ii][jj+1]
                origin = puntos[i0]
                destination = puntos[i1]

                data = [[origin[1], origin[0], destination[1], destination[0]]]
                # Create the pandas DataFrame
                df_coords = pd.DataFrame(data, columns=['O_Long', 'O_Lat', 'D_Long', 'D_Lat'])
                ori_node = network.get_node_ids(df_coords.O_Long,df_coords.O_Lat)
                dest_node = network.get_node_ids(df_coords.D_Long,df_coords.D_Lat)
                route_i = network.shortest_paths(ori_node, dest_node, imp_name='distance')[0]
                
                #added to obtain the length of the route 11/11/2024
                length_route_i_temp = network.shortest_path_lengths(ori_node, dest_node, imp_name='distance')[0]
                print('partial route length: ',length_route_i_temp)
                length_route_i = length_route_i + length_route_i_temp
                print('cumulative length of route '+str(ii)+':',length_route_i)
                ####################################################
                
                network.nodes_df['id'] = network.nodes_df.index
                df = network.nodes_df.copy()
                mask = df['id'].isin(route_i)
                path_coords = df[mask]
                path_coords = path_coords.reindex(route_i)
                for index, row in path_coords.iterrows():
                    #print(row['x'], row['y'])
                    #coords_route_i.append((Lat,Lon))
                    coords_route_i.append((row['y'],row['x']))
          coords_routes.append(coords_route_i)
          length_routes.append(length_route_i)
          #print('Coords of route ',ii,':')
          #print(coords_route_i)
          #print()

      #print(coords_routes)
      #root_dir + 'data/input_data_MCM/'
      import csv

      with open(root_dir + 'data/input_data_MCM/' + 'routes_coordinates.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for i, route in enumerate(coords_routes):
            writer.writerow([i])  # route index
            writer.writerows(route)
            writer.writerow([])  # empty row to separate routes
      
      return ruta_EZ0, coords_routes, G, length_routes