#!/bin/bash
LINES="$(tail -n1 helpers/stats.csv | awk -F',' '{print $5}')"
anybadge -l Code -s " lines" -v $LINES | tee img/lines.svg
