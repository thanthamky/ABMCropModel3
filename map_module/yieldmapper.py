import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.interpolate import griddata
import rasterio
from rasterio.transform import from_origin
import os

class YieldMapGenerator:
    
    
    def __init__(self, map_path):
        
        #self.crop_list = ['rice','maize','cassava', 'sugarcane', 'oilpalm', 'pararubber']
        self.crop_list = ['ri1','ri2', 'ri3', 'ri4', 'mp','cf','op', 'sc','rb']
        self.yield_map_folder = map_path
        ...
        
    def generateMaps(self, data):
        
        lat_list = data['lat']
        lon_list = data['lon']
        
        for crop in self.crop_list:
            
            print(f'generate {crop} map ...', end='')
            
            self.make_yield_map(lat_list, lon_list, data[crop], os.path.join(self.yield_map_folder, crop+'.tif'))
            
            print(f'DONE!', end='\n')
            
            
    def make_yield_map(self, list_lat, list_lon, list_value, out_file):

        #thailand_bbox
        xmin, ymin, xmax, ymax = 97.3758964376, 5.69138418215, 105.589038527, 20.4178496363

        # Thailand map dimension
        width = 1020
        height = 1812

        # Define the spatial reference of the output raster to WGS84
        crs = {'init': 'EPSG:4326'}

        # convert list to array
        list_lat = np.asarray(list_lat)
        list_lon = np.asarray(list_lon)
        list_value = np.asarray(list_value)

        # Create a grid of points within the bounding box
        x_grid, y_grid = np.meshgrid(np.linspace(xmin, xmax, width), np.linspace(ymin, ymax, height))

        # Interpolate the data onto the grid using linear interpolation
        z_interpolated = griddata((list_lon, list_lat), 
                                  list_value, 
                                  (x_grid, y_grid), 
                                  method='cubic', 
                                  fill_value=list_value.mean())

        #plt.imshow(z_interpolated)
        #plt.show()

        # Define the spatial resolution and affine transformation
        nrows, ncols = z_interpolated.shape
        xres = (xmax - xmin) / ncols
        yres = (ymax - ymin) / nrows
        affine = from_origin(xmin, ymax, xres, yres)

        # Write the interpolated data to the output raster using rasterio
        with rasterio.open(out_file, 'w', driver='GTiff', width=ncols, height=nrows, count=1, dtype=z_interpolated.dtype, crs=crs, transform=affine) as dst:
            dst.write(z_interpolated, 1)

        print(f'Make yield map at {out_file} success')