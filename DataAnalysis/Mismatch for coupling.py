# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 18:06:29 2021

@author: ibaldoni
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy import asarray as ar,exp


def gauss(x,a,x0,sigma):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))


x = [-3,-2,-1,0,1,2,3,]
y = [i/7.3 for i in [0.4,1.6,4,7.3,5.8,2.5,0.7]]

x_plot = np.linspace(x[0]-3,x[-1]+3,100)

x = np.array(x)
y = np.array(y)

n = len(x)                          #the number of data
mean = sum(x*y)/n                   #note this correction
sigma = sum(y*(x-mean)**2)/n        #note this correction

popt,pcov = curve_fit(gauss,x,y)

plt.plot(x,y, 'o',label = 'X Axis')
plt.plot(x_plot,gauss(x_plot,*popt),'r',label='fit X')

x = [i-34 for i in [31,32,33,34,35,36]]
y = [i/6.8 for i in[0.6,2.4,5.5,6.8,3.1,0.7]]


x = np.array(x)
y = np.array(y)
n = len(x)                          #the number of data
mean = sum(x*y)/n                   #note this correction
sigma = sum(y*(x-mean)**2)/n        #note this correction

popt,pcov = curve_fit(gauss,x,y)


plt.plot(x,y, 'o',label = 'Z Axis')
plt.plot(x_plot,gauss(x_plot,*popt),label='fit Z')
plt.grid()
plt.legend()
plt.ylabel('Normalized power')
plt.xlabel('Distance [10um]')


