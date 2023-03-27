import subprocess
from subprocess import check_output
import numpy as np
import json
from datetime import datetime
import requests
import pandas as pd
import sqlite3
import os


class InterfaceAPSIM:
    
    
    def __init__(self, base_path):
        
        self.base_path = os.path.join(base_path, 'apsim')
        self.default_yield_oilpalm = [1000,3000]
        self.default_yield_sugarcane = [9000,13000]
        
        self.crop_list = {'sc':'sugarcane', 'op':'oilpalm'}
        
        self.sql_yield_sugarcane = '''select max("Sugarcane.cane_wt") from Report;'''
        self.sql_yield_oilpalm = '''select max("Calculations.Script.AnnualBunches"*"Calculations.Script.AnnualYield") as yield from AnnualOutput;'''
        
        self.apsim_model_path = os.path.join(self.base_path, 'apsim_bin/Models')
        
        self.sugarcane_modelpath = os.path.join(self.base_path, 'apsim_models/sugarcane_mod.apsimx')
        self.oilpalm_modelpath = os.path.join(self.base_path, 'apsim_models/oilpalm_mod.apsimx')
        
        self.sugarcane_outputpath= os.path.join(self.base_path, 'apsim_models/sugarcane_mod.db')
        self.oilpalm_outputpath = os.path.join(self.base_path, 'apsim_models/oilpalm_mod.db')
        
        self.climate_file_path = os.path.join(self.base_path, 'apsim_weather/apsim_climate_file.met')
        
        self.weather_fetch_from = '20000101'
        self.weather_fetch_to = '20151231'
        self.sawing_date = '...'
        
        
    def get_sim_product(self, crop, lat, lon):
        
        
        if crop == 'sc':
            
            try:
                
                self._load_weather(crop, lat, lon)
                #self._config_model()
                self._run_model(crop)
                out_yield = self.connect_db_output(crop)
                
                return out_yield
            
            except Exception as e:
                
                print(str(e))
                return np.random.uniform(self.default_yield_sugarcane[0], self.default_yield_sugarcane[1])
        
          
        elif crop =='op':
            
            try:
                #print("load weather..",sep="")
                self._load_weather(crop, lat, lon)
                #self._config_model()
                #print("run model..",sep="")
                self._run_model(crop)
                #print("get output..")
                out_yield = self.connect_db_output(crop)
                
                return out_yield
            
            except Exception as e:
                
                print(str(e))
                return np.random.uniform(self.default_yield_oilpalm[0], self.default_yield_oilpalm[1])
            
            
        else:
            
            return 0.
        

        
    def _load_weather(self, crop, lat, lon):
        
        if crop == 'sc':
            
            self.fetch_and_save_met_data(lat, lon, '19900101', '20151231')

        elif crop == 'op':
            
            self.fetch_and_save_met_data(lat, lon, '20000101', '20151231')
        
    def _run_model(self, crop):
        
        if crop == 'sc':
            
            subprocess.run([self.apsim_model_path, self.sugarcane_modelpath], capture_output=True, text=True)
            
        elif crop == 'op':
            
            subprocess.run([self.apsim_model_path, self.oilpalm_modelpath], capture_output=True, text=True)
        
        
        
    def _config_model(self,):
        
        if crop == 'sc':
            
            ...
            
        elif crop == 'op':
            
            model = json.load(open(self.oilpalm_modelpath))
            
            # Modify start cropping
            model['Children'][0]['Children'][1]['Start'] = '2000-01-01T00:00:00'
            
            # Modify End cropping
            model['Children'][0]['Children'][1]['End']= '2015-12-31T00:00:00'
            
            # Modify Sawing date
            model['Children'][0]['Children'][4]['Children'][7]['Parameters'][0]['Value'] = '01/01/2000 00:00:00'
            
            # Serializing json
            json_object = json.dumps(model, indent=4)

            # Writing to sample.json
            with open(self.oilpalm_modelpath, "w") as outfile:
                outfile.write(json_object)
            
    
    def connect_db_output(self, crop):
        
        if crop == 'sc':
            
            try:
                
                command = self.sql_yield_sugarcane
                conn = sqlite3.connect(self.sugarcane_outputpath)    
                cursor = conn.cursor()
                df = pd.read_sql_query(command, conn)
                conn.close()

                return df.values[0][0] /1000 *1600
            
            except Exception as e:
                print(f'read output found Error! use reserved yield value...')
                print(str(e))
                return np.random.uniform(self.default_yield_sugarcane[0], self.default_yield_sugarcane[1])
            
            
        elif crop == 'op':
            
            try:
                
                command = self.sql_yield_oilpalm
                #print('connect sqlite')
                conn = sqlite3.connect(self.oilpalm_outputpath)   
                cursor = conn.cursor()
                #print('query result')
                df = pd.read_sql_query(command, conn)
                conn.close()

            
                return df.values[0][0] * 2.5
            
            except Exception as e:
                print(f'read output found Error! use reserved yield value...')
                print(str(e))
                return np.random.uniform(self.default_yield_oilpalm[0], self.default_yield_oilpalm[1])
                
    
    def date_to_day_of_year(self, date_str):
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        day_of_year = date_obj.timetuple().tm_yday
        return day_of_year
    
    def fetch_and_save_met_data(self, latitude, longitude, start_date, end_date):
        url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN,PRECTOT,T2M_MIN,T2M_MAX&community=ag&longitude={longitude}&latitude={latitude}&start={start_date}&end={end_date}&format=JSON"

        response = requests.get(url)
        data = response.json()

        table = pd.DataFrame.from_dict(data['properties']['parameter'])

        self.write_met_file(table, latitude, longitude)
    
    def write_met_file(self, table, lat, lon):

        sep = '   '
        
        f = open(self.climate_file_path, "w")

        f.writelines("[weather.met.weather]\n")
        f.writelines("!station name = thailandpalm\n")

        f.writelines(f"latitude = {round(lat)}  (DECIMAL DEGREES)\n")
        f.writelines(f"longitude= {round(lon)}  (DECIMAL DEGREES)\n")

        avg_temp = ((table['T2M_MAX']+table['T2M_MIN'])/2).mean()
        std_temp = ((table['T2M_MAX']+table['T2M_MIN'])/2).std()

        f.writelines(f"tav =  {round(avg_temp,2)} (oC) ! annual average ambient temperature\n")
        f.writelines(f"amp =  {round(std_temp,2)} (oC) ! annual amplitude in mean monthly temperature\n")

        f.write("\n")

        f.write(f'year{sep}day{sep}radn{sep}maxt{sep}mint{sep}rain\n')
        f.write(f'(){sep}(){sep}(){sep}(){sep}(){sep}()\n')

        date_list = table.index.tolist()
        year = [date[:4] for date in date_list]
        day = [self.date_to_day_of_year(date) for date in date_list]

        radn = table['ALLSKY_SFC_SW_DWN'].tolist()
        maxt = table['T2M_MAX'].tolist()
        mint = table['T2M_MIN'].tolist()
        rain = table['PRECTOTCORR'].tolist()

        for i in range(len(table)):

            f.write(f'{year[i]}{sep}{day[i]}{sep}{radn[i]}{sep}{maxt[i]}{sep}{mint[i]}{sep}{rain[i]}\n')

        f.close()
        