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
    
    lists,bins=np.histogram(lidar_dem_hist, bins)
    return lists,bins
    
    #creating json file and adding data to histogram.json

with open('metadata.json', 'r') as f:
    data2=json.load(f)
    print("loaded")

band_num=data2['numband']

band_min=np.zeros(band_num)
band_max=np.zeros(band_num)
i=0
b="b"
for t in range(band_num):
    c=b+str(i)
    band_min[i]=data2['statistics'][c]['min']
    band_max[i]=data2['statistics'][c]['max']
    i+=1
print("band_max",band_max)
print("band_min",band_min)

histogram_data={}
mydict={}

#reading data of each band and writing histogram data in individual dictionaries
with rio.open('index.tif') as src:
    for i in range(1,band_num+1):
        lidar_dem_im = src.read(i)
        lists,bins=hist(lidar_dem_im, i, band_max[i-1], band_min[i-1])
        mydict={
            'lists':lists.tolist(),
            'bins':bins.tolist()
        }
        histogram_data['band number '+str(i)]=mydict

#print("------------------------------------HISTO----------------------------------",histogram_data)


with open('histogram.json', 'w') as fp:
    json.dump(histogram_data,fp, indent=4)