import numpy as np
from simulation.parameters import *
from typing import TypeVar
from PIL import Image

T = TypeVar('T', bound='ProbabilityMap')


class ProbabilityMap:
    def __init__(self, prob_map: list):
        # if np.shape(prob_map) != (n,m):
        #     raise Exception(f"Invalid shape {np.shape(prob_map)}. ({n},{m}) was expected.")
        # if np.max(prob_map) > 1:
        #     raise Exception(f"Invalid maximum: {np.max(prob_map)}. Maximum allowed is 1")
        # if np.min(prob_map) < 0:
        #     raise Exception(f"Invalid minimum: {np.min(prob_map)}. Minimum allowed is 0")
        self.img = None
        self.prob_map = np.array(prob_map)/np.sum(prob_map)

    @staticmethod
    def fromPNG(img_path: str) -> T:
        img = Image.open(img_path)        
        prob =  ProbabilityMap(np.array(img)[:,:,0])
        prob.img = img
        return prob

    def toIMG(self) -> Image:
        return Image.fromarray(self._prob_map)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.prob_map[key]
        else:
            i,j = key
            return self.prob_map[int(j),int(i)]
    # def __iter__(self) -> T:
    #     self._i = 0
    #     self._j = 0
    #     return self
    # def __next__(self) -> float:
    #     if self._i < self.shape[0]:
    #         result = self.__getitem__((self._i, self._j))
    #         self._i += 1
    #         return result
    #     elif (self._j+1) < self.shape[1]:
    #         self._i=0
    #         self._j+=1
    #         result = self.__getitem__((self._i, self._j))
    #         self._i+=1
    #         return result
    #     else:
    #         raise StopIteration
    def __len__(self):
        return len(self.prob_map)          
    @property
    def shape(self) -> tuple:
        return np.shape(self.prob_map)