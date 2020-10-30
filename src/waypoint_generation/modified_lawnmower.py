from .base_wp_generator import BaseWPGenerator
from src.data_models.probability_map import ProbabilityMap
from src.data_models.positional.waypoint import Waypoint, Waypoints
from src.waypoint_generation.waypoint_factory import WaypointAlgSettings
import numpy as np
import itertools
import time

class ModifiedLawnmower(BaseWPGenerator):
    def __init__(self, **kwargs):
        self.settings = WaypointAlgSettings.ModifiedLawnmower()

        super().__init__(**kwargs)
        
        self.__normalize_columns_in_pm()
        

    @property
    def waypoints(self) -> Waypoints:
        N_vs = self.__calc_revisit()

        C_turn = np.square(np.arange(-self.settings.turn_radius+1,self.prob_map.shape[0]))
        for i in range(self.settings.turn_radius):
            C_turn[i] = np.iinfo(np.int16).max

        N_tv = sum(N_vs)

        N_perms = np.math.factorial(N_tv-1)
        arr_to_perm = []
        for i,visits in enumerate(N_vs):
            [arr_to_perm.append(i+1) for n in range(int(visits))]
        arr_to_perm.pop(0) # Remove start lane 

        perm_iter = itertools.permutations(np.random.permutation(arr_to_perm))

        cost_opt = np.inf
        p_opt = None
        c = 0
        t0 = time.time()

        test_perm_func = self.__test_permutation
        max_iter = self.settings.max_iter

        while True:
            try:
                perm = list(next(perm_iter))
            except StopIteration:
                break

            perm.insert(0,1)

            cost = test_perm_func(C_turn, perm)

            if cost<cost_opt:
                string = f"{100*float(c)/N_perms:.2f}% after {time.time()-t0:.1f}s and {c} iterations | New best: p_opt={p_opt} with cost={cost_opt}"
                print(int(len(string)*1.3)*' ',end='\r')
                print(string)
                cost_opt = cost
                p_opt = perm

            c+=1
            if c==1 or c%5000==0:
                string = f"{100*float(c)/(N_perms if N_perms<max_iter else max_iter):.2f}% after {time.time()-t0:.1f}s and {c}/{N_perms if N_perms<max_iter else max_iter} iterations | p_cur={perm} with cost={cost}"
                print(" "*len(string),end='\r')
                print(string,end='\r')

            if c%10000==0:
                perm_iter = itertools.permutations(np.random.permutation(arr_to_perm))

            if c >= max_iter: 
                break
        
        string = f"{100*float(c)/N_perms:.2f}% after {time.time()-t0:.1f}s and {c} iterations | p_opt={p_opt} with cost={cost_opt}"
        print(" "*len(string),end='\r')
        print(string,end='\n')

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

    def __test_permutation(self, C_turn: list, perm: list)-> float:
        pj_old = perm[0]
        cost = 0
        for pj in perm[1:]:
            cost += C_turn[pj-pj_old] # pj-pj_old is dist between lanes
            pj_old = pj
        return cost
        # ---> above took 10.5s over 1000000 iterations

        # return sum([C_turn[perm[f]-perm[f-1]] for f in range(1,len(perm))])
        # ---> above took 13.4s over 1000000

        # return sum([C_turn[f-g] for f,g in zip(perm[1:],perm[0:-1])])
        # 12.6s
        
        # cost = 0
        # for f,g in zip(perm[1:],perm[0:-1]):
        #     cost += C_turn[f-g]
        # return cost
        # 11.6s




    def __normalize_columns_in_pm(self) -> ProbabilityMap:
        # Map from 0->1 to 0->3
        prob_map = np.interp(self.prob_map.prob_map,(0,np.max(self.prob_map.prob_map)),(0,3))

        # Iterate over columns
        for i in range(prob_map.shape[0]):
            prob_map[:,i] = np.mean(prob_map[:,i])

        # Round to int
        prob_map = np.round(prob_map)

        self.prob_map = prob_map
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
            self.prob_map[i,:] -= 1

            # 5. Goto step 3 until path A is the last path (right border of the area).
            
            # Store
            N_vs[i] = N_vs_A
        return N_vs+1 # + 1 because otherwise 0 implies that it gets visited once which doens't make a lot of sense in the code. 







    