import numpy as np
from numpy.lib.utils import deprecate
from src.simulation.parameters import *
from typing import TypeVar, List, Tuple
from PIL import Image, ImageOps
from src.data_models.positional.waypoint import Waypoint, Waypoints
import matplotlib.path as mpp
import matplotlib.transforms as mpt

import matplotlib.pyplot as plt

from loguru import logger

T = TypeVar('T', bound='ProbabilityMap')


class ProbabilityMap:
    def __init__(self, prob_map: list):
        self.hq_prob_map = np.array(prob_map)/np.sum(prob_map)
        self.lq_prob_map = self.hq_prob_map
        
        self._hq_shape = np.shape(prob_map) # Bake it, for performance
        self._lq_shape = self._hq_shape
        
        assert(np.isclose(np.sum(self.hq_prob_map),1))
        
    @staticmethod
    def fromPNG(img_path: str) -> T:
        img = Image.open(img_path)
        prob =  ProbabilityMap(np.array(img)[:,:,0])
        return prob

    def toIMG(self,prob_map_hq=True) -> Image:
        if prob_map_hq:
            prob_map = self.hq_prob_map
        else:
            prob_map = self.lq_prob_map
        img_arr = (
                np.interp(np.array([[(f,f,f) for f in g] for g in prob_map]),[np.min(prob_map),np.max(prob_map)],[0,254]
                    )).astype(np.uint8)
        img = Image.fromarray(img_arr)
        return img 

    @property
    def max(self) -> float:
        return np.max(self.prob_map)
    @property
    def prob_map(self) -> list:
        return self.lq_prob_map
    @property
    def shape(self) -> list:
        return self.hq_shape
    @property
    def hq_shape(self) -> list:
        return self._hq_shape
    @property
    def lq_shape(self) -> list:
        return self._lq_shape
    @lq_shape.setter
    def lq_shape(self,val) -> None:
        if isinstance(val, (tuple,list)) and len(val) == 2:
            logger.debug(f"Resizing probability map to {val}")
            self._lq_shape = val
            tmp_prob_map = np.array(self.toIMG().resize(val))[:,:,0]
            self.lq_prob_map = tmp_prob_map/np.sum(tmp_prob_map)
        else:
            raise Exception("Invalid value for lq_shape")
    
    def lq_to_hq_coords(self,*args):
        if len(args) == 2:
            x, y = args
            return (
                np.interp(x, (0,self.lq_shape[0]),(0,self.hq_shape[0])),
                np.interp(y, (0,self.lq_shape[1]),(0,self.hq_shape[1]))
                    )
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg,(tuple,list)) and len(arg) == 2:
                return self.lq_to_hq_coords(arg[0],arg[1])
            elif isinstance(arg,Waypoint):
                x,y = self.lq_to_hq_coords(arg.x,arg.y)
                return Waypoint(x,y)
            elif isinstance(arg,Waypoints):
                return Waypoints([Waypoint(self.lq_to_hq_coords(f.x, f.y)) for f in arg])
    
        elif all([len(f) == 2 and isinstance(f, (tuple, list, Waypoint)) for f in args]):
            return [self.lq_to_hq_coords(f) for f in args]
        
        raise Exception()
    
    def hq_to_lq_coords(self,*args):
        if len(args) == 2:
            x, y = args
            return (
                np.interp(x, (0,self.hq_shape[0]),(0,self.lq_shape[0])),
                np.interp(y, (0,self.hq_shape[1]),(0,self.lq_shape[1]))
                    )
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg,(tuple,list,np.ndarray)) and len(arg) == 2:
                return self.lq_to_hq_coords(arg[0],arg[1])
            elif isinstance(arg,Waypoint):
                x,y = self.lq_to_hq_coords(arg.x,arg.y)
                return Waypoint(x,y)
            elif isinstance(arg,Waypoints):
                return Waypoints([Waypoint(self.lq_to_hq_coords(f.x, f.y)) for f in arg])
    
        elif all([len(f) == 2 and isinstance(f, (tuple, list, Waypoint)) for f in args]):
            return [self.lq_to_hq_coords(f) for f in args]
        
        raise Exception(args)

    @deprecate
    def sum_along_path(self,polygon: Waypoints, px_radius: float = 1, prob_map_hq=True, show: bool = False) -> float:
        prob_map = self.hq_prob_map if prob_map_hq else self.lq_prob_map

        x,y = np.meshgrid(np.arange(0,prob_map.shape[0]),np.arange(0,prob_map.shape[1]))
        x,y = x.flatten(),y.flatten()
        points = np.vstack((x,y)).T
        
        assert(isinstance(polygon, (Waypoints,np.ndarray)))
        if isinstance(polygon,Waypoints): lines = polygon.toNumpyArray()
        else: lines = polygon
        lines = np.append(lines,lines[::-1],0)

        polygon = mpp.Path(lines)
        grid = (polygon.contains_points(points,radius=px_radius)).reshape(prob_map.shape[0],prob_map.shape[1])

        cost = np.sum(prob_map*grid)


        if show:
            print(f"cost = {cost:.5f}")
            plt.figure()
            plt.imshow(prob_map*grid, cmap='hot', interpolation='nearest')
            plt.xlim(0,prob_map.shape[0])
            plt.ylim(0,prob_map.shape[1])
            plt.show()

        return cost

    def place(self, n:int=1,prob_map_hq=True) -> Waypoints:
        prob = self.hq_prob_map if prob_map_hq else self.lq_prob_map
        
        x,y = np.meshgrid(np.arange(0,prob.shape[0]),np.arange(0,prob.shape[1]))
        x,y = x.flatten(),y.flatten()
        xy  = np.vstack((x,y)).T

        xy_indices = np.arange(len(xy))

        choices = np.random.choice(xy_indices, n, p=prob.flatten())

        points = xy[choices]

        return Waypoints(points)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.prob_map[key]
        elif isinstance(key, Waypoint):
            return self.__getitem__((key.x, key.y))
        elif isinstance(key, (tuple, list)):
            i,j = key
            try:
                return self.prob_map[int(j),int(i)]
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
            self.prob_map[int(j),int(i)] = data
        else:
            raise KeyError(f"Type {type(key)} is not valid")

    def __len__(self):
        return self.shape[0]          
