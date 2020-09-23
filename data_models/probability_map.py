import numpy as np
from simulation.parameters import *
from typing import TypeVar
from PIL import Image, ImageOps
from data_models.positional.waypoint import Waypoint

T = TypeVar('T', bound='ProbabilityMap')


class ProbabilityMap:
    def __init__(self, prob_map: list):
        self.prob_map = np.array(prob_map)
        self.sum = np.sum(prob_map)
        self.max = np.max(prob_map)
        self.shape = np.shape(prob_map) # Bake it, for performance

    @staticmethod
    def fromPNG(img_path: str) -> T:
        img = Image.open(img_path)
        prob =  ProbabilityMap(np.array(img)[:,:,0])
        return prob

    def toIMG(self) -> Image:
        img_arr = np.array([[(f,f,f) for f in g] for g in self.prob_map]).astype(np.uint8)
        img = Image.fromarray(img_arr)#ImageOps.flip(Image.fromarray(img_arr)).rotate(-90)
        return img 


    def __getitem__(self, key):
        if isinstance(key, int):
            return self.prob_map[key]
        elif isinstance(key, Waypoint):
            return self.__getitem__((key.x, key.y))
        elif isinstance(key, (tuple, list)):
            i,j = key
            return self.prob_map[int(j),int(i)]
        raise KeyError(f"Type {type(key)} is not valid")

    def __len__(self):
        return self.shape[0]          