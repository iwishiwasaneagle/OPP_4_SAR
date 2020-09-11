import numpy as np
from .abstractPositionDataObjects import AbstractPositionDataObject
from .abstractListObject import AbstractListObject
from typing import TypeVar

w = TypeVar('w',bound='Waypoint')


class Waypoints(AbstractListObject):
    def __init__(self, *argv):
        super().__init__(*argv)

class Waypoint(AbstractPositionDataObject):
    def __init__(self,x:float,y:float,z:float):
        super().__init__(x,y,z)
    
    @staticmethod
    def zero():
        return Waypoint(0,0,0)