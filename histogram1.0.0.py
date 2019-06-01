import rasterio as rio
from rasterio.windows import Window
import numpy as np
import matplotlib.pyplot as plt

def hist(path, bins=10):
    steps=[]
    # Open data and assign negative values to nan
    with rio.open(path) as src:
        lidar_dem_im = src.read(1)#, window=Window(600, 1000, 500, 2500))
        print(lidar_dem_im.dtype)
        lidar_dem_hist = lidar_dem_im.ravel()
        l= len(lidar_dem_hist)
        print(l)
        if lidar_dem_hist[lidar_dem_hist<0]:
            lidar_dem_hist=lidar_dem_hist[False]
    print(lidar_dem_im.shape)
    
    # The .ravel method turns an 2-D numpy array into a 1-D vector
    # Remove the `nan` values for plotting
    
    #lidar_dem_hist = lidar_dem_hist[check]

    print(plt.hist(lidar_dem_hist))
    #mini=min(lidar_dem_hist)
    #maxi=max(lidar_dem_hist)
    #for i in range(bins+1):
    #    next_step=(mini+i*(maxi-mini)/bins)
    #    steps.append(next_step)    
    #lists,bins=np.histogram(lidar_dem_hist,bins)
    #print(lists, "-------------", bins)

hist('index.tif')
