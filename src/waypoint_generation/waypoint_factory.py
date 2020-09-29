from enum import IntEnum, unique, auto
from src.data_models.positional.waypoint import Waypoints, Waypoint
from src.data_models.probability_map import ProbabilityMap
from typing import TypeVar
T = TypeVar("T", bound="WaypointFactory")
@unique
class WaypointAlgorithmEnum(IntEnum):
    LHC_GW_CONV_E = auto()
    PARALLEL_SWATHS = auto()
    MODIFIED_LAWNMOWER  = auto()
    CONSTANT_SPEED = auto()
    NONE = auto()


class WaypointFactory:
    def __init__(self, alg: WaypointAlgorithmEnum, prob_map: ProbabilityMap, threaded: bool=True, animate: bool = False):
        self.alg = alg
        self.prob_map = prob_map

        self.start = Waypoint(0,0) 
        self.end = None
        
        self.threaded = threaded
        self.animate = animate
    
    def setEnd(self, x:int, y:int) -> T:
        self.end = Waypoint(x,y)
        return self

    def generate(self) -> Waypoints:
        kwargs = {'prob_map':self.prob_map,'threaded':self.threaded,'animate':self.animate}
        
        if self.alg == WaypointAlgorithmEnum.LHC_GW_CONV_E:
            from src.waypoint_generation.LHC_GW_CONV import LHC_GW_CONV
            return LHC_GW_CONV(self.start, self.end, 10, **kwargs).waypoints
           
        elif self.alg == WaypointAlgorithmEnum.MODIFIED_LAWNMOWER:
            from src.waypoint_generation.modified_lawnmower import ModifiedLawnmower
            return ModifiedLawnmower(**kwargs).waypoints

