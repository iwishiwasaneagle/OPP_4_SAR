import json
import numpy as np
from src.data_models.probability_map import ProbabilityMap
from src.waypoint_generation.waypoint_settings import WpGenOutput
from src.data_models.positional.waypoint import Waypoint, Waypoints
from src.data_models.positional.pose import Pose, Poses
from src.simulation.vehicle import VehicleSimData

class GlobalJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Poses):
            return {'__poses__':True,'x':obj.x,'y':obj.y}
        elif isinstance(obj,Waypoints):
            return {'__waypoints__':True,'x':obj.x,'y':obj.y}
        elif isinstance(obj,WpGenOutput):
            return {'__wp_gen_output__':True,'img':obj.img,'data':obj.data}
        elif isinstance(obj,ProbabilityMap):
            return {'__probability_map__':True,'prob_map':obj.lq_prob_map.tolist()}
        elif isinstance(obj,VehicleSimData):
            return {'__vehicle_sim_data__':True,'t':obj.t,'t_found':obj.t_found, 'pos':obj.pos,'dpos':obj.dpos, 'ddpos':obj.ddpos}

        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()

        return json.JSONEncoder.default(self, obj)

class GlobalJsonDecoder(json.JSONDecoder):
    def __init__(self,*args,**kwargs) -> None:
            json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    def object_hook(self,dct):
        ret = dct
        if '__poses__' in dct:
            ret = Poses([Pose(f,g) for f,g in zip(dct['x'],dct['y'])])
        elif '__waypoints__' in dct:
            ret = Waypoints([Waypoint(f,g) for f,g in zip(dct['x'],dct['y'])])
        elif '__wp_gen_output__' in dct:
            ret = WpGenOutput(dct['img'])
            ret.data = dct['data']
        elif '__probability_map__' in dct:
            ret = ProbabilityMap(dct['prob_map'])
        elif '__vehicle_sim_data__' in dct:
            ret = VehicleSimData()
            ret.pop('__vehicle_sim_data__')
            ret.__dict__.update(dct)
        return ret