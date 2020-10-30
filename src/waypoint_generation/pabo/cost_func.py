import numpy as np
import matplotlib.pyplot as plt

from src.matlab_helper import MatlabHelper
from matlab import double as mdouble
import os
from enum import Enum, auto

from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint,Waypoints


class CostFunc:
    def __init__(self):
        print("Starting matlab engine...")
        self.mat_eng = MatlabHelper().eng
        self.mat_eng.addpath(os.path.join(*[os.getcwd()] + self.__module__.split('.')[:-1]))
        print(f"Matlab engine started as {self.mat_eng}")

    def calculate(self, path: Waypoints, prob_map: ProbabilityMap) -> float:
        mdouble_path = mdouble(path.toNumpyArray().tolist())
        mdouble_prob_map = mdouble(prob_map.prob_map.tolist())

        self.mat_eng.set_globs(mdouble_prob_map,mdouble([0.5]),mdouble([80]),mdouble([0.01]),mdouble([500]))

        out = self.mat_eng.cost_func(mdouble_path)

        return out






