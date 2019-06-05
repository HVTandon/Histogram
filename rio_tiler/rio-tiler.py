import utils
import json

histogram_data={}

stats=utils.raster_get_stats('DSM1.tif')

histogram_data['histogram']=stats
#histogram_data['band number '+str(i)]=stats

#print(histogram_data)

with open('histogram.json', 'w') as f:
    json.dump(histogram_data, f, indent=4)