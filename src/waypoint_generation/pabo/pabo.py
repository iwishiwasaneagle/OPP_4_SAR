from contextlib import redirect_stdout, redirect_stderr
from src.waypoint_generation.base_wp_generator import BaseWPGenerator

import numpy as np
import matplotlib.pyplot as plt

from matlab import double as mdouble
from matlab import logical as mbool
import os
import sys

from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint,Waypoints
from src.matlab_helper import MatlabHelper, StdOut
from src.waypoint_generation.waypoint_settings import WaypointAlgSettings
from src.enums import PABOSolverEnum

from loguru import logger


class PABO(BaseWPGenerator):
    def __init__(self,home:Waypoint,**kwargs):
        if 'solver' in kwargs and isinstance(kwargs['solver'], PABOSolverEnum):
            self.solver = kwargs.pop('solver')

        super().__init__(**kwargs)

        self.mat_eng = MatlabHelper.instance()
        path = os.path.join(os.getcwd(),'src', 'waypoint_generation')
        self.mat_eng.eng.addpath(os.path.join(path,'pabo'),**self.mat_eng.kwargs)

        self.home = home
        
        self.settings = WaypointAlgSettings.PABO()
        self.wp_count = self.settings.wp_count
        if 'solver' not in self.__dict__:
            self.solver = self.settings.pabo_solver

        logger.debug(f"Optimisation solver set to {self.solver}")

    @property
    def sweep_radius(self) -> float:
        return self.settings.search_radius
    
    @property
    def waypoints(self) -> Waypoints:
        mdouble_wp_count = mdouble([self.wp_count-2])
        mdouble_prob_map = mdouble(self.prob_map.prob_map.tolist())
        mdouble_home_wp = mdouble([self.home.x,self.home.y])
        solver_str = str(self.solver).split(".")[1].lower()

        # self.mat_eng.eng.eval("dbstop in pabo.m at 48",nargout=0)
         # self.mat_eng.eng.eval("dbstop in pabo.m at 12",nargout=0)

        logger.trace("Pre-matlab")      
        x = self.mat_eng.eng.pabo(
            solver_str,
            mdouble_wp_count,
            mdouble_home_wp,
            mdouble_prob_map,
            mdouble([self.sweep_radius]),
            mdouble([self.settings.unit_endurance]),
            mdouble([self.settings.unit_endurance_miss_const]),  
            mdouble([self.settings.prob_accum_const]), 
            mbool([self.animate]),
            **self.mat_eng.kwargs)
        logger.trace("Post-matlab")
     
        return Waypoints([self.home]+[list(f) for f in x]+[self.home])