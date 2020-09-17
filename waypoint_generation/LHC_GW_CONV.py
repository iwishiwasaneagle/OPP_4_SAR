from waypoint_generation.base_wp_generator import BaseWPGenerator
from data_models.probability_map import ProbabilityMap
from data_models.positional.waypoint import Waypoint,Waypoints

import numpy as np

from simulation.parameters import *
class LHC_GW_CONV(BaseWPGenerator):
    def __init__(self, prob_map: ProbabilityMap, start: Waypoint, end:Waypoint = None, l:int=40):
        super().__init__()

        self.prob_map = prob_map
        self.start = start
        self.end = end
        # self.l = l

        # self.C

    def LHC(self) -> Waypoints:
        wps = Waypoints()
        cur = self.start
        for i in range(5):
            neighbours = np.array(self.neighbours(cur))
            best = neighbours[np.argmax(neighbours[:,1])][0]

            wps.add(Waypoint(best[0], best[1]))
            cur = wps[-1]
        return wps

    def neighbours(self, pos: Waypoint):
        neighbours = [
            (pos.x-1, pos.y-1),
            (pos.x+1, pos.y-1),
            (pos.x  , pos.y-1),

            (pos.x-1, pos.y+1),
            (pos.x+1, pos.y+1),
            (pos.x  , pos.y+1),
            
            (pos.x-1, pos.y),
            (pos.x+1, pos.y),
        ]

        return [(f, self.prob_map[f[0], f[1]]) for f in neighbours if min(f) > 0 and f[0] < self.prob_map.shape[0] and f[1] < self.prob_map.shape[1]]
        

def main():
    wps = LHC_GW_CONV(ProbabilityMap.fromPNG("waypoint_generation/probs_map_1.png"), Waypoint(0,0)).LHC()

    print(wps)

