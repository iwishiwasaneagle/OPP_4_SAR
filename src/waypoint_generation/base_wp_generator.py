from abc import ABC, abstractmethod
from src.data_models.probability_map import ProbabilityMap
import numpy as np
import matplotlib.pyplot as plt
from src.data_models.positional.waypoint import Waypoints


class BaseWPGenerator(ABC):
    def __init__(self, prob_map: ProbabilityMap = None, threaded: bool = True, animate: bool = False):
        if prob_map is None: raise TypeError(f"prob_map can't be type {type(prob_map)}. {ProbabilityMap} expected")


        self.threaded = threaded
        self.animate = not self.threaded and animate
        self.prob_map = prob_map 
        
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
