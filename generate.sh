#!/bin/bash
MENG_BASE_DIR=$HOME/Documents/meng_project/
OUT_DIR=$MENG_BASE_DIR/gend_data/
CODE_DIR=$MENG_BASE_DIR/code/
PROB_MAP=$CODE_DIR/img/probability_imgs/prob_map_4_location_based.png

X_SHAPE=15
Y_SHAPE=15
N_SAR=100000
source $CODE_DIR/venv/bin/activate

for i in {1..10}; do
    wp_out_file="$OUT_DIR/output_wp_$i.json"
    sar_out_file="$OUT_DIR/output_sar_$i.json"
    sim_out_file="$OUT_DIR/output_sim_$i.json"

    echo "`date` | Iteration ${i}/10"
    
    echo "`date` | Generating WPs"
    time python3 $CODE_DIR/main.py -I $PROB_MAP --shape $X_SHAPE $Y_SHAPE wp -LSMP --solver fmincon ga particleswarm -O $wp_out_file 2>>$OUT_DIR/out.log
    echo "`date` | Generating $N_SAR SAR points"
    time python3 $CODE_DIR/main.py -I $PROB_MAP --shape $X_SHAPE $Y_SHAPE sar -n $N_SAR -O $sar_out_file 2>>$OUT_DIR/out.log
    echo "`date` | Simulation SAR scenarios"
    time python3 $CODE_DIR/main.py sim $wp_out_file -o $sar_out_file -O $sim_out_file 2>>$OUT_DIR/out.log
done
