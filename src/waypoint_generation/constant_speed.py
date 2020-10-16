from .base_wp_generator import BaseWPGenerator

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize as sco

from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint,Waypoints

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize as sco

from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint,Waypoints


class ConstantSpeed(BaseWPGenerator):
    def __init__(self, wp_count: int = 4, sweep_width: float = 2, **kwargs):
        super().__init__(**kwargs)

        self.wp_count = wp_count
        self.sweep_width = sweep_width


    @staticmethod
    def cost_func(x: np.array, prob_map: ProbabilityMap, sweep_width: float) -> float:
        x = Waypoints(np.reshape(x,(len(x)//2,2)))

        cost = prob_map.sum_along_path(x,sweep_width,show=True)

        cost += np.sum(np.linalg.norm(x[1:]-x[:-1],axis=0))
                
        return cost
    
    def generate(self):
        r = 0.9*min(self.prob_map.shape[0],self.prob_map.shape[1])/2
        x0 = [(r+r*np.cos(theta), r+r*np.sin(theta)) for theta in np.arange(0,2*np.pi,2*np.pi/self.wp_count)]
        x0.append(x0[0])
        x0_store = np.array(x0)
        x0 = np.reshape(x0,np.shape(x0)[0]*np.shape(x0)[1])
    
        res = sco.minimize(cost_func,x0,args=(self.prob_map, self.sweep_width),method='Nelder-Mead',options={'maxiter':10000000})

        min_x = np.reshape(res.x,(len(res.x)//2,2))

        return Waypoints(min_x)