from .abstractPositionDataObjects import AbstractAngleDataObject
from typing import TypeVar

T = TypeVar('T', bound='Yaw')

class Yaw(AbstractAngleDataObject):
    def __init__(self,yaw:float):
        super().__init__(yaw)
    
    @staticmethod
    def zero() -> T:
        return Yaw(0)