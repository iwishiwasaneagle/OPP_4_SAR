import numpy as np
from .abstractPositionDataObjects import AbstractPositionDataObject
from data_models.abstractListObject import AbstractListObject
from typing import TypeVar

w = TypeVar('w',bound='Waypoint')


class Waypoints(AbstractListObject):
    def __init__(self, list_:list=[]):
        super().__init__(list_)

class Waypoint(AbstractPositionDataObject):
    def __init__(self,x:float,y:float):
        super().__init__(x,y)
    
    @staticmethod
    def zero():
        return Waypoint(0,0)