import json
from src.data_models.positional.waypoint import Waypoint
from src.data_models.abstractListObject import AbstractListObject
from .abstractPositionDataObjects import AbstractPositionDataObject
from typing import Type, TypeVar
T = TypeVar('T', bound='Pose')

class Pose(AbstractPositionDataObject):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x,y)
    
    @staticmethod
    def zero() -> T:
        return Pose(0,0)
    @staticmethod
    def fromWP(WP: Waypoint) -> T:
        return Pose(WP.x, WP.y)

    def __str__(self) -> str:
        return f"Pose({self.x},{self.y})"



class Poses(AbstractListObject):
    def __init__(self, *args):
        super().__init__(*args)

    # def fromFile(fid):
    #     raise NotImplementedError()
    # def toFile(self, fid):
    #     raise NotImplementedError()

    @property
    def x(self):
        return [f.x for f in self.items]
    @property
    def y(self):
        return [f.y for f in self.items]

    def __str__(self):
        return f"Poses([{', '.join([str(f) for f in self.items])}])"