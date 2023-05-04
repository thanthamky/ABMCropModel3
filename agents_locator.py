import numpy as np
from tqdm import tqdm
import pandas as pd
#from array_compressor import compress_array, decompress_array

def convertPixelCoordinateToLatLon(row, col):
    x_min, y_min, x_max, y_max = 99.0853175160000035, 15.0483699459999993, 100.8600274380000030, 16.2031785890000002
    width, height = 4726, 3144

    lat = y_min + (row / height) * (y_max - y_min)
    lon = x_min + (col / width) * (x_max - x_min)

    return lat, lon

def convertPixelCoordinateToLatLonBatch(row, col, i, j):
    
    x_min, y_min, x_max, y_max = 99.0853175160000035,15.0483699459999993, 100.8600274380000030,16.2031785890000002

    width, height = 4726, 3144
        
    batch_row = row + i
    batch_col = col + j

    lat = y_min + (batch_row/height)*(y_max-y_min)
    lon = x_min + (batch_col/width)*(x_max-x_min)

    return lat, lon


def convertAgentsMapToDataFrame(agent_array):
    # Find unique agent IDs
    unique_agents = np.unique(agent_array)

    # Filter unique agent IDs to select only those that are greater than or equal to 0
    unique_agents = [agent_id for agent_id in unique_agents if agent_id >= 0]

    # Initialize an empty dictionary to store the row and column indices for each agent ID
    agent_indices = {agent_id: ([], []) for agent_id in unique_agents}

    # Iterate through the 2D numpy array and store row and column indices for each agent ID
    for row_idx, row in enumerate(agent_array):
        for col_idx, agent_id in enumerate(row):
            if agent_id in agent_indices:
                agent_indices[agent_id][0].append(row_idx)
                agent_indices[agent_id][1].append(col_idx)

    # Initialize an empty list to store mean row and mean column index for each agent
    agent_mean_positions_list = []

    # Iterate through unique agent IDs
    for agent_id in unique_agents:
        # Get the row and column indices from the dictionary
        row_indices, col_indices = agent_indices[agent_id]

        # Calculate mean row and mean column index
        mean_row = np.mean(row_indices)
        mean_col = np.mean(col_indices)

        # Convert mean row and mean column index to latitude and longitude
        lat, lon = convertPixelCoordinateToLatLon(mean_row, mean_col)

        # Append the result to the list
        agent_mean_positions_list.append([agent_id, lat, lon])

    # Create a pandas DataFrame to store the result
    agent_mean_positions_df = pd.DataFrame(agent_mean_positions_list, columns=['ids', 'lats', 'lons'])

    return agent_mean_positions_df

def convertAgentsMapToDataFrameBatch(agent_array, i, j):
    # Find unique agent IDs
    unique_agents = np.unique(agent_array)

    # Filter unique agent IDs to select only those that are greater than or equal to 0
    unique_agents = [agent_id for agent_id in unique_agents if agent_id >= 0]

    # Initialize an empty dictionary to store the row and column indices for each agent ID
    agent_indices = {agent_id: ([], []) for agent_id in unique_agents}

    # Iterate through the 2D numpy array and store row and column indices for each agent ID
    for row_idx, row in enumerate(agent_array):
        for col_idx, agent_id in enumerate(row):
            if agent_id in agent_indices:
                agent_indices[agent_id][0].append(row_idx)
                agent_indices[agent_id][1].append(col_idx)

    # Initialize an empty list to store mean row and mean column index for each agent
    agent_mean_positions_list = []

    # Iterate through unique agent IDs
    for agent_id in unique_agents:
        # Get the row and column indices from the dictionary
        row_indices, col_indices = agent_indices[agent_id]

        # Calculate mean row and mean column index
        mean_row = np.mean(row_indices)
        mean_col = np.mean(col_indices)

        # Convert mean row and mean column index to latitude and longitude
        lat, lon = convertPixelCoordinateToLatLonBatch(mean_row, mean_col, i, j)

        # Append the result to the list
        agent_mean_positions_list.append([agent_id, lat, lon])

    # Create a pandas DataFrame to store the result
    agent_mean_positions_df = pd.DataFrame(agent_mean_positions_list, columns=['ids', 'lats', 'lons'])

    return agent_mean_positions_df




# ======= DEPRECATED LINES OF CODE ======================================================================================


def convertAgentsMapToDataFrame_old(data):

    
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

def convertAgentsMapToDataFrameBatch_old(data, i, j):

    
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

