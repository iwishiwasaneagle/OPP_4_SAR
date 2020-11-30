import numpy as np
from .abstractPositionDataObjects import AbstractPositionDataObject
from src.data_models.abstractListObject import AbstractListObject
from typing import TypeVar
w = TypeVar('w',bound='Waypoint')
ws = TypeVar('ws',bound='Waypoints')

class Waypoints(AbstractListObject):
    def __init__(self, *args):
        if len(args)>0 and isinstance(args[0], Waypoints):
            self.__dict__.update(args[0].__dict__)
        elif len(args) == 1 and isinstance(args[0], (list,tuple,np.ndarray)) and all([len(f)==2 for f in args[0]]):
            super().__init__(*[Waypoint(f[0],f[1]) for f in args[0]])
        else:
            super().__init__(*args)

    @property
    def x(self):
        return [f.x for f in self.items]
    @property
    def y(self):
        return [f.y for f in self.items]

    def interped(self,range_from,range_to) -> ws:
        assert(len(range_from)==2)
        assert(len(range_to)==2)

        return_val = Waypoints(np.array([
                np.interp(self.x,(0,range_from[0]),(0,range_to[0])),
                np.interp(self.y,(0,range_from[1]),(0,range_to[1]))
        ]).T)

        return return_val



    # def toFile(self, fid):
    #     data = json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
    #     json.dump(data,fid)

    # @staticmethod
    # def fromFile(fid):
    #     raw_data = json.load(fid)
    #     data = json.loads(raw_data)
    #     items = []
    #     for item in data["items"]:
    #         tmpWp = Waypoint()
    #         tmpWp.__dict__ = item
    #         items.append(tmpWp)
    #     return Waypoints(items)

    @property
    def dist(self) -> float:
        wps = self.toNumpyArray()
        return np.sum(np.linalg.norm(wps[1:] - wps[:-1],axis=1))

class Waypoint(AbstractPositionDataObject):
    def __init__(self,*args):
        super().__init__(*args)    
    @classmethod
    def zero(cls):
        return cls(0,0)

    def __str__(self) -> str:
        return f"Waypoint({self.x},{self.y})"

    def __repr__(self) -> str:
        return self.__str__()