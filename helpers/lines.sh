#!/bin/bash
cloc . --exclude-dir=venv,img --quiet --csv 
LINES="$(cloc . --exclude-dir=venv,img --quiet --csv | grep -i SUM)"
echo "LINES: $LINES"
anybadge -l Code -s " lines" -v $(echo $LINES | awk -F',' '{print $5}') | tee img/lines.svg
