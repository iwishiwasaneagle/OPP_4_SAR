import numpy as np
from .abstractPositionDataObjects import AbstractPositionDataObject
from src.data_models.abstractListObject import AbstractListObject
from typing import TypeVar
import json
w = TypeVar('w',bound='Waypoint')


class Waypoints(AbstractListObject):
    def __init__(self, *args):
        if len(args)>0 and isinstance(args[0], Waypoints):
            self.__dict__.update(args[0].__dict__)
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

class Waypoint(AbstractPositionDataObject):
    def __init__(self,*args):
        super().__init__(*args)    
    @staticmethod
    def zero():
        return Waypoint(0,0)