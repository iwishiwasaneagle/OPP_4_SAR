#!/bin/bash

LINES="$(cloc $PWD --exclude-dir=venv,img --quiet --csv | grep -i SUM)"
echo "$(date),$(echo $LINES | awk -F',' '{print $1","$3","$4","$5}')" >> helper/lines.csv
anybadge -l Code -s " lines" -v $(echo $LINES | awk -F',' '{print $5}')  > img/lines.svg
