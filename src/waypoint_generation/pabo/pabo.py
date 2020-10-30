from ..base_wp_generator import BaseWPGenerator

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

class PABOSolverEnum(Enum):
    FMINCON=auto()
    GA=auto()
    PARTICLESWARM=auto()

class PABO(BaseWPGenerator):
    def __init__(self, solver: PABOSolverEnum = PABOSolverEnum.PARTICLESWARM, **kwargs):
        super().__init__(**kwargs)


        self.solver = solver

        print("Starting matlab engine...")
        self.mat_eng = MatlabHelper.instance()

        path = os.path.join(os.getcwd(),'src', 'waypoint_generation')

        self.mat_eng.eng.addpath(os.path.join(path,'pabo'))
        print(f"Matlab engine started as {self.mat_eng}")
        
        with open(os.path.join(path,'global.settings'),'r') as f:
            self.settings = json.load(f)
        with open(os.path.join(path,'pabo','pabo.settings'), 'r') as f:
            self.settings.update(json.load(f))
        
        mdouble_prob_map = mdouble(self.prob_map.lq_prob_map.tolist())
        self.mat_eng.eng.set_globs(
            mdouble_prob_map,
            mdouble([self.sweep_radius]),
            mdouble([self.settings['unit_endurance']]),
            mdouble([self.settings['unit_endurance_miss_const']]),  
            mdouble([self.settings['prob_accum_const']]), 
            mbool([False])
            )
        
        self.wp_count = self.settings['wp_count']

    @property
    def sweep_radius(self) -> float:
        return self.settings['radius']
    
    @property
    def waypoints(self) -> Waypoints:
        mdouble_wp_count = mdouble([self.wp_count])
        alg_inp = str(self.solver).split(".")[1].lower()
       
        x = self.mat_eng.eng.pabo(alg_inp,mdouble_wp_count)
         
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
