import numpy as np
import matplotlib.pyplot as plt

from src.matlab_helper import MatlabHelper
from matlab import double as mdouble
from matlab import logical as mbool
import os
from enum import Enum, auto

from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint,Waypoints


class CostFunc:
    def __init__(self):
        self.mat_eng = MatlabHelper.instance()
        self.mat_eng.eng.addpath(os.path.join(*[os.getcwd()] + self.__module__.split('.')[:-1]))

    def calculate(self, path: Waypoints, prob_map: ProbabilityMap) -> float:
        mdouble_path = mdouble(path.toNumpyArray().tolist())
        mdouble_prob_map = mdouble(prob_map.prob_map.tolist())

        out = self.mat_eng.eng.cost_func(mdouble_path,mdouble_prob_map,mdouble([0.5]),mdouble([80]),mdouble([0]),mdouble([1]))

        return out






