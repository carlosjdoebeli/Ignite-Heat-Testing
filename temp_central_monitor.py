"""
Created on Fri Nov  2 12:25:36 2018

@author: Justin Myles

Edited by Carlos Doebeli for Ignite

Switch must initially be off before the test begins, or the code will not work.
"""


import numpy as np
from numpy import diff
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import re
import time
import serial
import serial.tools.list_ports
import os
import sys

# Which port you connect to will depend on your computer's connections
ports = list(serial.tools.list_ports.grep("USB Serial Device"))
SENSORS = 4                         # Choose your number of sensors here
temps = []
times = []
sensor_labels = []

if len(ports) == 1:
    print("USB Serial Device found")
else:
    print("USB Serial Device not found or too many of them.")
    print("Check your connections!")
    time.sleep(1)
    sys.exit()

serial_port = ports[0]
print(serial_port)
ser = serial.Serial(serial_port[0], 9600)

file_path = sys.path[0]

def initTemps(num):
    for i in range(0, num):
        t = []
        time = []
        temps.append(t)
        times.append(time)

def readTrial():
    start = time.perf_counter()
    line =  str(ser.readline())
    while not "FINISH" in line:
        print(line)
        nums = re.findall('-?\d+\.?\d*', line)

        if "DATA" in line:
            temps[int(nums[2])].append(float(nums[1]))
            times[int(nums[2])].append((float(nums[0]) - start_time)/60000.00)
            start = time.perf_counter()
        elif time.perf_counter() - start > 5:
            break
        line =  str(ser.readline())
    print("DONE")

def createFiles():
    for i in range(0, SENSORS):
        if len(temps[i]) >= 3:
            t = time.localtime()
            timestamp = time.strftime('%b-%d-%Y_%H.%M', t)
            file_name = file_path + "/Data/" #Configure your path for data
            file_name += test_desc + "/"

            if not os.path.isdir(file_name):
                os.makedirs(file_name)

            file_name += sensor_labels[i] + "_" + timestamp + ".txt"
            f = open(file_name,"w+")
            f.write(sensor_labels[i] + "\n")
            for j in range(0,len(temps[i])):
                f.write(str(times[i][j]) + ", "
                        + str(temps[i][j]) + "\n")
            f.close()

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)

def plot():
    t = time.localtime()
    timestamp = time.strftime('%b-%d-%Y_%H.%M', t)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for i in range(0, SENSORS):
        if len(temps[i]) >= 3:
            plt.plot(np.array(times[i]), np.array(temps[i]), label=sensor_labels[i])
    plt.legend()
    ax.set_xlabel('time (min)')
    ax.set_ylabel('Temp (deg C)')
    file_name = file_path + "/Graphs/"    #Configure your path for graphs

    if not os.path.isdir(file_name):
        os.makedirs(file_name)

    file_name += test_desc + "_"
    file_name += timestamp + ".png"
    fig.savefig(file_name)
    plt.show()


def derivative(arr1, arr2):
    return diff(arr1) / diff(arr2)

def process():
    initTemps(SENSORS)
    readTrial()
    plot()
    createFiles()


test_desc = input("Please enter test description: ")

for i in range(0, SENSORS):
    temp_label = input("Enter label for sensor " + str(i) + ": ")
    sensor_labels.append(temp_label)

print("Turn on the switch to take data.")

trials = 0
start = time.perf_counter()
initTemps(SENSORS)
while True:
    line = str(ser.readline())
    if "START" in line:
        print("STARTING")
        print(line)
        nums = re.findall('-?\d+\.?\d*', line)
        start_time = float(nums[0])
        process()
        break
    elif "FINISH" in line:
        print(line)
        print("DONE")
        break
    else:
        print(line)

start = time.perf_counter()
while True and time.perf_counter() - start < 3:
    continue
ser.close()
