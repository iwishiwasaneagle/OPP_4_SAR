from abc import ABC, abstractmethod

class AbstractPoseDataObject(ABC):
    def __init__(self, a, b, c):
        self._a = a
        self._b = b 
        self._c = c 
    
    @staticmethod
    @abstractmethod
    def zero():
        raise NotImplementedError()

    def __getitem__(self,key:int):
        if key == 0:
            return self._a
        elif key == 1:
            return self._b
        elif key == 2:
            return self._c
        else:
            raise KeyError(f"Index key:{key} out of range for XYZ indexing (max. 2)")

    def __iter__(self):
        self._n = 0
        return self

    def __next__(self):
        if self._n < self.__len__():
            result = self.__getitem__(self._n)
            self._n += 1
            return result  
        else:
            raise StopIteration

    def __len__(self):
        return 3


class AbstractPositionDataObject(AbstractPoseDataObject):
    def __init__(self, x,y,z):
        self._a = x
        self._b = y
        self._c = z

    @property
    def x(self) -> float:
        return self._a
    @x.setter 
    def x(self, x:float) -> None:
        self._a = x
    @x.deleter
    def x(self) -> None:
        del self._a
    @property
    def y(self) -> float:
        return self._b
    @y.setter 
    def y(self, x:float) -> None:
        self._b = x
    @y.deleter
    def y(self) -> None:
        del self._b
    @property
    def z(self) -> float:
        return self._c
    @z.setter 
    def z(self, z:float) -> None:
        self._c = z
    @z.deleter
    def z(self) -> None:
        del self._c
    
class AbstractAngleDataObject(AbstractPoseDataObject):
    def __init__(self, roll,pitch,yaw):
        self._a = roll
        self._b = pitch
        self._c = yaw

    @property
    def roll(self) -> float:
        return self._a
    @roll.setter 
    def roll(self, roll:float) -> None:
        self._a = roll
    @roll.deleter
    def roll(self) -> None:
        del self._a
    @property
    def pitch(self) -> float:
        return self._b
    @pitch.setter 
    def pitch(self, roll:float) -> None:
        self._b = roll
    @pitch.deleter
    def pitch(self) -> None:
        del self._b
    @property
    def yaw(self) -> float:
        return self._c
    @yaw.setter 
    def yaw(self, yaw:float) -> None:
        self._c = yaw
    @yaw.deleter
    def yaw(self) -> None:
        del self._c
