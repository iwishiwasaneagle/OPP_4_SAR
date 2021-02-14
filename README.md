<p align="center">
  <img src="./img/logo.png" alt="logo" width="360">
</p>

# Optimum Path Planning for Search and Rescue

![Tests](https://github.com/iwishiwasaneagle/OPP_4_SAR/workflows/Tests/badge.svg)

*View the full thesis [here](https://iwishiwasaneagle.github.io/OPP_4_SAR_thesis/)!*

Search and Rescue (SAR) of vulnerable missing persons is unfortunately a common task for the Police and other emergency services. Organisations like the Centre for Search and Rescue (CSR)[1] carry out research into the typical behaviour patterns for classes of missing person (young child, elderly person with dementia etc.) and provide specialist training to Police forces in all areas related to SAR. The category of missing person is mapped to a behavioural or psychological profile that is used to refine the search, indicating buildings or landmarks that the person is most likely to be. One of the key outcomes from all studies into the effectiveness of missing person search strategies is that time is crucial - the quicker the person is found, the more likely a favourable outcome.

With the rapid development and expansion of the drone sector over the last decade, Unmanned Aerial Vehicles (UAVs) have become cheaper and more accessible than ever before. Officers from the Air Support Unit of Police Scotland are one of the first emergency services in the UK to take advantage of this technology by using infrared and visible light cameras on commercially available quadrotors as an aid to the current single manned helicopter. Current plans are to use single UAV platforms to search a pre-defined area, to detect possible targets and direct the search team, although swarms of vehicles are also being considered for future use. However, their flight plans are made solely by instinct and training and this provides a unique opportunity to use a priori information to create optimised coverage paths.

However, if little thought is given to the path planning algorithm it may well be suboptimal intime sensitive scenarios. Therefore, it is imperative to find the optimum path for the scenario tomobilise ground units as fast as possible. Research has been conducted in this field, with themost promising using the Bayesian search theory which is based on the Bayesian statisticswhere probability expresses adegree of beliefin an event. This search theory has been usedfor SAR efforts previously, such as in the MH370 incident of 2011[2]. For the use in drones, thistheory can be used to construct coverage paths using various greedy path planning algorithmsand numerical optimisation methods.

This repository implements algorithms from [3], [4] and [5] as well as implementing a custom area coverage algorithm based on probability accumulation based optimisation. 

## Installation

```
make install
```

## Documentation

Either

 - Build by running `doxygen` from within the repo dir

Or
 
 - Launch the `index.html` from within the `docs` folder (`firefox docs/index.html`)

## Usage 

### Global settings

```
usage: main.py [-h] [-I FILENAME] [-D X Y] [--shape X Y | -S SEARCH_RADIUS]
               [-v]
               {wp,w,sar,sim,simulate} ...

===============================================================
      ____  _____  _____    _  _      _____         _____  
     / __ \|  __ \|  __ \  | || |    / ____|  /\   |  __ \ 
    | |  | | |__) | |__) | | || |_  | (___   /  \  | |__) |
    | |  | |  ___/|  ___/  |__   _|  \___ \ / /\ \ |  _  / 
    | |__| | |    | |         | |    ____) / ____ \| | \ \ 
     \____/|_|    |_|         |_|   |_____/_/    \_\_|  \_                                                        
                                                    
    Optimal Path Planning for Search and Rescue
===============================================================

positional arguments:
  {wp,w,sar,sim,simulate}
    wp (w)              Waypoint generation utility with 4 algorithms
    sar                 SAR simulation case setup utility SMART logic
    sim (simulate)      Simulation runner

optional arguments:
  -h, --help            show this help message and exit
  -v                    Log level

PROBABILITY MAP:
  -I FILENAME, --in_file FILENAME
                        probability map image file path
  -D X Y, --dim X Y     physical dimmensions of the probability map
  --shape X Y           desired shape of the probability map (don't use for
                        physically accurate calculations)
  -S SEARCH_RADIUS, --search_radius SEARCH_RADIUS
                        search radius of drone's sensors [ b = h tan(theta) ]
```

### Waypoint Generation utility

```
usage: main.py wp [-h] [-L] [-M] [-S] [-P]
                  [--solver {fmincon,ga,particleswarm} [{fmincon,ga,particleswarm} ...]]
                  [--home HOME HOME] [-A] [-T] [-O FILENAME]

===================================================
    __          _______     _____ ______ _   _ 
    \ \        / /  __ \   / ____|  ____| \ | |
     \ \  /\  / /| |__) | | |  __| |__  |  \| |
      \ \/  \/ / |  ___/  | | |_ |  __| | . ` |
       \  /\  /  | |      | |__| | |____| |\  |
        \/  \/   |_|       \_____|______|_| \_|

===================================================

optional arguments:
  -h, --help            show this help message and exit

LHC_GW_CONV:
  -L                    calculate the LHC_GW_CONV path

MODIFIED_LAWNMOWER:
  -M                    calculate the Modified Lawnmower path

PARALLEL SWATHS:
  -S                    calculate the Parallel Swaths path

PABO:
  -P                    calculate the PABO path
  --solver {fmincon,ga,particleswarm} [{fmincon,ga,particleswarm} ...]
                        select the solver for PABO

OPERATIONAL:
  --home HOME HOME      Home for the paths. Defaults to no home.
  -A, --animate         Animate calculations where possible
  -T, --threaded        Thread calculations where possible
  -O FILENAME, --out_file FILENAME
                        Output file name in json format
```

### SAR Simulation utility

```    
usage: main.py sim [-h] [-o OBJECT_LOCATION [OBJECT_LOCATION ...]] [-5 | -F]
                   [--flight_speed FLIGHT_SPEED] [-O FILENAME] [-T | -A]
                   WPS [WPS ...]

================================================================
      _____ _____ __  __ _    _ _            _______ ______ 
     / ____|_   _|  \/  | |  | | |        /\|__   __|  ____|
    | (___   | | | \  / | |  | | |       /  \  | |  | |__   
     \___ \  | | | |\/| | |  | | |      / /\ \ | |  |  __|  
     ____) |_| |_| |  | | |__| | |____ / ____ \| |  | |____ 
    |_____/|_____|_|  |_|\____/|______/_/    \_\_|  |______|

================================================================

positional arguments:
  WPS                   Input waypoints to the simulation

optional arguments:
  -h, --help            show this help message and exit
  -o OBJECT_LOCATION [OBJECT_LOCATION ...], --object_location OBJECT_LOCATION [OBJECT_LOCATION ...]
                        Input search object location. Can be multiple space
                        seperated inputs for multiple simulations or output
                        file from `wp`.
  -5, --quintic_polynomial
  -F, --fmincon
  --flight_speed FLIGHT_SPEED
                        Mean flight speed of the point mass (m/s)

OPERATIONAL:
  -O FILENAME, --out_file FILENAME
                        Output file name in json format
  -T, --threaded        Thread calculations where possible
  -A, --animate         Animate calculations where possible
```
### SAR Setup Utility
```    
usage: main.py sar [-h] [-n NUM_PERSONS] [-O FILENAME] [-V]

=====================================================================
      _____         _____     _____ ______ _______ _    _ _____  
     / ____|  /\   |  __ \   / ____|  ____|__   __| |  | |  __ \ 
    | (___   /  \  | |__) | | (___ | |__     | |  | |  | | |__) |
     \___ \ / /\ \ |  _  /   \___ \|  __|    | |  | |  | |  ___/ 
     ____) / ____ \| | \ \   ____) | |____   | |  | |__| | |     
    |_____/_/    \_\_|  \_\ |_____/|______|  |_|   \____/|_|     
                                                              
=====================================================================

optional arguments:
  -h, --help            show this help message and exit
  -n NUM_PERSONS        The amount of persons placed on the map
  -O FILENAME, --out_file FILENAME
                        Output file name in json format
  -V, --visualize       Visualize the output before quiting (requires
                        matplotlib)
``` 

### Example

```bash
BASE_DIR=$HOME/Documents/opp_4_sar
CODE_DIR=$MENG_BASE_DIR/code
OUT_DIR=$CODE_DIR/generated_data/prob_map_9
PROB_MAP=$CODE_DIR/img/probability_imgs/prob_map_9.png

X_SHAPE=700
Y_SHAPE=700
RAD=15
N_SAR=100000

wp_out_file="$OUT_DIR/output_wp.json"
sar_out_file="$OUT_DIR/output_sar.json"
sim_out_file="$OUT_DIR/output_sim.json"

time python3 $CODE_DIR/main.py -vvv -I $PROB_MAP --dim $X_SHAPE $Y_SHAPE -S $RAD wp -LSMP --solver fmincon ga particleswarm -O $wp_out_file -T
time python3 $CODE_DIR/main.py -vvv -I $PROB_MAP --dim $X_SHAPE $Y_SHAPE -S $RAD sar -n $N_SAR -O $sar_out_file
time python3 $CODE_DIR/main.py -vvv -I $PROB_MAP --dim $X_SHAPE $Y_SHAPE -S $RAD sim $wp_out_file -o $sar_out_file -O $sim_out_file -T
```

### References
[1] D. Perkins, P. Roberts, and G. Feeney, “The U.K. Missing Person Behaviour Study,” 2011. [Online]. Available: http://www.searchresearch.org.uk/downloads/ukmpbs/13556434714e40eee77e749.pdf.

[2] Angus Whitley, “How an Eighteenth-Century Statistician Is Helping to Find MH370,” Bloomberg, 2015.

[3] J. Ousingsawat and M. G. Earl, “Modified lawn-mower search pattern for areas comprised of weighted regions,” Proc. Am. Control Conf., pp. 918–923, 2007, doi: 10.1109/ACC.2007.4282850.

[4] L. Lin and M. A. Goodrich, “UAV intelligent path planning for wilderness search and rescue,” 2009 IEEE/RSJ Int. Conf. Intell. Robot. Syst. IROS 2009, vol. 0, no. 1, pp. 709–714, 2009, doi: 10.1109/IROS.2009.5354455.

[5] E. M. Arkin, S. P. Fekete, and J. S. B. Mitchell, “Approximation algorithms for lawn mowing and milling,” Comput. Geom. Theory Appl., vol. 17, no. 1–2, pp. 25–50, 2000, doi: 10.1016/S0925-7721(00)00015-8.

