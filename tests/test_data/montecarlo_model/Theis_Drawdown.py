import math as mth;

import scipy.special as sci;
from numpy import *;


dx = 1;
dy = 1;
x_min = 0;
x_max = 1000;
y_min = 0;
y_max = 1000;

# #calib 10 tr 0.0001 st
def read_input():
    file_handle = open("params.txt", "r")
    first_line = file_handle.readlines()[0]
    transmissivity, storativity = first_line.split(',')
    return float(transmissivity), float(storativity)


transmissivity, storativity = read_input()
print("INPUTS")
print("Transmissivity:              ", transmissivity, " m^2/d")
print("Storage:                     ", storativity, " - ")

wells = [{'name': 'first_well', 'Q': 2000, 'X': 500, 'Y': 500, 'rw': 0.1},
         {'name': 'second_well', 'Q': 800, 'X': 700, 'Y': 700, 'rw': 0.1},
         {'name': 'third_well', 'Q': 800, 'X': 400, 'Y': 400, 'rw': 0.1}]

obs_time_steps = []

for steps in range(1, 1500):
    obs_time_steps.append((0.1 * steps))

pumping_schedules = {'first_well': {0: 30, 10: 40, 50: 0},
                     'second_well': {0: 40, 20: 10, 75: 0},
                     'third_well': {0: 50, 30: 30, 80: 0}}

obs_points = [
    {'name': 'obs_1', 'X': 500.1, 'Y': 510},
    {'name': 'obs_2', 'X': 525.1, 'Y': 515}
]


def calc_s_super(_well_name, _S, _T, _time_in, _r):
    drawdown = 0
    Q_m1 = 0
    schedule_sorted = sorted(pumping_schedules[_well_name].keys())
    for time in schedule_sorted:
        if time < _time_in:
            t_delta = _time_in - time
            Q_1 = pumping_schedules[_well_name][time]
            Q = Q_1 - Q_m1
            drawdown = drawdown + calc_s(_S, _T, t_delta, Q, _r)
            Q_m1 = Q_1
    return drawdown


def calc_s(_S, _T, _t, _Q, _r):
    return ((sci.expn(1, ((_r ** 2 * _S) / (4 * _T * _t)))) * _Q) / (4 * mth.pi * _T)


x_range_idx = int((x_max - x_min) / dx + 1);
y_range_idx = int((y_max - y_min) / dy + 1)

for obs in obs_points:
    FILEOBS = open(obs["name"] + ".csv", "w")
    for timei in obs_time_steps:
        drawdown = 0
        for well in wells:
            r = mth.sqrt((well['X'] - obs["X"]) ** 2 + (well['Y'] - obs["Y"]) ** 2)
            drawdown = drawdown + calc_s_super(well['name'], storativity, transmissivity, timei, r)
        FILEOBS.write(str(timei) + "\t" + str(drawdown) + "\n")
    FILEOBS.close()
    #time.sleep(100)