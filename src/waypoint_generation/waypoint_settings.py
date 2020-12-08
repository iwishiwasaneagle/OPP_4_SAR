import json
from src.data_models.probability_map import ProbabilityMap
from src.enums import *
import enum
import os
from src.data_models.positional.waypoint import Waypoint, Waypoints

class SarGenOutput:
    def __init__(self) -> None:
        self.data = [] 
    def add_generated_locations(self, *args):
        if isinstance(args[0] ,Waypoints):
            self.data = [f for f in args[0]]
        elif all([isinstance(f,Waypoint) for f in args]):
            self.add_generated_locations(Waypoints(args))
        else:
            raise TypeError(f"Not type {type(Waypoints)} nor {type(Waypoint)}")

class WpGenOutput:
    def __init__(self,img:ProbabilityMap) -> None:
        self.img = img
        self.data = {}

    def add_generated_wps(self, wps:Waypoints, time:float, algorithm:WaypointAlgorithmEnum):
        assert(isinstance(wps, Waypoints))
        assert(isinstance(algorithm,WaypointAlgorithmEnum))
        dct = {'time':time,'wps':wps}
        self.data[str(algorithm)] = dct
        return self

class WPSettingsDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    def object_hook(self, dct):
        updates = {}
        if 'pabo_solver' in dct:
            updates['pabo_solver'] = PABOSolverEnum[dct['pabo_solver'].upper()]                    
        if 'home_wp' in dct:
            updates['home_wp'] = Waypoint(dct['home_wp'])
        dct.update(updates)
        return dct

class WPSettingsEncoder(json.JSONEncoder):    
    def __init__(self, *args, **kwargs):
        json.JSONEncoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    def default(self, obj):
        if isinstance(obj, Waypoint):
            return [obj.x, obj.y]
        if isinstance(obj, enum.Enum):
            return obj.name

class WaypointAlgSettings:
    class _BaseSetting:
        def __init__(self,rel_f_path):
            with open(os.path.join(*[os.getenv('OPP4SAR_DIR')]+["src","waypoint_generation"]+rel_f_path),'r') as f:
                data = json.load(f,cls=WPSettingsDecoder)
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