from flask import Flask, request, jsonify
from array_compressor import compress_array, decompress_array, decompress_array_nodecode

from agents_locator import convertAgentsMapToDataFrame, convertAgentsMapToDataFrameBatch

import rasterio

from yield_module import CropModel

import geopandas as gpd
import pandas as pd

# a function to generate all yield by latlon

import os
from tqdm import tqdm
import numpy as np

from wofost.wofost import InterfaceWOFOST
from paraallo.paraallo import InterfaceParaAllo
from apsim.apsim import InterfaceAPSIM
from map_module.yieldmapper import YieldMapGenerator

app = Flask(__name__)

model = CropModel()

def getIrrigation(data, irri_file):
    
    # make latlon set
    coordinateList = [(data['lons'][i], data['lats'][i]) for i in range(len(data))]
        
    with rasterio.open(irri_file) as src:
        
        # sampling yield value from baseyield raster
        data['irri'] =  [x[0] for x in src.sample(coordinateList)]
        
    return data

def calculateCropProduct(data, crop_list, area_col):
    
    area_array = np.asarray(data[area_col])
    
    for crop in crop_list:
                                    
        data[crop] = data[crop] * data[area_col]
        
    return data


def calculateCropYield(data, col_lat, col_lon):
    
    # Initializa Crop Models
    # Init WOFOST
    wofost = InterfaceWOFOST(os.getcwd())
    
    # Init APSIM
    apsim = InterfaceAPSIM(os.getcwd())
    
    # Init ParaRubberAllometry
    para_allo = InterfaceParaAllo()
    
    
    xmin, ymin, xmax, ymax = 97.3758964376, 5.69138418215, 105.589038527, 20.4178496363
    
    #crop_list = ['rice','maize','cassava', 'sugarcane', 'oilpalm', 'pararubber']
    
    crop_list = ['ri1','ri2', 'ri3', 'ri4', 'mp','cf','op', 'sc','rb']
    
    wofost_crop = ['ri1','ri2', 'ri3', 'ri4', 'mp','cf']
    
    apsim_crop = ['op', 'sc']
    
    allo_crop = ['rb']
    
    # Filter the data to only include points within the bounding box
    filtered_data = data[(data['lon'] >= xmin) & (data['lon'] <= xmax) & (data['lat'] >= ymin) & (data['lat'] <= ymax)]
    
    for crop in tqdm(crop_list):
        
        crop_yield_list = []
        
        for i in range(len(filtered_data)):

            #print(f'simulating {crop} yield {i+1}/{len(filtered_data)}')

            lat = filtered_data[col_lat][i]
            lon = filtered_data[col_lon][i]
            
            if crop in wofost_crop:
                
                crop_yield_list.append(wofost.get_sim_product(crop, lat, lon))
                
            elif crop in apsim_crop:
                
                crop_yield_list.append(apsim.get_sim_product(crop, lat, lon))
                
            else:
                
                crop_yield_list.append(para_allo.get_sim_product(crop, lat, lon))
        
        filtered_data[crop] = crop_yield_list
            
    return filtered_data
        
    
def fix_missing_agent2(data, n_agent, id_col = 'ids'):
    
    data_columns = data.columns.tolist()
    
    data_dict = {}
    
    for col in data_columns:
        
        data_dict[col] = []
    
    for agent_i in range(n_agent):
        
        if agent_i in data[id_col].tolist():
            
            for col in data_columns:
                
                data_dict[col].append(data[col][agent_i])
            
        else:
            
            data_dict[id_col].append(agent_i)
            
            for col in data_columns[1:]:
                
                data_dict[col].append(0.0)
            
    return pd.DataFrame(data_dict)    
# ===========================================================================================================
    
    
@app.route('/crop_yield', methods=['POST'])
def crop_yield():
    print("CROP YEILD START....")
    # RECEIVE ARGUMENTS
    rain = request.args.get('rain')
    temp = request.args.get('temp')
    diss = request.args.get('diss')
    n_agent = request.args.get('n_agent')
    #data = request.get_json()['data']

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    file_content = file.read()
    

    # CONVERT DATA

    data_dtype = 'int16'
    data_shape = (3144, 4726)

    map_data = decompress_array_nodecode(file_content, dtype=data_dtype, shape=data_shape)
    print(map_data.shape)

    #print(file_content)

    rain = eval(rain)
    temp = eval(temp)
    diss = eval(diss)
    n_agent= eval(n_agent)


    #map_data = decompress_array(data_map, dtype=data_dtype, shape=data_shape)

    # PROCESS DATA ================================================================

    
    agents = convertAgentsMapToDataFrame(map_data)
    agents = getIrrigation(agents, './gis/irrigation_map.tif')
    result = model.get_baseyield_1(agents)
    result = model.vary_baseyield_2(result)
    #result = model.shock_temp_3(result, (15, 35))
    result = model.shock_temp_3(result, (temp[0], temp[1]))
    #result = model.shock_rain_4(result, (1800, 2200))
    result = model.shock_rain_4(result, (rain[0], rain[1]))
    
    if diss:
        result = model.shock_disaster_5(result)
        result = model.clean_agent_data(result, is_disaster=diss)
    else:
        result = model.clean_agent_data(result, is_disaster=diss)
        
    result = fix_missing_agent2(result, n_agent, id_col='ids')
    
    #data_prod = calculateCropProduct(result, ['ri1','ri2', 'ri3', 'ri4', 'mp','cf','op', 'sc','rb'], 'areas')

    return jsonify({"status": "Success", "data":result.to_json()})

@app.route('/crop_yield_batch', methods=['POST'])
def crop_yield_batch():
    print("CROP YEILD START....")
    # RECEIVE ARGUMENTS
    rain = request.args.get('rain')
    temp = request.args.get('temp')
    diss = request.args.get('diss')
    ij   = request.args.get('ij')
    shape = request.args.get('shape')
    n_agent = request.args.get('n_agent')
    #data = request.get_json()['data']

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    file_content = file.read()

    # CONVERT DATA
    
    ij = eval(ij)
    shape = eval(shape)
    print(shape)
    i,j = ij[0], ij[1]
    
    data_dtype = 'int16'
    data_shape = (shape[0], shape[1])

    map_data = decompress_array_nodecode(file_content, dtype=data_dtype, shape=data_shape)
    print(map_data.shape)

    #print(file_content)

    rain = eval(rain)
    temp = eval(temp)
    diss = eval(diss)
    n_agent= eval(n_agent)

    #map_data = decompress_array(data_map, dtype=data_dtype, shape=data_shape)

    # PROCESS DATA ================================================================
    
    #agents = convertAgentsMapToDataFrame(map_data)
    agents = convertAgentsMapToDataFrameBatch(map_data, i, j)
    agents = getIrrigation(agents, './gis/irrigation_map.tif')
    result = model.get_baseyield_1(agents)
    result = model.vary_baseyield_2(result)
    #result = model.shock_temp_3(result, (15, 35))
    result = model.shock_temp_3(result, (temp[0], temp[1]))
    #result = model.shock_rain_4(result, (1800, 2200))
    result = model.shock_rain_4(result, (rain[0], rain[1]))
    
    if diss:
        result = model.shock_disaster_5(result)
        result = model.clean_agent_data(result, is_disaster=diss)
    else:
        result = model.clean_agent_data(result, is_disaster=diss)
        
    result = fix_missing_agent2(result, n_agent, id_col='ids')
    
    #data_prod = calculateCropProduct(result, ['ri1','ri2', 'ri3', 'ri4', 'mp','cf','op', 'sc','rb'], 'areas')

    return jsonify({"status": "Success", "data":result.to_json()})

@app.route('/crop_sim')
def crop_sim():
    print("CROP SIMULATION START....")
    points = gpd.read_file('./gis/sampling_points.shp')
    result_y = calculateCropYield(points, 'lat', 'lon')
    mapper = YieldMapGenerator(os.path.join(os.getcwd(),'./yield_maps'))
    mapper.generateMaps(result_y)
    return jsonify("Success")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001,debug=True)