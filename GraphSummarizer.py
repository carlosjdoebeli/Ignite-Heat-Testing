"""
Created on Friday, February 1, 2019
@author: Carlos Doebeli

This is a simple script to open every .txt file in a directory, split into two or more lines of data,
and graphs each file as a different series of data.

This code was created with the assumption that the data was collected using the temp_central_monitor.py script
located in the same directory as this one, and can be used to summarize graphs for a trial.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import os
import re
import sys

# This can be used to manually input the series labels instead of reading them from the file

# SERIES = 4
# SERIES_LABELS = ([
#         "1mL Syringe",
#         "3mL Syringe",
#         "5mL Syringe",
#         "10mL Syringe"
#         ])

files = []
path = sys.path[0]   # Configure this path each time you use the code
file_names = []
labels = []

times = []
temps = []


# Open all .txt files in the directory.
def open_files():
    for file_name in os.listdir(path):
        if file_name.endswith(".txt"):
            file_names.append(file_name)
            file_path = path + "/" + file_name
            f = open(file_path, "r")
            files.append(f)


# Close the files
def close_files():
    for f in files:
        f.close()


# Plot the data after having collected it
def plot():

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for i in range(0, len(files)):

        # Optional: make colour dependent on features of the label for visual grouping.

        if len(temps[i]) >= 3:
            plt.plot(np.array(times[i]), np.array(temps[i]), label=labels[i], linewidth=1.0)

            # optional: prints average and median temperature
            # x = sum(temps[i])/float(len(temps[i]))
            # print(x)
            # print(statistics.median(temps[i]))
            # print("\n")

    plt.legend()
    ax.set_title(name)
    ax.set_xlabel('time (min)')
    ax.set_ylabel('Temp (deg C)')
    file_name = path + "/"
    file_name += name + ".png"
    fig.savefig(file_name)
    plt.show()


open_files()

for i in range(0, len(files)):
    times.append([])
    temps.append([])
    titled = False

    for line in files[i]:
        data = re.split(', |,', line)
        # If the title is included in the first line of the txt file, that title will be labeled on the graph.
        if len(data) == 1 and not titled:
            labels.append(data[0].rstrip("\n\r"))
            titled = True
        elif len(data) >= 2:
            times[i].append(float(data[0]))
            temps[i].append(float(data[1]))

    if not titled:
        labels.append("Series " + str(i + 1))

# print(labels)
name = input("Please enter file name: ")
plot()
close_files()
print("Done!")
