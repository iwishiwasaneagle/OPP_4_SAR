import json
from src.enums.waypoint_algorithm_enum import WaypointAlgorithmEnum
from src.simulation.simulation import SimRunnerOutput
import numpy as np
from src.data_models.probability_map import ProbabilityMap
from src.waypoint_generation.waypoint_settings import SarGenOutput, WpGenOutput
from src.data_models.positional.waypoint import Waypoint, Waypoints
from src.data_models.positional.pose import Pose, Poses
from src.simulation.vehicle import VehicleSimData

PUBLIC_ENUMS = {
    'WaypointAlgorithmEnum':WaypointAlgorithmEnum
}

class GlobalJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Poses):
            return {'__poses__':True,'x':obj.x,'y':obj.y}
        elif isinstance(obj,Waypoints):
            return {'__waypoints__':True,'x':obj.x,'y':obj.y}
        elif isinstance(obj,Waypoint):
            return {'__waypoint__':True, 'x':obj.x, 'y':obj.y}
        elif isinstance(obj,WpGenOutput):
            return {'__wp_gen_output__':True,'img':obj.img,'data':obj.data}
        elif isinstance(obj,SimRunnerOutput):
            return {'__sim_runner_output__':True,'data':obj.data}
        elif isinstance(obj,SarGenOutput):
            return {'__sar_gen_output__':True,'data':obj.data}
        elif isinstance(obj,ProbabilityMap):
            return {'__probability_map__':True,'prob_map':obj.prob_map.tolist()}
        elif isinstance(obj,VehicleSimData):
            return {'__vehicle_sim_data__':True,'found':obj.found,'t':obj.t,'pos':obj.pos,'dpos':obj.dpos, 'ddpos':obj.ddpos}
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif type(obj) in PUBLIC_ENUMS.values():
            return {'__enum__':str(obj)}

        return json.JSONEncoder.default(self, obj)

class GlobalJsonDecoder(json.JSONDecoder):
    def __init__(self,*args,**kwargs) -> None:
            json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    def object_hook(self,dct):
        ret = dct
        if '__poses__' in dct:
            poses = [Pose(f,g) for f,g in zip(dct['x'],dct['y'])]
            ret = Poses(poses)
        elif '__waypoints__' in dct:
            ret = Waypoints([Waypoint(f,g) for f,g in zip(dct['x'],dct['y'])])
        elif '__waypoint__' in dct:
            ret = Waypoint(dct['x'],dct['y'])
        elif '__wp_gen_output__' in dct:
            ret = WpGenOutput(dct['img'])
            ret.data = dct['data']
        elif '__sim_runner_output__' in dct:
            ret = SimRunnerOutput()
            ret.data = dct['data']
        elif'__sar_gen_output__' in dct:
            ret = SarGenOutput()
            ret.data = dct['data'] 
        elif '__probability_map__' in dct:
            ret = ProbabilityMap(dct['prob_map'])
        elif '__vehicle_sim_data__' in dct:
            ret = VehicleSimData()
            dct.pop('__vehicle_sim_data__')
            ret.__dict__.update(dct)
        if "__enum__" in dct:
            name, member = dct["__enum__"].split(".")
            return getattr(PUBLIC_ENUMS[name], member) 
        return ret