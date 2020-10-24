import matplotlib.pyplot as plt
import csv
from datetime import datetime
import sys

FILE="helper/stats.csv"

time = []
files = []
lines = []

with open(FILE,'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        dt_obj = datetime.strptime(row['date'],"%a %d %b %H:%M:%S BST %Y")
        time.append(dt_obj)
        files.append(int(row['files']))
        lines.append(int(row['code']))

fig,ax = plt.subplots(2,1, sharex="all")

fig.suptitle("MEng metrics over time")
plt.xlabel("Time")

ax[0].plot(time,lines)
ax[0].set_ylabel("Lines")

ax[1].plot(time,files)
ax[1].set_ylabel("Files")

fig.autofmt_xdate()

if "save" in sys.argv:
    plt.savefig("helper/stats.png")

if "show" in sys.argv:
    plt.show()
