import numpy as np
import osmnx as ox
import pandas as pd
import random
import sklearn
from sklearn.cluster import KMeans
import geopy.distance
from scipy import stats
from scipy.interpolate import interp2d

import scipy.ndimage.filters as filters
import scipy.ndimage.morphology as morphology

from matplotlib import pyplot as plt
#from google.colab import drive
#drive.mount('/content/drive',  force_remount=True)

"""
#n_clusters = 23
n_clusters = 19
cutoff = 0.8 # cutoff for maximum density: take maxima which are at least cutoff*max
root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/data/'
workers_DF = pd.read_csv(root_dir + "workers.csv", encoding='latin-1')
stops_DF = pd.read_csv(root_dir + "all_bus_stops.csv", encoding='latin-1') 
#dist_tol = 1000 # distance tolerance for bus_stop from cluster center (in meters)


ori_lat = 43.13525255625577
ori_lon = -2.080054227169231
"""


def detect_local_minima(arr):
    # https://stackoverflow.com/questions/3684484/peak-detection-in-a-2d-array/3689710#3689710
    """
    Takes an array and detects the troughs using the local maximum filter.
    Returns a boolean mask of the troughs (i.e. 1 when
    the pixel's value is the neighborhood maximum, 0 otherwise)
    """
    # define a connected neighborhood
    # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology.html#generate_binary_structure
    neighborhood = morphology.generate_binary_structure(len(arr.shape),2)
    # apply the local minimum filter; all locations of minimum value
    # in their neighborhood are set to 1
    # http://www.scipy.org/doc/api_docs/SciPy.ndimage.filters.html#minimum_filter
    local_min = (filters.minimum_filter(arr, footprint=neighborhood)==arr)
    # local_min is a mask that contains the peaks we are
    # looking for, but also the background.
    # In order to isolate the peaks we must remove the background from the mask.
    #
    # we create the mask of the background
    background = (arr==0)
    #
    # a little technicality: we must erode the background in order to
    # successfully subtract it from local_min, otherwise a line will
    # appear along the background border (artifact of the local minimum filter)
    # http://www.scipy.org/doc/api_docs/SciPy.ndimage.morphology.html#binary_erosion
    eroded_background = morphology.binary_erosion(
        background, structure=neighborhood, border_value=1)
    #
    # we obtain the final mask, containing only peaks,
    # by removing the background from the local_min mask
    detected_minima = local_min ^ eroded_background
    return np.where(detected_minima)


def FindStops(workers_df, stops_df, n_clusters, cutoff):
    #lat_lon = workers_df[['O_lat', 'O_long']][::n_skip] # take every n elements
    workers_lat_lon = workers_df[['O_lat', 'O_long']].values.tolist()
    stops_lat_lon = stops_df[['stop_lat','stop_lon']].to_numpy()    
    model = KMeans(n_clusters=n_clusters)
    # fit the model
    model.fit(workers_lat_lon)
    # assign a cluster to each example
    yhat = model.predict(workers_lat_lon)

    # retrieve unique clusters
    clusters = np.unique(yhat)
    centers = np.array(model.cluster_centers_)

    highDens_points = []
    local_maxima_all_clusters = []
    for cluster in clusters:
        X = []
        Y = []
        # get row indexes for samples with this cluster
        row_ix = np.where(yhat == cluster)
        # create scatter of these samples
        # get coordinates of workers of this cluster ##################################
        temp_array = np.array(workers_lat_lon)[row_ix[0]]
        Lats = [temp_array[i,0] for i in range(len(temp_array))]
        Lons = [temp_array[i,1] for i in range(len(temp_array))]
        ###############################################################################

        minLat = min(Lats)
        maxLat = max(Lats)
        minLon = min(Lons)
        maxLon = max(Lons)

        #xy = np.vstack([Y,X])
        xy = np.vstack([Lons,Lats]) 
        kernel = stats.gaussian_kde(xy)
        x,y = np.mgrid[minLat:maxLat:150j, minLon:maxLon:150j]  # 150 x 150 grid for plotting
        z = kernel.pdf(np.array([y.ravel(),x.ravel()])).reshape(x.shape)

        # find absolute max: ##########################################################
        indmax = np.unravel_index(np.argmax(z, axis=None), z.shape)  # returns a tuple
        highestDP = (x[indmax],y[indmax])
        highDens_points.append(highestDP)
        ###############################################################################

        print('Point density function for cluster: ', str(cluster))
        fig,ax = plt.subplots()
        ax.contourf(y, x, z, levels=20)
        ax.axis('scaled')
        #plt.scatter(Y,X, marker = 'o', alpha=0.5, color='white')
        plt.scatter(Lons,Lats, marker = 'o', alpha=0.5, color='white')
        plt.scatter(highestDP[1], highestDP[0], s=48, marker="x", color='black')
        #plt.savefig('/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/Point_density_cluster_'+str(cluster)+'.png')
        plt.show()

        # find local maxima
        local_maxima_locations = detect_local_minima(-z)
        print('Local maxima for cluster: ', cluster)
        print(z[local_maxima_locations])
        maxs = z[local_maxima_locations]
        ind_maxs = [i for i in range(len(maxs)) if maxs[i]/max(maxs)>=cutoff]
        #for i_max in range(len(local_minima_locations[0])):
        print('Local maxima within 20% of absolute max:')
        local_maxima_cluster_i = []
        for i_max in range(len(ind_maxs)):
            i_tmp = ind_maxs[i_max]
            x_coord = x.T.ravel()[local_maxima_locations[0][i_tmp]]
            y_coord = y.ravel()[local_maxima_locations[1][i_tmp]]
            print(x_coord, y_coord)
            local_maxima_cluster_i.append((x_coord,y_coord))
        print()
        local_maxima_all_clusters.append(local_maxima_cluster_i)

    # generate list of closest bus stops ######################################
    bus_stops = []
    center_ind = []
    for i in range(len(local_maxima_all_clusters)):
      for j in range(len(local_maxima_all_clusters[i])):
          lat = local_maxima_all_clusters[i][j][0]
          lon = local_maxima_all_clusters[i][j][1]
          print('local maxima cluster: ',i)
          print(lat,lon)
          try:
              # find closest bus stop
              ref = np.array([lat,lon])
              ref = np.tile(ref,(len(stops_lat_lon),1)) # generate replicas of ref point
              #d = [sum((p-q)**2)**0.5 for p, q in zip(ref, stops_lat_lon)] # calculate distance of each bus stop to ref point
              d = [geopy.distance.geodesic((p[0],p[1]), (q[0],q[1])).km for p, q in zip(ref, stops_lat_lon)] # calculate distance of each bus stop to ref point

              ind_min = d.index(min(d)) # find index of closest bus stop
              x = stops_lat_lon[ind_min][0]
              y = stops_lat_lon[ind_min][1]
              bus_stops.append((x, y))

              center_ind.append(i)
              print('bus stop found:')
              print(x,y)

          except:
              print('WARNING: stops not found for cluster ',i)
              #print(centers[i])
              #print(highDens_points[i])
          print()
    ###########################################################################
          

    df = pd.DataFrame(bus_stops, columns =['Lat', 'Lon'])    
    return [df,model,yhat]

"""
bus_stops_df,model,yhat = FindStops(workers_DF, stops_DF, n_clusters, cutoff)
bus_stops_df.to_csv(root_dir + 'data/INPUT_stops.csv', index=False)
bus_stops_arr = bus_stops_df[['Lat','Lon']].to_numpy()
tmp_df = workers_DF[['O_lat', 'O_long']].to_numpy()
plt.scatter(tmp_df[:, 0], tmp_df[:, 1], c=yhat, s=20, cmap='viridis')
plt.scatter(model.cluster_centers_[:, 0], model.cluster_centers_[:, 1], s = 100, c = 'black', marker='x')
plt.scatter(bus_stops_arr[:, 0], bus_stops_arr[:, 1], s=70, facecolors='none', edgecolors='black', marker='s' )
plt.show()
"""
