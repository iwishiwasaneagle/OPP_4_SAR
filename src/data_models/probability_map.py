import PIL
import numpy as np
from numpy.lib.utils import deprecate
from src.simulation.parameters import *
from typing import TypeVar
from PIL import Image
from src.data_models.positional.waypoint import Waypoint, Waypoints

from loguru import logger

T = TypeVar('T', bound='ProbabilityMap')

class ProbabilityMap:
    def __init__(self, prob_map: list) -> None:
        self.prob_map = np.copy(prob_map)/np.sum(prob_map)
    
    @classmethod
    def fromPNG(cls,img_path: str) -> T:
        img = Image.open(img_path)
        arr = np.array(img)
        if len(arr.shape)==3:
            mask = np.ones((arr.shape[0],arr.shape[1],4))
            mask[:,:,1:] = 0        
            return cls((mask*arr)[:,:,0])
        else:
            return cls(arr)

    def toIMG(self) -> PIL.Image:
        mask = np.ones((*self.shape,3))
        arr = np.reshape(self.prob_map,(*self.shape,1))
        arr = mask*arr
        img_arr = (
                np.interp(arr,[np.min(arr),np.max(arr)],[0,254])).astype(np.uint8)
        return PIL.Image.fromarray(img_arr)
    
    @property
    def shape(self) -> tuple:
        return self.prob_map.shape
    @property
    def max(self) -> float:
        return np.max(self.prob_map)
    @property
    def min(self) -> float:
        return np.min(self.prob_map)

    def resampled(self, x,y):
        img = Image.fromarray(self.prob_map).resize((x,y),Image.BOX)        
        return ProbabilityMap(np.array(img))
    
    def place(self, n:int=1) -> Waypoints:               
        x,y = np.meshgrid(np.arange(0,self.shape[1]),np.arange(0,self.shape[0]))
        x,y = x.flatten(),y.flatten()
        xy  = np.vstack((x,y)).T
        xy_indices = np.arange(len(xy))
        choices = np.random.choice(xy_indices, n, p=self.prob_map.flatten())
        points = xy[choices]
        return Waypoints(points)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.prob_map[key]
        elif isinstance(key, Waypoint):
            return self.__getitem__((key.x, key.y))
        elif isinstance(key, (np.ndarray,tuple, list)):
            i,j = key
            try:
                return self.prob_map[int(j),int(i)] # Images are stored line then column hence we use y x indexing 
            except IndexError:
                return -np.iinfo(np.int16).max
        raise KeyError(f"Type {type(key)} is not valid")
    
    def __setitem__(self, key, data):
        if isinstance(key, int):
            self.prob_map[key] = data
        elif isinstance(key, Waypoint):
            self.prob_map[key.x, key.y] = data
        elif isinstance(key, (tuple, list)):
            i,j = key
            self.prob_map[int(j),int(i)] = data # Images are stored line then column hence we use y x indexing
        else:
            raise KeyError(f"Type {type(key)} is not valid")

    def __len__(self):
        return len(self.prob_map) 