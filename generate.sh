#!/bin/bash

MENG_BASE_DIR=$HOME/Documents/meng_project
CODE_DIR=$MENG_BASE_DIR/code
OUT_DIR=$CODE_DIR/generated_data
PROB_MAP=$CODE_DIR/img/probability_imgs/prob_map_3_multimodal.png

X_SHAPE=300
Y_SHAPE=300
RAD=15
N_SAR=10000
N_ITER=${1-3}
source $CODE_DIR/venv/bin/activate
echo "`date` | $N_ITER iterations"
for i in $(seq 1 $N_ITER); do
    KEY="$(date | md5sum | cut -c-8)"
    wp_out_file="$OUT_DIR/output_wp_$KEY.json"
    sar_out_file="$OUT_DIR/output_sar_$KEY.json"
    sim_out_file="$OUT_DIR/output_sim_$KEY.json"

    echo "`date` | Iteration ${i}/$N_ITER"
    
    echo "`date` | Generating WPs" 
    time python3 $CODE_DIR/main.py -vvv -I $PROB_MAP --dim $X_SHAPE $Y_SHAPE -S $RAD wp -LSMP --solver fmincon ga particleswarm -O $wp_out_file -T 1>>$OUT_DIR/out.log 2>>$OUT_DIR/out.log
    echo "`date` | Generating $N_SAR SAR points"
    time python3 $CODE_DIR/main.py -vvv -I $PROB_MAP --dim $X_SHAPE $Y_SHAPE -S $RAD sar -n $N_SAR -O $sar_out_file 2>>$OUT_DIR/out.log
    echo "`date` | Simulation SAR scenarios"
    time python3 $CODE_DIR/main.py -vvv -I $PROB_MAP --dim $X_SHAPE $Y_SHAPE -S $RAD sim $wp_out_file -o $sar_out_file -O $sim_out_file -T 2>>$OUT_DIR/out.log
done
