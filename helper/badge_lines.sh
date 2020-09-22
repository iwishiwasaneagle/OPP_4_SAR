#!/bin/bash

anybadge -l Code -s " lines" -v "$(cloc ./ --exclude-dir=venv,img --quiet --csv | grep -i sum | awk -F',' '{print $5}')" > img/lines.svg
