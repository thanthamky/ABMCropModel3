import numpy as np

class InterfaceParaAllo:
    
    def __init__(self,):
        
        self.n_tree_range = [76, 91]
        self.n_day_harvest = 30
        
        
    def get_sim_product(self, crop='pararubber', lat=13, lon=102):
        
        rain_acc30, temp_avg30, ep_avg30 = self._load_weather(lat, lon)
        
        yield_atree = self.calcualateLatexYieldFromMeteo(rain_acc30, temp_avg30, ep_avg30)
        
        yield_arai = self.calculateLatexProduct(yield_atree)
        
        return yield_arai
        

        
    def _load_weather(self, lat, lon):
        
        # default
        rain_acc30 = 167.65
        temp_avg30 = 24
        ep_avg30 = 120
        
        # Insert code for load and refine weather data here 
        
        #
        #
        #
        
        
        return rain_acc30, temp_avg30, ep_avg30

        
    def calcualateLatexYieldFromMeteo(self, r30, t30, ep30=0):
    
        if ep30 != 0:
            Y = 320.37 - 0.0016*r30 - 8.563*t30
        else:
            Y = 259.0 - 0.008*r30 - 15.815*t30 - 6.029*ep30

        return Y
    
    def calculateLatexProduct(self, latex_yield_per_tree):
    
        n_day = np.random.uniform(self.n_tree_range[0], self.n_tree_range[1])
        
        return latex_yield_per_tree * self.n_day_harvest * n_day / 1000