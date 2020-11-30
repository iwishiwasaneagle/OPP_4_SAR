from typing import TypeVar, List
import numpy as np
from abc import ABC, abstractmethod
T = TypeVar('T',bound='AbstractListObject')

class AbstractListObject(ABC):
    def __init__(self,*args) -> None:
        if len(args) == 1 and isinstance(args[0],(tuple, list)):
            args = args[0]   
        self.items: List = [f for f in args]

    def __getitem__(self,key) -> T:
        return self.items.__getitem__(key)

    def __iter__(self) -> T:
        self._n = 0
        return self

    def __next__(self) -> T:
        if self._n<self.__len__():
            result = self.items[self._n]
            self._n += 1
            return result
        else:
            raise StopIteration

    def __len__(self) -> None:
        return len(self.items)

    def add(self,item:T)-> None:
        self.items.append(item)
    
    def __str__(self):
        return f"{type(self)} {[str(f) for f in self.items]}"

    def toNumpyArray(self):
        return np.array(self.items)

    # @abstractmethod
    # def toFile(self, fid):
    #     raise NotImplementedError()

    # @staticmethod
    # @abstractmethod
    # def fromFile(fid):
    #     raise NotImplementedError()

