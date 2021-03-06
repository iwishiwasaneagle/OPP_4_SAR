#!/usr/bin/env python

__author__ = "Jan-Hendrik Ewers"
__copyright__ = "Copyright 2020, Jan-Hendrik Ewers"
__credits__ = ["Jan-Hendrik Ewers"]
__license__ = "GPL"
__version__ = "3.0.0"
__maintainer__ = "Jan-Hendrik Ewers"
__email__ = "jh.ewers@gmail.com"
__status__ = "prototype"

import functools
import multiprocessing
from src.json_helpers import GlobalJsonDecoder, GlobalJsonEncoder
from src.simulation.simulation import SimRunnerOutput
from src.waypoint_generation.waypoint_settings import SarGenOutput, WpGenOutput
from src.data_models.positional.waypoint import Waypoint, Waypoints

import src.simulation.simulation as sim
from src.simulation.parameters import *

import json
import time
import os
import argparse
import sys
import re
os.environ['OPP4SAR_DIR'] = os.path.dirname(os.path.realpath(sys.argv[0]))

from loguru import logger

import matplotlib.pyplot as plt

from src.data_models.probability_map import ProbabilityMap
from src.waypoint_generation import WaypointFactory
from src.enums import WaypointAlgorithmEnum, PABOSolverEnum

header_main = """
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

header_wp = """
===================================================
    __          _______     _____ ______ _   _ 
    \ \        / /  __ \   / ____|  ____| \ | |
     \ \  /\  / /| |__) | | |  __| |__  |  \| |
      \ \/  \/ / |  ___/  | | |_ |  __| | . ` |
       \  /\  /  | |      | |__| | |____| |\  |
        \/  \/   |_|       \_____|______|_| \_|

===================================================
"""

header_sar_setup = """
=====================================================================
      _____         _____     _____ ______ _______ _    _ _____  
     / ____|  /\   |  __ \   / ____|  ____|__   __| |  | |  __ \ 
    | (___   /  \  | |__) | | (___ | |__     | |  | |  | | |__) |
     \___ \ / /\ \ |  _  /   \___ \|  __|    | |  | |  | |  ___/ 
     ____) / ____ \| | \ \   ____) | |____   | |  | |__| | |     
    |_____/_/    \_\_|  \_\ |_____/|______|  |_|   \____/|_|     
                                                              
=====================================================================
"""

header_simulate = """
================================================================
      _____ _____ __  __ _    _ _            _______ ______ 
     / ____|_   _|  \/  | |  | | |        /\|__   __|  ____|
    | (___   | | | \  / | |  | | |       /  \  | |  | |__   
     \___ \  | | | |\/| | |  | | |      / /\ \ | |  |  __|  
     ____) |_| |_| |  | | |__| | |____ / ____ \| |  | |____ 
    |_____/|_____|_|  |_|\____/|______/_/    \_\_|  |______|

================================================================
"""

epilog = """
============================================================================================
    OPP 4 SAR was created by Jan-Hendrik Ewers and falls under the GPL-3.0 License
============================================================================================
    """


def min_length(nmin):
    class MinLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not nmin <= len(values) and not isinstance(values[0],(SarGenOutput,WpGenOutput)):
                msg = f"Argument \"{self.dest}\" requires at least {nmin} coordinates ({len(values)} received)"
                parser.error(msg)
            setattr(args, self.dest, values)
    return MinLength

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return os.path.abspath(arg)

def is_valid_path_for_file(parser, arg):
    path = os.path.abspath(os.path.dirname(arg))
    if not os.path.exists(path):
        parser.error("The directory %s does not exist!" % path)
    else:
        return os.path.abspath(arg)

def is_valid_wps_or_wpout_file(parser, arg):
    r = r'([0-9]+(?:\.[0-9]+)?),([0-9]+(?:\.[0-9]+)?)'
    res = re.findall(r, arg)
    if len(res) == 0 and not os.path.isfile(arg):
        parser.error(f"Incorrect waypoint pattern or filename in \"{arg}\"")
    else:
        ret = None
        if len(res) > 0:
            x,y = res[0]
            ret = Waypoint(float(x),float(y))
        else:
            with open(arg,'r') as f:
                ret = json.load(f,cls=GlobalJsonDecoder)
                if not isinstance(ret,WpGenOutput):
                   parser.error(f"Invalid file data ({type(ret)})") 
        return ret

def is_valid_sar_placements_or_file(parser,arg):
    r = r'([0-9]+(?:\.[0-9]+)?),([0-9]+(?:\.[0-9]+)?)'
    res = re.findall(r, arg)
    if len(res) == 0 and not os.path.isfile(arg):
        parser.error(f"Incorrect waypoint pattern or filename in \"{arg}\"")
    else:
        ret = None
        if len(res) > 0:
            x,y = res[0]
            ret = Waypoint(float(x),float(y))
        else:
            with open(arg,'r') as f:
                ret = json.load(f,cls=GlobalJsonDecoder)
                if not isinstance(ret,SarGenOutput):
                   parser.error(f"Invalid file data ({type(ret)})") 
        return ret

def setup_wp_gen_parser(parser) -> None:
    # Algorithms
    lhc_gw_conv_group = parser.add_argument_group('LHC_GW_CONV')
    lhc_gw_conv_group.add_argument(
        "-L", dest='lhc_gw_conv', action="store_true", help="calculate the LHC_GW_CONV path")
    modified_lawnmower_group = parser.add_argument_group('MODIFIED_LAWNMOWER')
    modified_lawnmower_group.add_argument(
        "-M", dest='modified_lawnmower', action="store_true", help="calculate the Modified Lawnmower path")
    parallel_swaths_group = parser.add_argument_group('PARALLEL SWATHS')
    parallel_swaths_group.add_argument(
        "-S", dest='parallel_swaths', action="store_true", help="calculate the Parallel Swaths path")

    pabo_group = parser.add_argument_group('PABO')
    pabo_group.add_argument(
        "-P", dest='pabo', action="store_true", help="calculate the PABO path")
    choices = [str(f).split('.')[1].lower() for f in PABOSolverEnum]
    pabo_group.add_argument("--solver",
                            dest='pabo_solver',
                            nargs='+',
                            help=f"select the solver for PABO", choices=choices, default=[choices[0]])

    # Operational
    operational = parser.add_argument_group('OPERATIONAL')
    operational.add_argument('--home',
        type=float,nargs=2,default=(-1,-1),help="Home for the paths. Defaults to no home.")
    operational.add_argument(
        "-A", "--animate", action="store_true", help="Animate calculations where possible")
    operational.add_argument(
        "-T", "--threaded", action="store_true", help="Thread calculations where possible")
    operational.add_argument("-O", "--out_file",
                             default="output_wp.json",
                             dest="out_file",
                             metavar='FILENAME',
                             help="Output file name in json format",
                             type=lambda x: is_valid_path_for_file(parser, x)
                             )

def setup_sar_parser(parser) -> None:
    parser.add_argument('-n',
                        help="The amount of persons placed on the map",
                        type=int,
                        default=10,
                        dest="num_persons"
                        )
    parser.add_argument("-O", "--out_file",
                        dest="out_file",
                        default="output_sar.json",
                        metavar='FILENAME',
                        help="Output file name in json format",
                        type=lambda x: is_valid_path_for_file(parser, x)
                        )
    parser.add_argument('-V', '--visualize',
                        dest="visualize",
                        help="Visualize the output before quiting (requires matplotlib)",
                        action="store_true")

def setup_sim_parser(parser) -> None:
    parser.add_argument('WPS',
                        help="Input waypoints to the simulation",
                        nargs="+",
                        action=min_length(2),
                        type=lambda x: is_valid_wps_or_wpout_file(parser, x))
    parser.add_argument("-o", "--object_location",
                        dest='object_location',
                        help=f"Input search object location. Can be multiple space seperated inputs for multiple simulations or output file from `wp`.",
                        nargs='+', 
                        action=min_length(1), 
                        type=lambda x: is_valid_sar_placements_or_file(parser, x))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-5', '--quintic_polynomial', action='store_true')
    group.add_argument('-F', '--fmincon', action='store_true')

    parser.add_argument('--flight_speed',help="Mean flight speed of the point mass (m/s)",default=1.0,type=float)
    
    operational = parser.add_argument_group('OPERATIONAL')
    operational.add_argument("-O", "--out_file",
                             default="output_sim.json",
                             dest="out_file",
                             metavar='FILENAME',
                             help="Output file name in json format",
                             type=lambda x: is_valid_path_for_file(parser, x)
                             )
    group = operational.add_mutually_exclusive_group()
    group.add_argument(
        "-T", "--threaded", action="store_true", help="Thread calculations where possible")
    group.add_argument(
        "-A", "--animate", action="store_true", help="Animate calculations where possible")
    
def do_wp_gen(args):
    #   ==================
    #   | PROB MAP SETUP |
    #   ==================

    prob_map = ProbabilityMap.fromPNG(args.filename)
    prob_map_original = prob_map
    logger.trace(f"ProbabilityMap({args.filename})")

    wp_gen_output = None
    if args.dimmensions is not None:
        width_m,height_m = args.dimmensions
        b = args.search_radius*2
        if any([b<1,width_m<b,height_m<b]):
            logger.warning(f"Values for search radius should be >1 or <dimmensions")

        args.home = Waypoint([f/b for f in args.home])
        # We want 1 pixel to match the physical dimmensions of the search radius
        prob_map = prob_map.resampled(int(width_m/b),int(height_m/b))
        prob_map_original = prob_map_original.resampled(int(width_m),int(height_m))
        
        wp_gen_output = WpGenOutput(prob_map_original)

    elif args.shape is not None:
        prob_map = prob_map.resampled(*args.shape)
        args.home = Waypoint.zero() # TODO implement properly

        wp_gen_output = WpGenOutput(prob_map)

    #   ==============
    #   | ALGS SETUP |
    #   ==============

    algs = []
    if args.lhc_gw_conv:
        algs.append(WaypointAlgorithmEnum.LHC_GW_CONV)
    if args.modified_lawnmower:
        algs.append(WaypointAlgorithmEnum.MODIFIED_LAWNMOWER)
    if args.parallel_swaths:
        algs.append(WaypointAlgorithmEnum.PARALLEL_SWATHS)
    if args.pabo:
        if "fmincon" in args.pabo_solver:
            algs.append(WaypointAlgorithmEnum.PABO_FMINCON)
        if "ga" in args.pabo_solver:
            algs.append(WaypointAlgorithmEnum.PABO_GA)
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

        # Gen WPS
        waypoints = WaypointFactory(
            alg, prob_map, animate=args.animate, threaded=args.threaded,home_wp=args.home).generate()

        if args.dimmensions is not None:
            waypoints = waypoints.interped((prob_map.shape[1],prob_map.shape[0]),args.dimmensions)  

        wp_gen_output.add_generated_wps(waypoints,time.time()-t,alg)
    
        # Animate
        if args.animate:
            img = prob_map.toIMG()
            if args.dimmensions is not None:
                img = prob_map_original.toIMG()
            plt.figure(1)
            plt.imshow(img)
            plt.plot(waypoints.x, waypoints.y)
            plt.show(block=True)

    #   ================
    #   | DATA STORAGE |
    #   ================

    with open(args.out_file, 'w') as f:
        json.dump(wp_gen_output,f,cls=GlobalJsonEncoder)

def do_sar(args):
    prob_map = ProbabilityMap.fromPNG(args.filename)
    logger.trace(f"ProbabilityMap({args.filename})")
    if args.dimmensions is not None:
        width_m,height_m = args.dimmensions
        # We want 1 pixel to match the physical dimmensions of the search radius
        prob_map = prob_map.resampled(int(width_m),int(height_m))
    elif args.shape is not None:
        prob_map = prob_map.resampled(*args.shape)


    logger.info(
        f"Generating {args.num_persons} possible positions within the {prob_map.shape} area")

    sar_gen_output = SarGenOutput()
    points = prob_map.place(args.num_persons)
    sar_gen_output.add_generated_locations(points)

    outfile = sys.stdout
    if args.out_file is not None:
        outfile = open(args.out_file, 'w')

    logger.debug(f"Writing output from sar to {outfile.name}")
    json.dump(sar_gen_output,outfile,cls=GlobalJsonEncoder)

    if args.visualize:
        import matplotlib.pyplot as plt
        import numpy as np
        plt.figure()
        x, y = np.meshgrid(
            np.arange(0, prob_map.shape[0]), np.arange(0, prob_map.shape[1]))
        x, y = x.flatten(), y.flatten()

        points = points.toNumpyArray()

        img = prob_map.toIMG()
        plt.imshow(img, 
                    interpolation=None,
                    cmap='gray'
                    )
        plt.plot(points[:, 0]+0.5, points[:, 1]+0.5, 'rx')
        plt.xlabel("X (m)")
        plt.ylabel("Y (m)")
        plt.show()

def threaded_sim(placed_objs,r,v, out_dic,alg,wps):
    out_dic[alg] = sim.Simulation(wps, placed_objs, r, v, False,alg=alg).run()

def do_sim(args):

    wp_gen_output = WpGenOutput([]).add_generated_wps(Waypoints(args.WPS),-1,WaypointAlgorithmEnum.UNKNOWN) if not isinstance(args.WPS[0],WpGenOutput) else args.WPS[0]
    
    if isinstance(args.object_location[0],SarGenOutput):
        placed_objs = Waypoints(args.object_location[0].data)
    else:
        placed_objs = Waypoints(args.object_location)
    assert(all([isinstance(f, Waypoint) for f in placed_objs]))

    sim_runner_output = SimRunnerOutput()

    total_items = len(wp_gen_output.data)
    c = 0

    if args.threaded:
        logger.info(f"Simulating all algs with threading ({total_items} simulations to run)")
        managers = multiprocessing.Manager()
        out_dict = managers.dict()
        # pool = multiprocessing.Pool(2)
        # wps_iter = [(f,g['wps']) for f,g in wp_gen_output.data.items()]
        # partial = functools.partial(threaded_sim,placed_objs,args.search_radius, args.flight_speed,out_dict)
        # result = pool.map(func=partial, iterable=wps_iter)
        # pool.close()
        # pool.join()

        jobs = []
        for wp_alg,data in wp_gen_output.data.items():
            wps = data['wps']
            p = multiprocessing.Process(target=threaded_sim, args=(placed_objs,args.search_radius, args.flight_speed,out_dict,wp_alg,wps))
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        for key in out_dict:
            sim_runner_output.add_simulation_data(out_dict[key],WaypointAlgorithmEnum[key.split('.')[1]])
    else:
        for wp_alg,data in wp_gen_output.data.items():
            wps = data['wps']
            logger.info(f"Simulating {wp_alg}")
            logger.trace(f"Iteration {(c:=c+1)} out of {total_items} ({100*c/total_items:.2f}%)")
            vehicle_sim_data = sim.Simulation(wps,placed_objs,args.search_radius,args.flight_speed,args.animate).run()
            sim_runner_output.add_simulation_data(vehicle_sim_data,WaypointAlgorithmEnum[wp_alg.split('.')[1]])

    with open(args.out_file,'w') as f:
        json.dump(sim_runner_output,f,cls=GlobalJsonEncoder)

def get_parser() -> argparse.ArgumentParser:
    #   ====================
    #   | ARGUMENT PARSING |
    #   ====================

    parser = argparse.ArgumentParser(
        description=header_main,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog
    )

    # Subparsers for
    # - waypoint generation -> wp
    # - simulation scenario -> sar

    subparsers = parser.add_subparsers(dest="command")
    wp_aliases = ["wp", "w"]
    wp_gen_parser = subparsers.add_parser(
        wp_aliases[0],
        aliases=wp_aliases[1:],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=header_wp,
        help="Waypoint generation utility with 4 algorithms",
        epilog=epilog
    )
    setup_wp_gen_parser(wp_gen_parser)

    sar_aliases = ["sar"]
    sar_parser = subparsers.add_parser(
        sar_aliases[0],
        aliases=sar_aliases[1:],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=header_sar_setup,
        help="SAR simulation case setup utility SMART logic",
        epilog=epilog
    )
    setup_sar_parser(sar_parser)

    sim_aliases = ["sim", "simulate"]
    sim_parser = subparsers.add_parser(
        sim_aliases[0],
        aliases=sim_aliases[1:],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=header_simulate,
        help="Simulation runner",
        epilog=epilog
    )
    setup_sim_parser(sim_parser)

    #   ===============
    #   | GLOBAL ARGS |
    #   ===============

    # Prob map image -> general parser
    prob_map_group = parser.add_argument_group("PROBABILITY MAP")
    prob_map_group.add_argument("-I", "--in_file",
                                dest='filename',
                                metavar='FILENAME',
                                required=False,
                                type=lambda x: is_valid_file(parser, x),
                                default=os.path.join(
                                    os.getenv('OPP4SAR_DIR'), "img", "probability_imgs", "prob_map_4_location_based.png"),
                                help="probability map image file path"
                                )

    prob_map_group.add_argument("-D","--dim",
                                dest="dimmensions",
                                metavar=("X", "Y"),
                                nargs=2,
                                type=float,
                                help="physical dimmensions of the probability map")

    mut_exc_pmap = prob_map_group.add_mutually_exclusive_group()
    mut_exc_pmap.add_argument("--shape",
                                dest='shape',
                                nargs=2,
                                metavar=('X', 'Y'),
                                type=int,
                                help="desired shape of the probability map (don't use for physically accurate calculations)"
                                )
    mut_exc_pmap.add_argument("-S","--search_radius",
                                dest='search_radius',
                                type=float,
                                help="search radius of drone's sensors [ b = h tan(theta) ]"
                                )

    # Logging
    parser.add_argument("-v", dest='log_level',
                        help="Log level", action='count', default=1)

    return parser, wp_aliases, sar_aliases, sim_aliases

if __name__ == "__main__":

    parser, wp_aliases, sar_aliases, sim_aliases = get_parser()

    if os.getenv('TERM_PROGRAM') != 'vscode':
        args = parser.parse_args()
    else:
        args = parser.parse_args("-vvv --dim 300 300 -S 15 sim generated_data/output_wp_baf37f5e.json -o generated_data/output_sar_baf37f5e.json -O generated_data/output_sim_baf37f5e.json".split())

#   ==============================
#   | CHECK ARGS (error on fail) |
#   ==============================

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

    logger.add(sys.stderr, level=log_level)
    logger.info("Welcome to \n"+header_main)
    logger.debug(f'Log level set to {log_level}')
    logger.trace(args)


#   ==============================
#   | CHECK ARGS (warn on fail) |
#   ==============================
    
    if args.search_radius is None:
        logger.warning("Search radius not given. Defaulting to 0.5")
        args.search_radius = 0.5



#   ========
#   | MAIN |
#   ========

    if args.command in wp_aliases:
        do_wp_gen(args)
        logger.info("Exiting waypoint generation")

    elif args.command in sar_aliases:
        do_sar(args)
        logger.info("Exiting SAR setup")

    elif args.command in sim_aliases:
        do_sim(args)
        logger.info("Exiting simulation")
