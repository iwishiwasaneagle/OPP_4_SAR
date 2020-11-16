from src.json_helpers import GlobalJsonEncoder
from src.waypoint_generation.waypoint_settings import WpGenOutput
from src.data_models.positional.waypoint import Waypoint

from numpy.core.function_base import linspace
import src.simulation.simulation as sim
from src.simulation.parameters import *

import json
import time
import os
import argparse
import sys
import csv
import re

from loguru import logger

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
            if not nmin <= len(values):
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


def is_valid_wps(parser, arg):
    r = r'([0-9]+(?:\.[0-9]+)?),([0-9]+(?:\.[0-9]+)?)'
    res = re.findall(r, arg)
    if len(res) == 0:
        parser.error(f"Incorrect waypoint pattern in \"{arg}\"")
    else:
        x, y = res[0]
        return Waypoint(float(x), float(y))


def setup_wp_gen_parser(parser):
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
    operational.add_argument(
        "-A", "--animate", action="store_true", help="Animate calculations where possible")
    operational.add_argument("-a", "--animate_sim",
                             action="store_true", help="Animate simulation")
    operational.add_argument('--sim', action='store_true', dest="simulate",
                             help="Simulate each path with a point-mass model")
    operational.add_argument(
        "-T", "--threaded", action="store_true", help="Thread calculations where possible")
    operational.add_argument("-O", "--out_file",
                             default="output.json",
                             dest="out_file",
                             metavar='FILENAME',
                             help="Output file name in json format",
                             type=lambda x: is_valid_path_for_file(parser, x)
                             )


def setup_sar_parser(parser):
    parser.add_argument('-n',
                        help="The amount of persons placed on the map",
                        type=int,
                        default=10,
                        dest="num_persons"
                        )
    parser.add_argument("-O", "--out_file",
                        dest="out_file",
                        metavar='FILENAME',
                        help="Output file name in csv format. If empty, outputs to stdout",
                        type=lambda x: is_valid_path_for_file(parser, x)
                        )
    parser.add_argument('-V', '--visualize',
                        dest="visualize",
                        help="Visualize the output before quiting (requires matplotlib)",
                        action="store_true")


def setup_sim_parser(parser):
    parser.add_argument('WPS',
                        help="Input waypoints to the simulation",
                        nargs="+",
                        action=min_length(2),
                        type=lambda x: is_valid_wps(parser, x))
    parser.add_argument("-o", "--object_location",
                        dest='object_location',
                        help="Input search object location. Can be multiple space seperated inputs for multiple simulations.",
                        nargs='+', 
                        action=min_length(1), 
                        type=lambda x: is_valid_wps(parser, x))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-5', '--quintic_polynomial', action='store_true')
    group.add_argument('-F', '--fmincon', action='store_true')


def do_wp_gen(args):

    #   ==================
    #   | PROB MAP SETUP |
    #   ==================

    prob_map = ProbabilityMap.fromPNG(args.filename)
    logger.trace(f"ProbabilityMap({args.filename})")
    if args.shape is not None:
        prob_map.lq_shape = args.shape
  
    #   ======================
    #   | DATA STORAGE SETUP |
    #   ======================

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
            alg, prob_map, animate=args.animate, threaded=args.threaded).generate()

        # Store
        wp_gen_output.add_generated_wps(waypoints,time.time()-t,alg)

    #   ================
    #   | DATA STORAGE |
    #   ================

    with open(args.out_file, 'w') as f:
        data = json.dumps(wp_gen_output,cls=GlobalJsonEncoder)
        json.dump(data, f)


def do_sar(args):
    #   ==================
    #   | PROB MAP SETUP |
    #   ==================

    prob_map = ProbabilityMap.fromPNG(args.filename)
    logger.trace(f"ProbabilityMap({args.filename})")
    if args.shape is not None:
        prob_map.lq_shape = args.shape

    logger.info(
        f"Generating {args.num_persons} possible positions within the {prob_map.shape} area")
    points = prob_map.place(args.num_persons, prob_map_hq=False)

    outfile = sys.stdout
    if args.out_file is not None:
        outfile = open(args.out_file, 'w')

    logger.debug(f"Writing output from sar to {outfile.name}")
    csvwriter = csv.writer(outfile)
    csvwriter.writerows(points)

    if args.visualize:
        import matplotlib.pyplot as plt
        import numpy as np
        plt.figure()
        x, y = np.meshgrid(
            np.arange(0, prob_map.shape[0]), np.arange(0, prob_map.shape[1]))
        x, y = x.flatten(), y.flatten()

        points = points.toNumpyArray()
        img_placed = np.zeros(prob_map.shape)
        unique, counts = np.unique(
            [f"{f[0]},{f[1]}" for f in points], return_counts=True)
        unique = [(int(f), int(g)) for f, g in [h.split(',') for h in unique]]

        for xyi, c in zip(unique, counts):
            x, y = xyi
            img_placed[x, y] = c

        plt.imshow(prob_map.toIMG(prob_map_hq=False), interpolation=None, origin='bottom', extent=[
                   0, prob_map.lq_shape[0], 0, prob_map.lq_shape[1]], cmap='gray')
        plt.plot(points[:, 0]+0.5, points[:, 1]+0.5, 'rx')
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.show()


def do_sim(args):
    for obj in args.object_location:
        vehicle_sim_data = sim.simulation(args.WPS,obj).run()
        print(vehicle_sim_data)

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
                                    "img", "probability_imgs", "prob_map_4_location_based.png"),
                                help="probability map image file path"
                                )
    prob_map_group.add_argument("--shape",
                                dest='shape',
                                nargs=2,
                                metavar=('X', 'Y'),
                                type=int,
                                help="desired shape of the probability map"
                                )

    # Logging
    parser.add_argument("-v", dest='log_level',
                        help="Log level", action='count', default=0)

    return parser, wp_aliases, sar_aliases, sim_aliases


if __name__ == "__main__":

    parser, wp_aliases, sar_aliases, sim_aliases = get_parser()

    if os.getenv('TERM_PROGRAM') != 'vscode':
        args = parser.parse_args()
    else:
        # '-I img/probability_imgs/prob_map_4_location_based.png -vvv sar -n 200 -V'.split())
        args = parser.parse_args("-vvv --shape 5 5 wp -S".split())


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
