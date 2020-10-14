import numpy as np
from .abstractPositionDataObjects import AbstractPositionDataObject
from src.data_models.abstractListObject import AbstractListObject
from typing import TypeVar

w = TypeVar('w',bound='Waypoint')


class Waypoints(AbstractListObject):
    def __init__(self, *args):
        super().__init__(*args)

class Waypoint(AbstractPositionDataObject):
    def __init__(self,*args):
        super().__init__(*args)    
    @staticmethod
    def zero():
        return Waypoint(0,0)