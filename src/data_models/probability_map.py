import numpy as np
from src.simulation.parameters import *
from typing import TypeVar
from PIL import Image, ImageOps
from src.data_models.positional.waypoint import Waypoint, Waypoints
from matplotlib.path import Path

T = TypeVar('T', bound='ProbabilityMap')


class ProbabilityMap:
    def __init__(self, prob_map: list):
        self.hq_prob_map = np.array(prob_map)/np.sum(prob_map)
        self.lq_prob_map = self.hq_prob_map
        
        self._hq_shape = np.shape(prob_map) # Bake it, for performance
        self._lq_shape = self._hq_shape
        
        assert(np.sum(self.hq_prob_map) == 1)
        
        self.max = np.max(prob_map)

    @staticmethod
    def fromPNG(img_path: str) -> T:
        img = Image.open(img_path)
        prob =  ProbabilityMap(np.array(img)[:,:,0])
        return prob

    def toIMG(self,prob_map=None) -> Image:
        if prob_map is None:
            prob_map = self.hq_prob_map

        img_arr = (
                np.interp(np.array([[(f,f,f) for f in g] for g in prob_map]),[np.min(prob_map),np.max(prob_map)],[0,254]
                    )).astype(np.uint8)
        img = Image.fromarray(img_arr)
        return img 

    def sum_along_path(self, path: Waypoints, radius:float=1) -> float:
        # Construct polygon
        pass
    
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
            self._lq_shape = val
            tmp_prob_map = np.array(self.toIMG().resize(val))[:,:,0]
            self.lq_prob_map = tmp_prob_map/np.sum(tmp_prob_map)
        else:
            raise Exception("Invalid value for lq_shape")
    
    def lq_to_hq_coords(self,*args):
        if len(args == 2):
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
                return Waypoints([self.lq_to_hq_coords(f.x, f.y) for f in arg])
    
        elif all([len(f) == 2 and isinstance(f, (tuple, list, Waypoint)) for f in args]):
            return [self.lq_to_hq_coords(f) for f in args]
        
        raise Exception()
    
    def hq_to_lq_coords(self,*args):
        if len(args == 2):
            x, y = args
            return (
                np.interp(x, (0,self.hq_shape[0]),(0,self.lq_shape[0])),
                np.interp(y, (0,self.hq_shape[1]),(0,self.lq_shape[1]))
                    )
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg,(tuple,list)) and len(arg) == 2:
                return self.lq_to_hq_coords(arg[0],arg[1])
            elif isinstance(arg,Waypoint):
                x,y = self.lq_to_hq_coords(arg.x,arg.y)
                return Waypoint(x,y)
            elif isinstance(arg,Waypoints):
                return Waypoints([self.lq_to_hq_coords(f.x, f.y) for f in arg])
    
        elif all([len(f) == 2 and isinstance(f, (tuple, list, Waypoint)) for f in args]):
            return [self.lq_to_hq_coords(f) for f in args]
        
        raise Exception()

    def sum_in_polygon(self,polygon: Waypoints, radius: float = 0, is_path_closed: bool = False) -> float:
        x,y = np.meshgrid(
            np.arange(self.shape[0]),
            np.arange(self.shape[1])
        )
        x,y = x.flatten(), y.flatten()
        points = np.vstack((x,y)).T
        poly = polygon
        p = Path(poly, closed=is_path_closed)
        grid = p.contains_points(points, radius = radius) 
        mask = grid.reshape(self.shape[0], self.shape[1])

        ret = self.prob_map*mask

        return ProbabilityMap(ret)


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