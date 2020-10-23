import src.simulation.simulation as sim
from src.data_models.positional.waypoint import Waypoint, Waypoints
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np 
from src.simulation.parameters import *

import json
import time
import os

from src.data_models.probability_map import ProbabilityMap
from src.waypoint_generation.waypoint_factory import WaypointFactory, WaypointAlgorithmEnum

prob_map_img = "img/probability_imgs/prob_map_3_multimodal.png"


if __name__ == "__main__":
    prob_map = ProbabilityMap.fromPNG(prob_map_img)
    prob_map.lq_shape = (15,15)

    dict_ = {}    
    fname = 'algorithms_output.json'
    # if os.path.isfile(fname):
    #     with open(fname, 'r') as f:
    #         dict_ = json.loads(json.load(f))

    dict_['img'] = prob_map.lq_prob_map.tolist()

    for alg in [WaypointAlgorithmEnum.CONSTANT_SPEED,WaypointAlgorithmEnum.PARALLEL_SWATHS ,WaypointAlgorithmEnum.LHC_GW_CONV_E]:#, WaypointAlgorithmEnum.MODIFIED_LAWNMOWER]:

        
        t = time.time()

        waypoints = WaypointFactory(alg, prob_map, Waypoint(0,0),threaded=True,animate=False).generate()
        # waypoints = prob_map.lq_to_hq_coords(waypoints)

        # sim = sim.simulation(waypoints, animate=False)
        # vehicle = sim.run()
        
        alg_dict = {}
        alg_dict["wps"] = [(float(f.x),float(f.y)) for f in waypoints]
        alg_dict["time"] = time.time()-t

        dict_[str(alg)] = alg_dict


    with open(fname,'w') as f:
        data = json.dumps(dict_)
        json.dump(data, f)
    
    print("Exiting")