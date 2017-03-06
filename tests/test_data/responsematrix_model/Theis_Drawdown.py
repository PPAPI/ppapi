import math as mth
import scipy.special as sci
from numpy import *

def read_input():
    ret={}
    file_handle = open("rm.inp", "r")
    lines = file_handle.readlines()
    for line in range(1, len(lines)):
        linearr=lines[line].split()
        ret[linearr[0]] = float(linearr[1])
    return ret

ret = read_input()
transmissivity = 10
storativity = 0.0001
print "INPUTS"
print "Transmissivity:              ", transmissivity, " m^2/d"
print "Storage:                     ", storativity, " - "

wells = [{'name': 'first_well' , 'X': 500, 'Y': 500, 'rw': 0.1},
         {'name': 'second_well', 'X': 700, 'Y': 700, 'rw': 0.1},
         {'name': 'third_well' , 'X': 400, 'Y': 400, 'rw': 0.1}]

obs_time_steps = []

active_well = None

for key,val in ret.items():
    if val > 0:
        active_well=key

for steps in range(1, 1500):
    obs_time_steps.append((0.1 * steps))

pumping_schedules = {'first_well':  {0: ret['first_well'] , 200: ret['first_well'] },
                     'second_well': {0: ret['second_well'], 200: ret['second_well']},
                     'third_well':  {0: ret['third_well'] , 200: ret['third_well'] }}

obs_points = [
    {'name': 'obs_1', 'X': 500.1, 'Y': 510},
    {'name': 'obs_2', 'X': 525.1, 'Y': 515}
]

def calc_s_super(_well_name, _S, _T, _time_in, _r):
    drawdown = 0
    Q_m1 = 0
    schedule_sorted = sorted(pumping_schedules[_well_name].iterkeys())
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

FILEOBS = open(active_well + ".csv", "w")
for obs in obs_points:

    for timei in obs_time_steps:
        drawdown = 0
        for well in wells:
            r = mth.sqrt((well['X'] - obs["X"]) ** 2 + (well['Y'] - obs["Y"]) ** 2)
            drawdown = drawdown + calc_s_super(well['name'], storativity, transmissivity, timei, r)
        FILEOBS.write(obs['name'] + "\t" + str(timei) + "\t" + str(drawdown) + "\n")
FILEOBS.close()