
import sys, os
import pandas as pd
import json
import glob
import yaml

import pcse
print("This notebook was built with:")
print("python version: %s " % sys.version)
print("PCSE version: %s" %  pcse.__version__)

from pcse.fileinput import YAMLCropDataProvider, CABOFileReader
from pcse.fileinput import CABOFileReader
from pcse.util import WOFOST71SiteDataProvider
from pcse.fileinput import ExcelWeatherDataProvider
from pcse.models import Wofost72_WLP_FD, Wofost72_PP
from pcse.base import ParameterProvider

import xlrd

from pcse.db import NASAPowerWeatherDataProvider

class InterfaceWOFOST:
    
    def __init__(self, base_path):
        self.base_path = os.path.join(base_path, 'wofost')
        self.crop_list = ['rice', 'sugarcane', 'cassava', 'maize']
        self.crop_list2 = ['ri1', 'ri2', 'ri3', 'ri4', 'cf', 'mp']
        self.input_soil_dir = os.path.join(self.base_path, 'wofost_soil_config')
        self._errors = [] 
        self.input_cropparam_dir = os.path.join(self.base_path, 'wofost_param_config')
        
        self.reserved_yield = {'ri1': 363,
                               'ri2': 712,
                               'ri3': 745,
                               'ri4': 600,
                               'sc' : 10000,
                               'mp' : 1400,
                               'cf' : 3438}
    
    def read_crop_config(self, crop_type):
        with open(self.input_cropparam_dir+'/'+crop_type+'.json', 'r') as f:
             self.config = json.load(f)
    
    def load_crop_data(self):
        self.cropd = YAMLCropDataProvider(force_reload=True)
        #self.cropd = YAMLCropDataProvider(fpath="CropModel3/WOFOST_crop_parameters")
        self.cropd.set_active_crop(self.config['plant'], self.config['crop_variety'])
        
    def load_soil_data(self):
        self.soilfile = os.path.join(self.input_soil_dir, self.config['soil'])
        self.soild = CABOFileReader(self.soilfile)
    
    def load_site_data(self):
        #self.sited = WOFOST71SiteDataProvider(WAV=100, CO2=360)
        self.sited = WOFOST71SiteDataProvider(WAV=100)
        
    def load_agromanagement(self):
        self.agromanagement = yaml.safe_load(self.config['argo'])
    
    def init_params(self):
        self.parameters = ParameterProvider(cropdata=self.cropd, soildata=self.soild, sitedata=self.sited)
        
    def load_weather_file(self):
        # Load weather file
        self.wdp = ExcelWeatherDataProvider('input_weather/WOFOST-ข้าว-118811920-141233557.xlsx', force_reload=False)
        #print(self.wdp)
        
    def load_weather_nasa(self, lat, lon):
        self.wdp = NASAPowerWeatherDataProvider(latitude=lat, longitude=lon)
        
    def simulate_crop(self):
        # Run simulation until terminate
        try:
            # wofsim = Wofost72_WLP_FD(parameters, wdp, agromanagement)
            self.wofsim = Wofost72_PP(parameterprovider=self.parameters, weatherdataprovider=self.wdp, agromanagement=self.agromanagement)
            self.wofsim.run_till_terminate()
        except Exception as e:
            self._errors.append({
                'err': e
            })
    
    def output_product(self):
        ''' PASS OUT OUTPUT FROM MODEL ---------------------------------------------------------------- '''
        self.df_results = pd.DataFrame(self.wofsim.get_output()) # convert to dataframe
        convert_ha_to_rai = ['TAGP', 'TWSO', 'TWLV', 'TWST', 'TWRT', 'TRA'] # define fields
        self.df_results[convert_ha_to_rai] = self.df_results[convert_ha_to_rai]/6.25 # select field and convert to rai
        self.df_results = self.df_results.set_index("day") # set index
        return self.df_results['TWSO'][-1]
    
    def get_sim_product(self, crop_type, lat, lon):
        
        try:
        
            if crop_type == 'ri1':

                return self.reserved_yield['ri1']

            elif crop_type == 'ri2':

                return self.reserved_yield['ri2']

            elif crop_type == 'ri3':

                return self.reserved_yield['ri3']

            elif crop_type == 'ri4':

                return self.reserved_yield['ri4']

            else:

                self.read_crop_config(crop_type)
                self.load_crop_data()
                self.load_soil_data()
                self.load_site_data()
                self.load_agromanagement()
                self.init_params()
                self.load_weather_nasa(lat, lon) # <-- weather modify
                self.simulate_crop()
                product = self.output_product()


            return product
        
        except Exception as e:
            
            print(str(e))
            
            return 0
        
    