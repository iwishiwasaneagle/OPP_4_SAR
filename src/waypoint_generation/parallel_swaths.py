from .base_wp_generator import BaseWPGenerator
from src.data_models.positional.waypoint import Waypoint, Waypoints
import numpy as np

class ParallelSwaths(BaseWPGenerator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def waypoints(self) -> Waypoints:
        wps = Waypoints([Waypoint.zero()])
        lower_y,upper_y = (1,self.prob_map.lq_shape[1]-1)

        rows = np.arange(1,self.prob_map.lq_shape[0]-1)
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

        return wps