from waypoint_generation.base_wp_generator import BaseWPGenerator
from data_models.probability_map import ProbabilityMap
from data_models.positional.waypoint import Waypoint,Waypoints

import matplotlib.pyplot as plt
import numpy as np

import time

from simulation.parameters import *
class LHC_GW_CONV(BaseWPGenerator):
    def __init__(self, prob_map: ProbabilityMap, start: Waypoint, end:Waypoint = None, l:int=40):
        super().__init__()

        self.prob_map = prob_map
        self.visited = []
        self.start = start
        self.end = end
        self.accumulator = 0
        # self.l = l

        # self.C

        if animate:
            plt.ion()
            fig = plt.figure()
            # for stopping simulation with the esc key.
            fig.canvas.mpl_connect('key_release_event',
                    lambda event: [exit(0) if event.key == 'escape' else None])

            self._ax = fig.add_subplot(111)

    @property
    def waypoints(self):
        return self.LHC()

    def LHC(self) -> Waypoints:
        wps = Waypoints()
        cur = self.start
        t = time.time()
        for i in range(2000):
            neighbours = np.array(self.neighbours(cur))
            try:
                best = neighbours[np.argmax(neighbours[:,1])]
            except IndexError:
                break

            self.accumulator += best[1]
            best = best[0]

            wps.add(Waypoint(best[0], best[1]))
            #self.prob_map.pop(best[0], best[1])
            if animate: 
                self._plot(cur, neighbours, best)
            cur = wps[-1]
            self.visited.append(best)
            
            
            # dt = time.time() - t
            # if dt < t_fast: t_fast = dt
            # elif dt > t_slow: t_slow = dt
            # ts.append((t,dt))
            # print(f"dt={dt:3f}s\tt_slow={t_slow:.3f}s\tt_fast={t_fast:.3f}s")
        # print(f"{self.accumulator/self.prob_map.max:.2f}% efficient")
        # plt.figure()
        # ts = np.array(ts)
        # plt.plot(ts[:,0], ts[:,1])
        # plt.show()
        print(f"Completed in {time.time()-t:.3f}s")
        return wps

    def neighbours(self, pos: Waypoint):
        neighbours = [
            (pos.x-1, pos.y-1),
            (pos.x+1, pos.y-1),
            (pos.x  , pos.y-1),

            (pos.x-1, pos.y+1),
            (pos.x+1, pos.y+1),
            (pos.x  , pos.y+1),
            
            (pos.x-1, pos.y),
            (pos.x+1, pos.y),
        ]

        return [(f, self.prob_map[f[0], f[1]]) for f in neighbours if min(f) > 0 and f[0] < self.prob_map.shape[0] and f[1] < self.prob_map.shape[1] if f not in self.visited]
    
    def _plot(self, cur, neighbours, best) -> None:
        plt.cla()
        
        if len(self.visited) > 0:
            visited = np.array(self.visited)
            self._ax.plot(visited[:,0],visited[:,1], color='r')

        for i in neighbours:
            self._ax.add_artist(plt.Circle(i[0], size, color='b'))

        self._ax.add_artist(plt.Circle((cur.x,cur.y), size, color='r'))
        self._ax.add_artist(plt.Circle(best, size, color='g'))

        plt.imshow(self.prob_map.toIMG())
        # plt.xlim(cur[0]-10,cur[0]+10)
        # plt.ylim(cur[1]-10,cur[1]+10)

        plt.pause(dt*0.01)
       

def main():
    import matplotlib.pyplot as plt
    wps = LHC_GW_CONV(ProbabilityMap.fromPNG("waypoint_generation/probs_map_1.png"), Waypoint(0,0)).LHC()

    plt.figure()
    plt.imshow(wps.prob_map.img)
    plt.show()

    print(wps)

