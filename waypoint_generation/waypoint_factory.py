from enum import IntEnum, unique, auto
from data_models.positional.waypoint import Waypoints, Waypoint
from data_models.probability_map import ProbabilityMap
@unique
class WaypointAlgorithmEnum(IntEnum):
    LHC_GW_CONV_E = auto()
    PARALLEL_SWATHS = auto()
    MODIFIED_LAWNMOWER  = auto()
    CONSTANT_SPEED = auto()
    NONE = auto()


class WaypointFactory:
    def __init__(self, alg: WaypointAlgorithmEnum, prob_map: ProbabilityMap, start: Waypoint):
        self.alg = alg

        self.start = start
        self.end = None
    
    def setEnd(self, x:int, y:int) -> self:
        self.end = Waypoint(x,y)
        return self

    def generate(self) -> Waypoints:
        return Waypoints()
