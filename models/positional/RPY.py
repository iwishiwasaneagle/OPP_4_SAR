from .abstractPositionDataObjects import AbstractAngleDataObject
from typing import TypeVar

T = TypeVar('T', bound='RPY')

class RPY(AbstractAngleDataObject):
    def __init__(self,roll:float, pitch:float, yaw:float):
        super().__init__(roll,pitch,yaw)
    
    @staticmethod
    def zero() -> T:
        return RPY(0,0,0)