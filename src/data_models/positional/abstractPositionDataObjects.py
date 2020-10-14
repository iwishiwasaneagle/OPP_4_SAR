from abc import ABC, abstractmethod
import numbers

class AbstractPoseDataObject(ABC):
    def __init__(self, *args):
        a,b=None,None
        if len(args) >= 3:
            raise Exception(f"Too many input arguments. 3 expected, received {len(args)}")
        elif len(args) == 2 and all([isinstance(f,numbers.Real) for f in args]):
            a,b = args
        elif len(args) == 1 and isinstance(args[0],(tuple, list)):
            a,b = args[0]
        else:
            a,b,=0,0
        if None in (a,b): raise Exception()
        self._a = a
        self._b = b        
    def __str__(self):
        return f"{type(self)}:({self._a},{self._b})"
    
    @staticmethod
    @abstractmethod
    def zero():
        raise NotImplementedError()

    def __getitem__(self,key:int):
        if key == 0:
            return self._a
        elif key == 1:
            return self._b
        else:
            raise KeyError(f"Index key:{key} out of range for XYZ indexing (max. 1)")

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
        return 2 

    def __eq__(self, value):
        if isinstance(value, (AbstractPoseDataObject, list, tuple)):
            return value[0] == self.__getitem__(0) and value[1] == self.__getitem__(1)
        return False
    def __ne__(self, value):
        return not self.__eq__(value)


class AbstractPositionDataObject(AbstractPoseDataObject):
    def __init__(self, *args):
        super().__init__(*args)

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
    
class AbstractAngleDataObject(AbstractPoseDataObject):
    def __init__(self, yaw):
        super().__init__(yaw,0)

    @property
    def yaw(self) -> float:
        return self._a
    @yaw.setter 
    def yaw(self, yaw:float) -> None:
        self._a = yaw
    @yaw.deleter
    def yaw(self) -> None:
        del self._a

    def __getitem__(self,key:int):
        if key == 0:
            return self._a
        else:
            raise KeyError(f"Index key:{key} out of range for yaw indexing (max. 0)")

    def __len__(self):
        return 1