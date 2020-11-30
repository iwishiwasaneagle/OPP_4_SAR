from .base_wp_generator import BaseWPGenerator
from src.data_models.positional.waypoint import Waypoint, Waypoints
from src.waypoint_generation.waypoint_settings import WaypointAlgSettings

import matplotlib.pyplot as plt
import numpy as np

class ParallelSwaths(BaseWPGenerator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = WaypointAlgSettings.ParallelSwaths()

    @property
    def waypoints(self) -> Waypoints:
        wps = Waypoints([self.settings.home_wp])
        lower_y,upper_y = (1,self.prob_map.shape[0]-1)

        rows = np.arange(1,self.prob_map.shape[1])
        at_bottom = True
        for r in rows:
            if at_bottom:
                wps.add(
                   Waypoint(r,lower_y),
                )
                wps.add(
                   Waypoint(r,upper_y),
                )
            else:
                wps.add(
                   Waypoint(r,upper_y),
                )
                wps.add(
                   Waypoint(r,lower_y),
                )
            at_bottom = not at_bottom
        wps.add(self.settings.home_wp)
        return wps