from enum import IntEnum, unique, auto
from src.data_models.positional.waypoint import Waypoints, Waypoint
from src.data_models.probability_map import ProbabilityMap
from src.enums import PABOSolverEnum, WaypointAlgorithmEnum
from typing import TypeVar
import os
import json
from loguru import logger
T = TypeVar("T", bound="WaypointFactory")

class WaypointFactory:
    def __init__(self, alg: WaypointAlgorithmEnum, prob_map: ProbabilityMap, threaded: bool=True):
        
        self.alg = alg

        self.prob_map = prob_map
        
        assert(isinstance(threaded, bool))
        self.threaded = threaded
    
    def setEnd(self, x:int, y:int) -> T:
        self.end = Waypoint(x,y)
        return self

    def generate(self) -> Waypoints:
        kwargs = {'prob_map':self.prob_map,'threaded':self.threaded}
        waypoints = None

        if self.alg == WaypointAlgorithmEnum.LHC_GW_CONV:
            from src.waypoint_generation.LHC_GW_CONV import LHC_GW_CONV
            waypoints = LHC_GW_CONV(**kwargs).waypoints
           
        elif self.alg == WaypointAlgorithmEnum.MODIFIED_LAWNMOWER:
            from src.waypoint_generation.modified_lawnmower import ModifiedLawnmower
            waypoints = ModifiedLawnmower(**kwargs).waypoints

        elif self.alg == WaypointAlgorithmEnum.PARALLEL_SWATHS:
            from src.waypoint_generation.parallel_swaths import ParallelSwaths
            waypoints = ParallelSwaths(**kwargs).waypoints

        elif 'pabo' in str(self.alg).lower():
            from src.waypoint_generation.pabo import PABO
            
            if self.alg == WaypointAlgorithmEnum.PABO_FMINCON:
                kwargs['solver'] = PABOSolverEnum.FMINCON
            elif self.alg == WaypointAlgorithmEnum.PABO_GA:
                kwargs['solver'] = PABOSolverEnum.GA
            elif self.alg == WaypointAlgorithmEnum.PABO_PARTICLESWARM:
                kwargs['solver'] = PABOSolverEnum.PARTICLESWARM
            
            waypoints = PABO(**kwargs).waypoints

        assert(isinstance(waypoints, Waypoints))
        logger.info(f"{len(waypoints)} waypoints generated with distance = {waypoints.dist:.2f} units")
        return waypoints

