from src.waypoint_generation import pabo
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
===============================================================
      ____  _____  _____    _  _      _____         _____  
     / __ \|  __ \|  __ \  | || |    / ____|  /\   |  __ \ 
    | |  | | |__) | |__) | | || |_  | (___   /  \  | |__) |
    | |  | |  ___/|  ___/  |__   _|  \___ \ / /\ \ |  _  / 
    | |__| | |    | |         | |    ____) / ____ \| | \ \ 
     \____/|_|    |_|         |_|   |_____/_/    \_\_|  \_\
                                                        
                                                    
    Optimal Path Planning for Search and Rescue
===============================================================
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
#   ====================
#   | ARGUMENT PARSING |
#   ====================

    parser = argparse.ArgumentParser(
        description=header,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
============================================================================================
    OPP 4 SAR was created by Jan-Hendrik Ewers and falls under the GPL-3.0 License
============================================================================================
    '''
    )

    # Prob map image
    prob_map_group = parser.add_argument_group("PROBABILITY MAP")
    prob_map_group.add_argument("-I","--in_file",
        dest='filename', 
        metavar='FILENAME',
        required=False, 
        type=lambda x: is_valid_file(parser, x),
        default=os.path.join("img","probability_imgs","prob_map_1.png"),
        help="probability map image file path"
        )
    prob_map_group.add_argument("--shape",
        dest='shape',
        nargs=2,
        metavar=('X','Y'),
        type=int,
        help="desired shape of the probability map"
    )

    # Algorithms
    lhc_gw_conv_group = parser.add_argument_group('LHC_GW_CONV')
    lhc_gw_conv_group.add_argument("-L",dest='lhc_gw_conv',action="store_true",help="calculate the LHC_GW_CONV path")
    modified_lawnmower_group = parser.add_argument_group('MODIFIED_LAWNMOWER')    
    modified_lawnmower_group.add_argument("-M",dest='modified_lawnmower',action="store_true",help="calculate the Modified Lawnmower path")
    parallel_swaths_group = parser.add_argument_group('PARALLEL SWATHS')
    parallel_swaths_group.add_argument("-S" ,dest='parallel_swaths',action="store_true",help="calculate the Parallel Swaths path")
   
    pabo_group = parser.add_argument_group('PABO')
    pabo_group.add_argument("-P",dest='pabo',action="store_true",help="calculate the PABO path")
    choices=[str(f).split('.')[1].lower() for f in PABOSolverEnum]
    pabo_group.add_argument("--solver",
        dest='pabo_solver',
        nargs='+',
        help=f"select the solver for PABO",choices=choices, default=[choices[0]])

    # Operational
    operational = parser.add_argument_group('OPERATIONAL')
    operational.add_argument("-v", dest='log_level', help="Log level", action='count', default=1)
    operational.add_argument("-A","--animate",action="store_true",help="Animate calculations where possible")
    operational.add_argument("-T","--threaded",action="store_true",help="Thread calculations where possible")
    operational.add_argument("-O","--out_file",
        default="output.json",
        dest="out_file",
        metavar='FILENAME',
        help="Output file name in json format",
        type=lambda x: is_valid_path_for_file(parser, x)
        )

    args = parser.parse_args()


#   ================
#   | LOGGER SETUP |
#   ================

    logger.remove(0)
    if args.log_level == 0:
        log_level = 'ERROR'
    elif args.log_level == 1:
        log_level = 'INFO'
    elif args.log_level == 2:
        log_level = 'DEBUG'
    else: 
        log_level = 'TRACE'

    logger.add(sys.stderr,level=log_level)
    logger.info("Welcome to \n"+header+"\n")
    if args.log_level > 0:
        logger.debug(f'Log level set to {log_level}')


#   ======================
#   | DATA STORAGE SETUP |
#   ======================
    
    dict_ = {}    
    if os.path.isfile(args.out_file.upper()):
        with open(args.out_file, 'r') as f:
            dict_ = json.loads(json.load(f))


#   ==================
#   | PROB MAP SETUP |
#   ==================

    prob_map = ProbabilityMap.fromPNG(args.filename)
    if args.shape is not None:
        prob_map.lq_shape = args.shape
    dict_['img'] = prob_map.lq_prob_map.tolist()


#   ==============
#   | ALGS SETUP |
#   ==============

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


#   ================
#   | CALCULATIONS |
#   ================

    for alg in algs:
        middle = "|"+" "*8+f"{alg}" + " "*8 + "|"
        start = "-"*len(middle)
        end = start
        logger.info(start)
        logger.info(middle)
        logger.info(end)

        t = time.time()

        waypoints = WaypointFactory(alg, prob_map, animate=args.animate,threaded=args.threaded).generate()

        vehicle = sim.simulation(waypoints, animate=args.animate).run()
        
        alg_dict = {}
        alg_dict["wps"] = [(float(f.x),float(f.y)) for f in waypoints]
        alg_dict["time"] = time.time()-t
        alg_dict["vehicle"] = vehicle.data

        dict_[str(alg)] = alg_dict


#   ================
#   | DATA STORAGE |
#   ================

    with open(args.out_file,'w') as f:
        data = json.dumps(dict_)
        json.dump(data, f)
    
    logger.info("Exiting")