from src.waypoint_generation.base_wp_generator import BaseWPGenerator

import numpy as np
import matplotlib.pyplot as plt

from matlab import double as mdouble
from matlab import logical as mbool
import os
from enum import Enum, auto
import json

from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint,Waypoints
from src.matlab_helper import MatlabHelper
from src.waypoint_generation.waypoint_settings import WaypointAlgSettings
from src.enums import PABOSolverEnum

from loguru import logger

class PABO(BaseWPGenerator):
    def __init__(self,**kwargs):
        if 'solver' in kwargs and isinstance(kwargs['solver'], PABOSolverEnum):
            self.solver = kwargs.pop('solver')

        super().__init__(**kwargs)

        self.mat_eng = MatlabHelper.instance()
        path = os.path.join(os.getcwd(),'src', 'waypoint_generation')
        self.mat_eng.eng.addpath(os.path.join(path,'pabo'))
        
        self.settings = WaypointAlgSettings.PABO()
        
        mdouble_prob_map = mdouble(self.prob_map.lq_prob_map.tolist())
        self.mat_eng.eng.set_globs(
            mdouble_prob_map,
            mdouble([self.sweep_radius]),
            mdouble([self.settings.unit_endurance]),
            mdouble([self.settings.unit_endurance_miss_const]),  
            mdouble([self.settings.prob_accum_const]), 
            mbool([False])
            )
        

        self.wp_count = self.settings.wp_count
        if 'solver' not in self.__dict__:
            self.solver = self.settings.pabo_solver

        logger.debug(f"Optimisation solver set to {self.solver}")

    @property
    def sweep_radius(self) -> float:
        return self.settings.radius
    
    @property
    def waypoints(self) -> Waypoints:
        mdouble_wp_count = mdouble([self.wp_count])
        solver_str = str(self.solver).split(".")[1].lower()
       
        x = self.mat_eng.eng.pabo(solver_str,mdouble_wp_count)
         
        return Waypoints([list(f) for f in x])

        # r = 0.9*min(self.prob_map.shape[0],self.prob_map.shape[1])/2
        # x0 = [(r+r*np.cos(theta), r+r*np.sin(theta)) for theta in np.arange(0,2*np.pi,2*np.pi/self.wp_count)]
        # x0.append(x0[0])
        # x0_store = np.array(x0)
        # x0 = np.reshape(x0,np.shape(x0)[0]*np.shape(x0)[1])

        # res = sco.minimize(self.cost_func,x0,args=(self.prob_map, self.sweep_width),method='Nelder-Mead',options={'maxiter':10000000})

        # min_x = np.reshape(res.x,(len(res.x)//2,2))
        # tmp = [self.prob_map.hq_to_lq_coords(f) for f in min_x]
        # min_x = [Waypoint(g[0],g[1]) for g in tmp]
        # return Waypoints(min_x)
