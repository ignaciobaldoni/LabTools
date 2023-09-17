# -*- coding: utf-8 -*-
"""
Created on Fri May 29 16:46:13 2020

@author: Administrator

Temperature sensor 
"""

from time import time, sleep, gmtime, strftime

from py_thorlabs_tsp import ThorlabsTsp01B

def Temp_Sensor(fname):

    def record_sensor_values(sensor: ThorlabsTsp01B, fname: str):
        t = time()
        t1 = sensor.measure_temperature('th0')
        t2 = sensor.measure_temperature('th1')
        h = sensor.measure_humidity()
    
        with open(fname, 'a+') as f:
            f.write('{},{},{},{}\n'.format(t, t1, t2, h))
        
        return t, t1, t2, h
            
            
            
    sensor = ThorlabsTsp01B('M00569202')
    
    with open(fname, 'a+') as f:
        HEADER = 'time,th0,th1,h0\n'
        f.write(HEADER)
            
    t, t1, t2, h = record_sensor_values(sensor, fname)
    
    print('Measurement complete.')
    return t,t1,t2,h
    
#    return 

