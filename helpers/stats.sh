#!/bin/bash
# Copy/symlink this into .git/hooks as either "pre-commit" or "pre-push"
echo "🪝 Pre-push hook: auto update stats.csv"

CWD=$(git rev-parse --show-toplevel)
echo "$(date),$(cloc $PWD --exclude-dir=venv,img --csv | grep SUM | awk -F',' '{print $1","$3","$4","$5}')" >> $CWD/helpers/stats.csv

git commit $CWD/helpers/stats.csv -m "Auto: updated stats.csv"
echo "✅ Pre-push hook completed"
