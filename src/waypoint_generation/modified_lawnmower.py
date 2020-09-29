from .base_wp_generator import BaseWPGenerator
from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint, Waypoints
import numpy as np
import itertools
import time

class ModifiedLawnmower(BaseWPGenerator):
    def __init__(self, turn_radius:int=2, max_iter: int=np.iinfo(np.int64).max, **kwargs):
        self.turn_radius = turn_radius
        self.max_iter = max_iter

        super().__init__(**kwargs)
        
        self.__normalize_columns_in_pm()
        

    @property
    def waypoints(self) -> Waypoints:
        N_vs = self.__calc_revisit()

        C_turn = np.square(np.arange(-self.turn_radius+1,self.prob_map.shape[0]))
        for i in range(self.turn_radius):
            C_turn[i] = np.iinfo(np.int16).max

        N_tv = sum(N_vs)

        N_perms = np.math.factorial(N_tv)
        arr_to_perm = []
        for i,visits in enumerate(N_vs):
            [arr_to_perm.append(i+1) for n in range(int(visits))]

        perm_iter = itertools.permutations(np.random.permutation(arr_to_perm))

        cost_opt = np.inf
        theoretical_cost_opt = np.sum([np.min(C_turn) for f in arr_to_perm])
        p_opt = None
        c = 0
        t0 = time.time()

        for perm in perm_iter:
            pj_old = perm[0]
            cost = 0
            for pj in perm[1:]:
                cost += C_turn[pj-pj_old] # pj-pj_old is dist between lanes
                pj_old = pj

            if cost<cost_opt:
                string = f"{100*float(c)/N_perms:.2f}% after {time.time()-t0:.1f}s and {c} iterations | New best: p_opt={p_opt} with cost={cost_opt}"
                print(string)
                cost_opt = cost
                p_opt = perm

            c+=1
            if c==1 or c%5000==0:
                string = f"{100*float(c)/N_perms:.2f}% after {time.time()-t0:.1f}s and {c}/{N_perms if N_perms<self.max_iter else self.max_iter} iterations | p_cur={perm} with cost={cost}"
                print(" "*len(string),end='\r')
                print(string,end='\r')
            if c >= self.max_iter or cost_opt<=theoretical_cost_opt*20: 
                break
        
        string = f"{100*float(c)/N_perms:.2f}% after {time.time()-t0:.1f}s and {c} iterations | p_opt={p_opt} with cost={cost_opt} (best possible is {theoretical_cost_opt})"
        print(" "*len(string),end='\r')
        print(string,end='\r')

        wps = Waypoints([Waypoint(0,0)])

        lower_y,upper_y = (1,self.prob_map.shape[1]-1)

        
        at_bottom = True
        for p in p_opt:
            if at_bottom:
                wps.add(
                   Waypoint(p,lower_y),
                )
                wps.add(
                   Waypoint(p,upper_y),
                )
            else:
                wps.add(
                   Waypoint(p,upper_y),
                )
                wps.add(
                   Waypoint(p,lower_y),
                )
            at_bottom = not at_bottom
        
        return wps



    def __normalize_columns_in_pm(self) -> ProbabilityMap:
        # Map from 0->254 to 0->2
        self.prob_map.prob_map = np.interp(self.prob_map.prob_map,(0,254),(0,2))

        # Iterate over columns
        for i in range(self.prob_map.shape[0]):
            self.prob_map.prob_map[:,i] = np.mean(self.prob_map.prob_map[:,i])

        # Round to int
        self.prob_map.prob_map = np.round(self.prob_map.prob_map)

        return self

    def __calc_revisit(self) -> list:
        # Consider an area with size of L rows and D columns. Construct D − 1 paths along the vertical lines (exclude the left border). Let the path spacing be half of the width of the sensor footprint.
        L,D = self.prob_map.shape
        num_paths = D - 1
        spacing = 1
        N_vs = np.zeros(num_paths)

        # 2. Let the first path (most left) be path A. The other parameters are defined as shown in Figure 6.
        A = None
        B = None
        for i in range(1,num_paths):
            A = i
            B = i+1
            UL = self.prob_map[i-1,0]
            UR1 = self.prob_map[i,0]
            UR2 = self.prob_map[i+1,0]

            # 3. Compute the revisit number for path A, Nvs(A), using Equation 8.
            N_vs_A = max(UL,UR1-UR2)

            # 4. Update the right lane uncertainty that is reduced by Nvs(A)
            self.prob_map.prob_map[i,:] -= 1

            # 5. Goto step 3 until path A is the last path (right border of the area).
            
            # Store
            N_vs[i] = N_vs_A
        return N_vs+1 # + 1 because otherwise 0 implies that it gets visited once which doens't make a lot of sense in the code. 







    