from enum import IntEnum, unique, auto
from src.data_models.positional.waypoint import Waypoints, Waypoint
from src.data_models.probability_map import ProbabilityMap
from src.enums import PABOSolverEnum, WaypointAlgorithmEnum
from typing import TypeVar
import os
import json
T = TypeVar("T", bound="WaypointFactory")

class WaypointFactory:
    def __init__(self, alg: WaypointAlgorithmEnum, prob_map: ProbabilityMap, start:Waypoint=Waypoint(0,0), threaded: bool=True, animate: bool = False):
        
        self.alg = alg

        assert(min(start)>=0 and start.x <= prob_map.shape[0] and start.y <= prob_map.shape[1])
        self.prob_map = prob_map

        self.start = start
        self.end = None
        
        assert(isinstance(threaded, bool))
        self.threaded = threaded
        assert(isinstance(animate, bool))
        self.animate = animate
    
    def setEnd(self, x:int, y:int) -> T:
        self.end = Waypoint(x,y)
        return self

    def generate(self) -> Waypoints:
        kwargs = {'prob_map':self.prob_map,'threaded':self.threaded}
        
        if self.alg == WaypointAlgorithmEnum.LHC_GW_CONV:
            from src.waypoint_generation.LHC_GW_CONV import LHC_GW_CONV
            return LHC_GW_CONV(**kwargs).waypoints
           
        elif self.alg == WaypointAlgorithmEnum.MODIFIED_LAWNMOWER:
            from src.waypoint_generation.modified_lawnmower import ModifiedLawnmower
            return ModifiedLawnmower(**kwargs).waypoints

        elif self.alg == WaypointAlgorithmEnum.PARALLEL_SWATHS:
            from src.waypoint_generation.parallel_swaths import ParallelSwaths
            return ParallelSwaths(**kwargs).waypoints

        elif self.alg == WaypointAlgorithmEnum.PABO:
            from src.waypoint_generation.pabo import PABO
            return PABO(**kwargs).waypoints

