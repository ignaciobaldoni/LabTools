# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 10:13:08 2021
@author: Ignacio
"""

from newfocus import NewFocus6700
import time
import numpy as np
import matplotlib.pyplot as plt

idLaser = 4106
DeviceKey = '6700 SN62471' ##    DeviceKey = '6700 SN10027'

## First Controls
if 'Already_control' not in locals():
    print("First control is not yet done"); Already_control = 'Done';
    laser = NewFocus6700(id =idLaser, key = DeviceKey)
    laser.connected = True

    old_lbd = laser.lbd
    print('Laser wavelength: {} nm'.format(old_lbd))
    pzt = laser.pzt
    print('Laser piezo: {} %'.format(pzt))    
    output = ["OFF" if laser.output == False else "ON"]
    print('Laser output: {}'.format(output))  
    power = laser.power
    print('Laser power: {} mW'.format(power))   

else:
    print("First control already done")
    ## laser.connected = False

'''    
##    Set wavelength    
set_point_lbd = 1530.14
laser.lbd = set_point_lbd
print('waiting until laser parked at correct lbd')
while laser._is_changing_lbd:
    time.sleep(0.25)
    print('Current wavelength: {}nm'.format(laser.lbd))
    if abs(laser.lbd - set_point_lbd)<0.02:
        print('Set point reached: {}nm'.format(laser.lbd))
        break

##    Set Piezo
set_point_pzt = 40.7
laser.pzt  = set_point_pzt
print('Laser piezo:')
print("\t{}".format(laser.pzt))

####  Set power 
set_point_power = 13.0
laser.power  = set_point_power
print('Laser power:')
time.sleep(3)
print("\t{}".format(laser.power))   

## Turn on - Turn off
#laser.output = True
laser.output = False

### Set track in Off mode
laser.Track_Off = True

'''
begin_scan  = 1536.0
finish_scan = 1537.0
n_points    = 10   
scan_ = np.linspace(begin_scan, finish_scan, n_points)
laser.lbd = begin_scan
time.sleep(3)

step_size = 0.1
scan_ = np.arange(begin_scan,finish_scan+step_size,step_size)
for i in scan_:
    setpoint = np.round(i,2)
    print(setpoint)
    laser.lbd = setpoint
    time.sleep(5)
#    laser.Track_Off = True
