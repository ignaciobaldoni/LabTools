# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 10:09:54 2020

@author: ibaldoni
"""

'''
Numerical measurement of coupling ideality
'''

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from scipy.signal import find_peaks, peak_widths

from astropy.modeling import models
import astropy.units as u

artificial = 'on'
linear = True


if artificial == 'on':
    np.random.seed(42)
    y = np.zeros(1)
    x = np.linspace(0, 50, 700)
    for i in range(0,45):
        g1 = models.Lorentz1D(2.5, 1+ 2*i,0.01*i)
        y = y + 1.5*g1(x)
    y = y + np.random.normal(0., 0.12, x.shape)

#y = y*(-1)

avg = np.mean(y)
altura = 2.5*avg
peaks, _ = find_peaks(y,height=altura)
results_half = peak_widths(y, peaks, rel_height = .5)
         
## Resonances positions 
pos_res = x[peaks] 
## Resonances transmissions (deep) - It's turned around so I can find the peaks
t_res = y[peaks]

c = 299789452
for i in results_half[0]:    
    Q = c*i/1542*1e-6
    freq = c/(i*1e-9)
    print('Q %s mill' % np.round(Q,2))        


        


y = y*(-1)

min_peak = np.min(y[peaks]-altura)
variation = (y[peaks]-altura)/min_peak


if linear==True:
    z = np.polyfit(pos_res, variation, 1)
    if z[0]>=0:
        print('Undercoupled regime')
    else: 
        print('Overcoupled regime')
else:
    z = np.polyfit(pos_res, variation, 2)
       
# Dibujitos
fig = plt.figure(1, figsize=(12,8))
ax1 = fig.add_subplot(2, 1, 1)
ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)

ax1.plot(x,y)
ax1.hlines(x[0],x[-1],altura)
ax1.plot(x[peaks], y[peaks], "x")
ax1.set_ylabel('Transmission')

ax2.plot(pos_res,variation,'o-')
ax2.plot(x,z[0]*x+z[1],'r-')
ax2.set_ylabel('Transmission normalized')
ax2.set_xlabel('Wavelength (nm)')


#plt.plot(xx,-xx**2)
#plt.ylim([-5,2])
#plt.xlim([-2,2])