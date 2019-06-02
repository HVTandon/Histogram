import rasterio as rio
from rasterio.windows import Window
import numpy as np
import matplotlib.pyplot as plt
import json

def hist(lidar_dem_im, band_num, maxi, mini):
    # Open data and assign negative values to nan
    
        print(lidar_dem_im.dtype)
        # The .ravel method turns an 2-D numpy array into a 1-D vector
        lidar_dem_hist = lidar_dem_im.ravel()
        l= len(lidar_dem_hist)
        print(l)
        # Remove all negative values
        lidar_dem_hist=lidar_dem_hist[lidar_dem_hist>=0]
    print(lidar_dem_im.shape)
    
    bins=int(maxi)-int(mini)+1
    
    lists,bins=hist(lidar_dem_hist, bins)
    return lists,bins
    
    #creating json file and adding data to histogram.json

    
with open('metadata.json', 'r') as f:
    data2=json.load(f)

band_num=data2['numband']

for ty in data2['statistics']:
    band_min.append(ty['min'])
    band_max.append(ty['max'])

histogram_data={}

with rio.open('index.tif') as src:
    for i in range(1,band_num+1):
        lidar_dem_im = src.read(i)
        lists,bins=hist(lidar_dem_im, i, band_max[i-1], band_min[i-1])
        histogram_data[i]={
            'band number'=i,
            'lists'=lists,
            'bins'=bins
        }

with open('histogram.json', 'w') as fp:
    json.dump(histogram_data,fp)