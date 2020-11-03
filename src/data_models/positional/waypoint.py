import numpy as np
from .abstractPositionDataObjects import AbstractPositionDataObject
from src.data_models.abstractListObject import AbstractListObject
from typing import TypeVar
import numbers
import matplotlib.path as mpp
import json
w = TypeVar('w',bound='Waypoint')


class Waypoints(AbstractListObject):
    def __init__(self, *args):
        if len(args)>0 and isinstance(args[0], Waypoints):
            self.__dict__.update(args[0].__dict__)
        elif len(args) == 1 and isinstance(args[0], (list,np.ndarray)) and all([len(f)==2 for f in args[0]]):
            super().__init__(*[Waypoint(f[0],f[1]) for f in args[0]])
        else:
            super().__init__(*args)

    def toFile(self, fid):
        data = json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
        json.dump(data,fid)

    @staticmethod
    def fromFile(fid):
        raw_data = json.load(fid)
        data = json.loads(raw_data)
        items = []
        for item in data["items"]:
            tmpWp = Waypoint()
            tmpWp.__dict__ = item
            items.append(tmpWp)
        return Waypoints(items)

    @property
    def dist(self) -> float:
        wps = self.toNumpyArray()
        return np.sum(np.linalg.norm(wps[1:] - wps[:-1],axis=1))


            


class Waypoint(AbstractPositionDataObject):
    def __init__(self,*args):
        super().__init__(*args)    
    @staticmethod
    def zero():
        return Waypoint(0,0)