# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 12:22:42 2023

@author: ibaldoni
"""

import numpy as np
import matplotlib.pyplot as plt

def dBm_to_mW(dBm):
    # print(10**(dBm/10))
    return 10**(dBm/10)

def AM_depth(dBm):
    power = dBm_to_mW(dBm)
    
    # 0.89 mW are a proper modulation power
    fraccion = (0.89/power)*100


    AM_depth_power = fraccion*dBm_to_mW(dBm)/100
    AM_depth_porcentage = fraccion
      
    
    return AM_depth_porcentage, AM_depth_power,


dBm = np.arange(15,20,1)
AM_depth_porcentage, AM_depth_power = AM_depth(dBm)
# plt.plot(dBm, dBm_to_mW(dBm))

# fraccion1, fraccion2 =  AM_depth(dBm)
plt.plot(dBm,AM_depth_power)
plt.figure()
plt.plot(dBm,AM_depth_porcentage)

