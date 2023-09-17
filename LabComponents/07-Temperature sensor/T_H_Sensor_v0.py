# -*- coding: utf-8 -*-
"""
Created on Thu May 14 16:57:12 2020

@author: Administrator

long_term_monitor.py

This script repeatedly records readouts from the Thorlabs TSP01B sensor.
Requires a connected TSP01 Rev.B sensor.

Author: Dima Pustakhod
Copyright: TU/e
"""

from time import time, sleep, gmtime, strftime

from py_thorlabs_tsp import ThorlabsTsp01B

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Settings
# --------

DURATION_H = 0.5#input('Hours')
DURATION_S = 36.00 * DURATION_H

INTERVAL_S = 0.1*DURATION_S
HEADER = 'time,th0,th1,h0\n'
fname = 'Temperature_Metztzazusurement13.csv' #_output_data/{} - data.csv'.format(strftime('%Y%m%dT%H%M%S', gmtime()))



def record_sensor_values(sensor: ThorlabsTsp01B, fname: str):
    t = time()
    t1 = sensor.measure_temperature('th0')
    t2 = sensor.measure_temperature('th1')
#    t3 = sensor.measure_temperature('th1')
    h = sensor.measure_humidity()

    with open(fname, 'a+') as f:
        f.write('{},{},{},{}\n'.format(t, t1, t2, h))
        
def lectura_inmediata(fname):
    
    df = pd.read_csv(fname, delimiter=',')
    
    df['Time'] = pd.to_datetime(df['time'], unit='s')
    
    df.drop(['time'], inplace=True, axis='columns')
    
    df.set_index('Time', inplace=True)  
    
    
    
    fig = plt.figure(10)
    ax = fig.add_subplot(111)  
    color_dict = {'th0': 'black', 'th1': 'green','h0': 'blue'}


    ax = df[['th0', 'th1', 'h0']].plot(
            color=[color_dict.get(x) for x in df.columns],
            secondary_y=['h0'],ax=ax)  
    
    ax.set_ylabel('Temperature (°C)')
    ax.right_ax.set_ylabel('Humidity (%)')


sensor = ThorlabsTsp01B('M00569202')

with open(fname, 'a+') as f:
        f.write(HEADER)

print('\nDO NOT TERMINATE THE PROGRAM! THE MEASUREMENT IS ONGOING!\n')

t = time()
t_end = t + DURATION_S
t_next = t + INTERVAL_S

n_sampling = 0

while t < t_end:
    record_sensor_values(sensor, fname)
    
    
    n_sampling = n_sampling + 1 
    print(n_sampling)
        
    lectura_inmediata(fname)
    plt.pause(0.5)    
    
    sleep(t_next - time())    

    t = time()
    t_next = t + INTERVAL_S
    
    if t<t_end:
        plt.clf() 
        
print('Measurement complete.')

sensor.release()

## Reading the results



# Settings
# --------
#
#
#def lectura_inmediata(fname):
#    
#    df = pd.read_csv(fname, delimiter=',')
#    
#    df['Time'] = pd.to_datetime(df['time'], unit='s')
#    
#    df.drop(['time'], inplace=True, axis='columns')
#    
#    df.set_index('Time', inplace=True)  
#
#    
#    
#    
#    ax = df[['th0', 'th1', 'th2', 'h0']].plot(secondary_y=['h0'])
#    ax.set_ylabel('Temperature (°C)')
#    ax.right_ax.set_ylabel('Humidity (%)')
#    
#fname = 'Temperature_Measurement.csv'
#lectura_inmediata(fname)
#fname = 'Temperature_Measurement_3.csv'
#lectura_inmediata(fname)