import src.simulation.simulation as sim
from src.data_models.positional.waypoint import Waypoint, Waypoints
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np 
from src.simulation.parameters import *

import json
import time
import os
import argparse
import sys

from loguru import logger

from src.data_models.probability_map import ProbabilityMap
from src.waypoint_generation import WaypointFactory, CostFunc
from src.enums import WaypointAlgorithmEnum, PABOSolverEnum

header = """
   ____   _____ _____   _  _      _____         _____  
  / __ \ / ____/ ____| | || |    / ____|  /\   |  __ \ 
 | |  | | (___| (___   | || |_  | (___   /  \  | |__) |
 | |  | |\___ \\___ \  |__   _|  \___ \ / /\ \ |  _  / 
 | |__| |____) |___) |    | |    ____) / ____ \| | \ \ 
  \____/|_____/_____/     |_|   |_____/_/    \_\_|  \_\
"""

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return os.path.abspath(arg)

def is_valid_path_for_file(parser,arg):
    path = os.path.abspath(os.path.dirname(arg))
    if not os.path.exists(path):
        parser.error("The directory %s does not exist!" % path)
    else:
        return os.path.abspath(arg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Optimal Path Planning for SAR CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Prob map image
    parser.add_argument("--in_file", "-I",
        dest='filename', 
        required=False, 
        type=lambda x: is_valid_file(parser, x),
        default=os.path.join("img","probability_imgs","prob_map_1.png"),
        help="probability map image file path"
        )
    parser.add_argument("--shape",
        dest='shape',
        nargs=2,
        type=float,
        help="desired shape of the probability map"
    )

    # Algorithms
    parser.add_argument("-L",dest='lhc_gw_conv',action="store_true",help="calculate the LHC_GW_CONV path")
    parser.add_argument("-M",dest='modified_lawnmower',action="store_true",help="calculate the Modified Lawnmower path")
    parser.add_argument("-S" ,dest='parallel_swaths',action="store_true",help="calculate the Parallel Swaths path")

    parser.add_argument("-P",dest='pabo',action="store_true",help="calculate the (P)robability (A)ccumulation (B)ased (O)ptimisation path")
    choices=[str(f).split('.')[1].lower() for f in PABOSolverEnum]
    default=[choices[0]]
    parser.add_argument("--solver",dest='pabo_solver',nargs='+',help=f"select the solver for PABO",choices=choices, default=default)

    # Other
    parser.add_argument("--verbose","-v", dest='log_level', help="Log level", choices=['debug','info','error'], default='debug')
    parser.add_argument("--animate","-A",action="store_true",help="Animate calculations where possible")
    parser.add_argument("--threaded","-T",action="store_true",help="Thread calculations where possible")
    parser.add_argument("--out_file","-O", 
        default="output.json",
        dest="out_file",
        help="Thread calculations where possible",
        type=lambda x: is_valid_path_for_file(parser, x)
        )

    args = parser.parse_args()
    logger.remove(0)
    logger.add(sys.stderr,level=args.log_level.upper())
    logger.info("Starting...\n"+header)


    prob_map = ProbabilityMap.fromPNG(args.filename)
    if args.shape is not None:
        prob_map.lq_shape = args.shape
    
    dict_ = {}    
    if os.path.isfile(args.out_file.upper()):
        with open(args.out_file, 'r') as f:
            dict_ = json.loads(json.load(f))

    dict_['img'] = prob_map.lq_prob_map.tolist()

    algs = []
    if args.lhc_gw_conv: algs.append(WaypointAlgorithmEnum.LHC_GW_CONV)
    if args.modified_lawnmower: algs.append(WaypointAlgorithmEnum.MODIFIED_LAWNMOWER)
    if args.parallel_swaths: algs.append(WaypointAlgorithmEnum.PARALLEL_SWATHS)
    if args.pabo: 
        if "ga" in args.pabo_solver:
            algs.append(WaypointAlgorithmEnum.PABO_GA)
        if "fmincon" in args.pabo_solver:
            algs.append(WaypointAlgorithmEnum.PABO_FMINCON)
        if "particleswarm" in args.pabo_solver:
            algs.append(WaypointAlgorithmEnum.PABO_PARTICLESWARM)

    for alg in algs:
        middle = "|"+" "*8+f"{alg}" + " "*8 + "|"
        start = "-"*len(middle)
        end = start
        logger.info(start)
        logger.info(middle)
        logger.info(end)

        t = time.time()

        waypoints = WaypointFactory(alg, prob_map, threaded=args.threaded).generate()

        vehicle = sim.simulation(waypoints, animate=args.animate).run()
        
        alg_dict = {}
        alg_dict["wps"] = [(float(f.x),float(f.y)) for f in waypoints]
        alg_dict["time"] = time.time()-t
        alg_dict["vehicle"] = vehicle.data

        dict_[str(alg)] = alg_dict


    with open(args.out_file,'w') as f:
        data = json.dumps(dict_)
        json.dump(data, f)
    
    logger.info("Exiting")