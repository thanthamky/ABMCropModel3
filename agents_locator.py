import numpy as np
from tqdm import tqdm
import pandas as pd
from array_compressor import compress_array, decompress_array


def convertAgentsMapToDataFrame(data):

    
    def convertPixelCoordinateToLatLon(row, col):
    
        x_min, y_min, x_max, y_max = 99.0853175160000035,15.0483699459999993, 100.8600274380000030,16.2031785890000002

        width, height = 4726, 3144

        lat = y_min + (row/height)*(y_max-y_min)
        lon = x_min + (col/width)*(x_max-x_min)

        return lat, lon
    
    def getAgentAreaDict(data):
    
        agent_area = np.unique(data, return_counts=True)

        areas = dict()

        for idx, area in zip(agent_area[0], agent_area[1]):

            areas[str(idx)] = area

        return areas
    
    # find Area of each agent ID
    idx_areas = getAgentAreaDict(data)
    
    # 
    ids = [int(idx) for idx in list(idx_areas.keys())]
    start_idx = ids.index(0)
    agent_ids = ids[start_idx:]
    
    #
    out = {'ids': [],'lats': [], 'lons': [], 'areas': []}
    
    for agent_i in tqdm(agent_ids):
        
        agent_zone = np.where(data == agent_i)
        
        row_med, col_med = np.median(agent_zone[0]), np.median(agent_zone[1])
        
        lat, lon = convertPixelCoordinateToLatLon(row_med, col_med)
        out['ids'].append(agent_i)
        out['lats'].append(lat)
        out['lons'].append(lon)
        out['areas'].append(idx_areas[str(agent_i)])
    
    return pd.DataFrame(out)

def convertAgentsMapToDataFrameBatch(data, i, j):

    
    def convertPixelCoordinateToLatLon(row, col):
    
        x_min, y_min, x_max, y_max = 99.0853175160000035,15.0483699459999993, 100.8600274380000030,16.2031785890000002

        width, height = 4726, 3144
        
        batch_row = row + i
        batch_col = col + j

        lat = y_min + (batch_row/height)*(y_max-y_min)
        lon = x_min + (batch_col/width)*(x_max-x_min)

        return lat, lon
    
    def getAgentAreaDict(data):
    
        agent_area = np.unique(data, return_counts=True)

        areas = dict()

        for idx, area in zip(agent_area[0], agent_area[1]):

            areas[str(idx)] = area

        return areas
    
    # find Area of each agent ID
    idx_areas = getAgentAreaDict(data)
    
    # 
    ids = [int(idx) for idx in list(idx_areas.keys())]
    start_idx = ids.index(0)
    agent_ids = ids[start_idx:]
    
    #
    out = {'ids': [],'lats': [], 'lons': [], 'areas': []}
    
    for agent_i in tqdm(agent_ids):
        
        agent_zone = np.where(data == agent_i)
        
        row_med, col_med = np.median(agent_zone[0]), np.median(agent_zone[1])
        
        lat, lon = convertPixelCoordinateToLatLon(row_med, col_med)
        out['ids'].append(agent_i)
        out['lats'].append(lat)
        out['lons'].append(lon)
        out['areas'].append(idx_areas[str(agent_i)])
    
    return pd.DataFrame(out)