from enum import IntEnum, unique, auto
from src.data_models.positional.waypoint import Waypoints, Waypoint
from src.data_models.probability_map import ProbabilityMap
from typing import TypeVar
import os
import json
T = TypeVar("T", bound="WaypointFactory")
@unique
class WaypointAlgorithmEnum(IntEnum):
    LHC_GW_CONV = auto()
    PARALLEL_SWATHS = auto()
    MODIFIED_LAWNMOWER  = auto()
    PABO = auto()



class WaypointAlgSettings:
    class _BaseSetting:
        def __init__(self,rel_f_path):
            with open(os.path.join(*[os.getcwd()]+["src","waypoint_generation"]+rel_f_path),'r') as f:
                data = json.load(f)
            self.__dict__.update(data)
    class Global(_BaseSetting):
        def __init__(self, rel_f_path:list=None):
            super().__init__(["global.settings"])
            if rel_f_path is not None:
                super().__init__(rel_f_path)
    class PABO(Global):
        def __init__(self):
            super().__init__(["pabo","pabo.settings"])
    class ParallelSwaths(Global):
        def __init__(self):
            super().__init__(["parallel_swaths.settings"])
    class ModifiedLawnmower(Global):
        def __init__(self):
            super().__init__(["modified_lawnmower.settings"])    
    class LHC_GW_CONV(Global):
        def __init__(self):
            super().__init__(["LHC_GW_CONV.settings"])   

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

