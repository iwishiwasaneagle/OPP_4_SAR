from src.waypoint_generation.base_wp_generator import BaseWPGenerator
from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint,Waypoints
from src.waypoint_generation.waypoint_settings import WaypointAlgSettings
from src.simulation.parameters import *

import matplotlib.pyplot as plt
import numpy as np
import time
import multiprocessing
from enum import IntEnum

from typing import List

from loguru import logger

class ConvolutionType(IntEnum):
    LARGE = 3
    MEDIUM = 2
    SMALL = 1
    HYUGE = 4

class ConvolutionResult:
    def __init__(self,pos:Waypoint,value:float,n:int):
        self.pos = pos 
        self.value = value 
        self.n = n
    @property
    def bounds(self) -> List[Waypoint]:
        const = int((self.n-1)/float(2))
        lower_x = self.pos.x - const
        upper_x = self.pos.x + const 
        lower_y = self.pos.y - const 
        upper_y = self.pos.y + const
        return [Waypoint(lower_x, lower_y), Waypoint(upper_x, upper_y)]
    def __getitem__(self,key):
        if key == 0:   return self.pos
        elif key == 1: return self.value 
        elif key == 2: return self.n
        else :         raise IndexError(f"{key} > 2")

class LHC_GW_CONV(BaseWPGenerator):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.settings = WaypointAlgSettings.LHC_GW_CONV()

        self.search_threshold = 0

        self.animate = self.animate and not self.threaded
    @property
    def waypoints(self):
        return self.GW()

    def _inf(self) -> int:
        i = -1
        while True:
            if i>2500:
                break
            yield (i:=i+1)

    def GW(self) -> Waypoints:
        l_iterator = range(5,self.settings.l_value)
        t = time.time()
        return_dict = {}
        if self.threaded:
            logger.debug("Starting GW w/ threading")
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            jobs = []

            for l in l_iterator:
                p = multiprocessing.Process(target=self.LHC_CONV, args=(l,return_dict))
                jobs.append(p)
                p.start()
        
            for proc in jobs:
                proc.join()

            logger.debug(f"Finished GW w/ threading. Time taken: {time.time()-t:.2f}s")
        else:
            logger.debug("Starting GW w/o threading")
            for l in l_iterator:
                return_dict[l] = self.LHC_CONV(l,return_dict)
                
            logger.debug(f"Finished GW w/o threading. Time taken: {time.time()-t:.2f}s")

        best_l = None
        best_wps = None
        best_prob = -np.inf
        for key in return_dict:
            l = key
            wps = return_dict[key]

            probability = self.calc_prob(wps)
            if probability > best_prob:
                best_prob = probability
                best_wps = wps
                best_l = l

        logger.info(f"l={l} had {100*best_prob:.2f}% efficiency")
        return best_wps

    def LHC_CONV(self,l=0, ret_dict: dict={}) -> Waypoints:
        logger.debug(f"({l}) Starting LHC_CONV with l={l}")
        wps = []
        accumulator = 0
        visited = Waypoints([])

        cur = self.home_wp
        t = time.time()

        C = self.prob_map.max/float(l)
        temp_prob_map = ProbabilityMap(np.clip(self.prob_map.prob_map - C, 0, None))
        conflicts = 0
        for i in self._inf():
            if self.animate: plt.cla()
            neighbours = np.array(self.neighbours(cur, visited, temp_prob_map))
            try:
                best = None
                while best is None:
                    inds = np.where(neighbours[:,1]==np.max(neighbours[:,1]))[0]
                    ind = inds[0] # default

                    if len(inds) > 1 or np.max(neighbours[:,1]) < self.search_threshold: # More than 1 "best" probability was found
                        ind = None
                        convs = ConvolutionType.LARGE
                        if np.max(neighbours[:,1]) <= self.search_threshold:
                            convs = ConvolutionType.HYUGE 
                       
                        conv_probs = np.array([self.convolute(neighbours[f][0],visited,temp_prob_map,convs) for f in inds])

                        conv = [f.value for f in conv_probs]
                        conv_max = np.max(conv)
                        inds2 = np.where(conv==conv_max)
                        
                        if self.animate:
                            for f in conv_probs:
                                self._ax.add_artist(plt.Rectangle(f.bounds[0], f.n, f.n,fill=False, color=(f.value==conv_max,0,f.value!=conv_max)))
                                if f.value==conv_max:
                                    self._ax.add_artist(plt.Arrow(cur.x, cur.y, 3*(f.pos.x-cur.x), 3*(f.pos.y-cur.y)))

                        ind = inds2[0][0]
                        conflicts += 1

                    potential_best = neighbours[ind]

                    validated = self.validate(potential_best[0], visited, temp_prob_map) 
                    if validated or len(neighbours) == 1:
                        best = potential_best
                    else:
                        neighbours = np.delete(neighbours,ind,0)
                    
                    if self.animate: 
                       self._plot(cur, neighbours, potential_best[0], visited, temp_prob_map, l)
            except IndexError as e:
                break

            accumulator += best[1]
            best = best[0]
            wps.append(best)

            cur = wps[-1]
            visited.add(best)
           
        logger.debug(f"({l}) Completed in {time.time()-t:.3f}s with local score {accumulator:.4f} and {conflicts} conflicts", enqueue=True)
        

        wps = Waypoints([self.home_wp]+[Waypoint(f.x+0.5, f.y+0.5) for f in wps]+[self.home_wp]) # Bring the coord into the center of the square

        if self.threaded:
            ret_dict[l] = wps
        else: 
            return wps

    def convolute(self, pos: Waypoint, visited: Waypoints, prob_map: ProbabilityMap, conv_type: ConvolutionType):
        kernel = None
        n = 0
        if conv_type is ConvolutionType.SMALL:
            n = 3
        elif conv_type is ConvolutionType.MEDIUM:
            n = 5
        elif conv_type is ConvolutionType.LARGE:
            n = 7
        elif conv_type is ConvolutionType.HYUGE:
            n = 11
        else:
            raise TypeError(f"Unknown ConvolutionType: {type(conv_type)} with value {conv_type}")
        
        kernel = np.ones((n,n))

        sum_ = 0
        shift = int((n-1)/2)

        c = 1
        for i in range(n):
            for j in range(n):
                iprime, jprime =(i-shift, j-shift) 

                if (iprime,jprime) == (0,0): continue

                eval_pos = Waypoint(pos.x+iprime,pos.y+jprime)
                if eval_pos in visited: continue


                prob = prob_map[eval_pos] * kernel[i,j] 

                sum_ += prob
                c += 1
        return ConvolutionResult(pos,sum_/float(c),n)

    def validate(self, pos: Waypoint, visited: Waypoints, prob_map: ProbabilityMap):
        return len(self.neighbours(pos, visited, prob_map)) > 0 # True if 1 or more valid position exists
    
    def neighbours(self, pos: Waypoint, visited: Waypoints, prob_map: ProbabilityMap):
        neighbours = self.surrounding_grid(pos)
        return [(f, prob_map[f]) for f in neighbours if min(f) >= 0 and f.x <= prob_map.shape[0]-0.5 and f.y <= prob_map.shape[1]-0.5 if f not in visited]

    def calc_prob(self,wps: Waypoints) -> float:
        accumulator = 0
        if not isinstance(wps, Waypoints): 
            raise TypeError(f"wps is type {type(wps)} and not {Waypoints}")
        for wp in wps:
            accumulator += self.prob_map[wp]
        return accumulator

    def surrounding_grid(self, pos: Waypoint) -> list:
        tmp = [
            (-1, -1),
            (1, -1),
            ( 0,-1),
            (-1,1),
            (1,1),
            ( 0, 1),
            (-1, 0),
            ( 1, 0),
        ]
        return [Waypoint(pos.x+f[0],pos.y+f[1]) for f in tmp]
    
    def _plot(self, cur:Waypoint, neighbours: Waypoints, best: Waypoint, visited: Waypoints, prob_map: ProbabilityMap, l_val:float) -> None:
        if len(visited) > 0:
            self._ax.plot(visited.x,visited.y, color='r')
        for i in neighbours:
            self._ax.add_artist(plt.Circle(i[0], size, color='b'))
        self._ax.add_artist(plt.Circle((cur.x,cur.y), size, color='r'))
        self._ax.add_artist(plt.Circle(best, size, color='g'))
        img = prob_map.toIMG()
        self._ax.imshow(img)
        self._ax.set_ylabel("Y")
        self._ax.set_xlabel("X")
        self._ax.set_title(f"l={l_val}")
        plt.pause(0.001)
       

def main():
    import matplotlib.pyplot as plt
    wps = LHC_GW_CONV(ProbabilityMap.fromPNG("waypoint_generation/probs_map_1.png"), Waypoint(0,0)).LHC()

    plt.figure()
    plt.imshow(wps.prob_map.img.rotate(90))
    plt.show()

    print(wps)

