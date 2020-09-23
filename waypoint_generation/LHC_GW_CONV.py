from waypoint_generation.base_wp_generator import BaseWPGenerator
from data_models.probability_map import ProbabilityMap
from data_models.positional.waypoint import Waypoint,Waypoints

import matplotlib.pyplot as plt
import numpy as np

import time

import multiprocessing

from simulation.parameters import *
class LHC_GW_CONV(BaseWPGenerator):
    def __init__(self, prob_map: ProbabilityMap, start: Waypoint, end:Waypoint = None, l:int=40, animate: bool = animate):
        super().__init__()

        self.prob_map = prob_map
        self.start = start
        self.end = end
        self.l = l

        self.animate = animate
        if self.animate:
            plt.ion()
            fig = plt.figure()
            # for stopping simulation with the esc key.
            fig.canvas.mpl_connect('key_release_event',
                    lambda event: [exit(0) if event.key == 'escape' else None])

            self._ax = fig.add_subplot(111)

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
        l_iterator = range(5,self.l)
        t = time.time()
        print("Starting GW w/ threading")
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        jobs = []

        for l in l_iterator:
            p = multiprocessing.Process(target=self.LHC_CONV, args=(l,return_dict))
            jobs.append(p)
            p.start()
        
        for proc in jobs:
            proc.join()

        print(f"Finished GW w/ threading. Time taken: {time.time()-t:.2f}s")
        best_wps = None
        best_prob = 0
        for key in return_dict:
            l = key
            wps = return_dict[key]

            probability = self.calc_prob(wps)
            print(f"l={l} has score {probability}")
            if probability > best_prob:
                best_prob = probability
                best_wps = wps

        return best_wps

    def LHC_CONV(self,l=0, ret_dict: dict= None) -> None:
        print(f"({l})\tStarting LHC_CONV with l={l}")
        wps = []
        accumulator = 0
        visited = []

        cur = self.start
        t = time.time()

        C = self.prob_map.max/float(l)
        temp_prob_map = ProbabilityMap(np.clip(self.prob_map.prob_map - C, 0, None))
        conflicts = 0
        for i in self._inf():
            neighbours = np.array(self.neighbours(cur, visited, temp_prob_map))
            if i%100 == 0:
                print(f"({l})\tProgress: i={i}")


            try:
                best = None
                while best is None:
                    inds = np.where(neighbours[:,1]==np.max(neighbours[:,1]))[0]
                    ind = inds[0] # default
                    if len(inds) > 1: # More than 1 "best" probability was found
                        # Insert convolution kernel here
                        # set ind = the first for now
                        ind = inds[0]
                        conflicts += 1

                    potential_best = neighbours[ind]

                    validated = self.validate(potential_best[0], visited, temp_prob_map) 
                    if validated or len(neighbours) == 1:
                        best = potential_best
                    else:
                        neighbours = np.delete(neighbours,ind,0)
                    
                    if self.animate and ret_dict is None: 
                        self._plot(cur, neighbours, potential_best[0], visited)

            except IndexError as e:
                break

            accumulator += best[1]
            best = best[0]
            wps.append(best)

            cur = wps[-1]
            visited.append(best)
           
        print(f"({l})\tCompleted in {time.time()-t:.3f}s with local score {accumulator:.1f} and {conflicts} conflicts")
        ret_dict[l] = Waypoints(wps)

    def validate(self, pos: Waypoint, visited: list, prob_map: ProbabilityMap):
        return len(self.neighbours(pos, visited, prob_map)) > 0 # True if 1 or more valid position exists
    
    def neighbours(self, pos: Waypoint, visited: list, prob_map: ProbabilityMap):
        neighbours = self.surrounding_grid(pos)
        return [(f, prob_map[f]) for f in neighbours if min(f) >= 0 and f.x < prob_map.shape[0] and f.y < prob_map.shape[1] if f not in visited]

    def calc_prob(self,wps: list) -> float:
        accumulator = 0
        for wp in wps:
            accumulator += self.prob_map[wp]
        return accumulator

    def surrounding_grid(self, pos: Waypoint) -> list:
        tmp = [
            # (-1, -1),
            # (1, -1),
            ( 0,-1),
            # (-1,1),
            # (1,1),
            ( 0, 1),
            (-1, 0),
            ( 1, 0),
        ]
        return [Waypoint(pos.x+f[0],pos.y+f[1]) for f in tmp]
    
    def _plot(self, cur, neighbours, best, visited) -> None:
        plt.cla()
        
        if len(visited) > 0:
            visited = np.array(visited)
            self._ax.plot(visited[:,0],visited[:,1], color='r')

        for i in neighbours:
            self._ax.add_artist(plt.Circle(i[0], size, color='b'))

        self._ax.add_artist(plt.Circle((cur.x,cur.y), size, color='r'))
        self._ax.add_artist(plt.Circle(best, size, color='g'))

        img = self.prob_map.toIMG()
        plt.imshow(self.prob_map.toIMG(), origin='upper')
        plt.xlim(0,img.size[0])
        plt.ylim(0,img.size[1])

        plt.pause(0.001)
       

def main():
    import matplotlib.pyplot as plt
    wps = LHC_GW_CONV(ProbabilityMap.fromPNG("waypoint_generation/probs_map_1.png"), Waypoint(0,0)).LHC()

    plt.figure()
    plt.imshow(wps.prob_map.img.rotate(90))
    plt.show()

    print(wps)

