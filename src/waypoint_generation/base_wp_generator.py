from abc import ABC, abstractmethod

from numpy.lib.arraysetops import isin
from src.data_models.probability_map import ProbabilityMap
import numpy as np
import matplotlib.pyplot as plt
from src.data_models.positional.waypoint import Waypoint, Waypoints
from src.waypoint_generation.waypoint_settings import WaypointAlgSettings

from loguru import logger

class BaseWPGenerator(ABC):
    def __init__(self, prob_map: ProbabilityMap = None, home_wp: Waypoint=Waypoint.zero(), animate:bool=False,threaded: bool = True):
        if not isinstance(prob_map,ProbabilityMap): raise TypeError(f"prob_map can't be type {type(prob_map)}. {ProbabilityMap} expected")
        logger.debug(f"Start of {self.__class__.__name__}")

        self.settings =  WaypointAlgSettings.Global()
        self.threaded = threaded
        self.animate = animate
        self.prob_map = prob_map 
        assert(isinstance(home_wp,Waypoint))
        self.home_wp = home_wp
        
        if self.animate:
            plt.ion()
            fig = plt.figure()
            # for stopping simulation with the esc key.
            fig.canvas.mpl_connect('key_release_event',
                    lambda event: [exit(-1) if event.key == 'escape' else None])

            self._ax = fig.add_subplot(111)
    
    @property
    @abstractmethod
    def waypoints(self) -> Waypoints:
        return NotImplemented

    def __del__(self):
        logger.debug(f"End of {self.__class__.__name__}")