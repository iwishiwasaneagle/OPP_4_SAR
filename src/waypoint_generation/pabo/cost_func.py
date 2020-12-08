from src.waypoint_generation.waypoint_settings import WaypointAlgSettings
import numpy as np
import matplotlib.pyplot as plt

from src.matlab_helper import MatlabHelper
from matlab import double as mdouble
from matlab import logical as mbool
import os
from enum import Enum, auto

from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint, Waypoints


class CostFunc:
    def __init__(self):
        self.mat_eng = MatlabHelper.instance()
        self.mat_eng.eng.addpath(os.path.join(
            *[os.getenv('OPP4SAR_DIR')] + self.__module__.split('.')[:-1]))
        #self.settings = WaypointAlgSettings.Global()

    def calculate(self, path: Waypoints, prob_map: ProbabilityMap, search_radius: float = 0.5) -> float:
        assert(isinstance(path, Waypoints))
        assert(isinstance(prob_map, ProbabilityMap))
        mdouble_path = mdouble(path.toNumpyArray().tolist())
        mdouble_home_wp = mdouble([-1,-1])
        mdouble_prob_map = mdouble(prob_map.prob_map.tolist())
        mdouble_search_radius = mdouble([search_radius])
        out = self.mat_eng.eng.cost_func(
            mdouble_path,mdouble_home_wp, mdouble_prob_map, mdouble_search_radius, mdouble([-1]), mdouble([0]), mdouble([1]))
        return out
