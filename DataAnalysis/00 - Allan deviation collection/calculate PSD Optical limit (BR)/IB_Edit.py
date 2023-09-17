# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 14:16:29 2023

@author: ibaldoni
"""

from __future__ import division
import numpy as np
import allantools
import pandas as pd
import scipy.constants as c
import matplotlib.pyplot as plt

#set sample time in seconds
t = 0.1
#set wavelength in meter #1542.14 1064 698.45
Wavelength = 1542.12E-9
#choose Data: All Data is starting with 0
anfang = 12*3600*10+19.76*3600*10#19.76*3600*10
ende = anfang+1*3600*10#51.62*3600*10#

#set file name and column number starting from 0
columnno = 7
filename = '230401_1_Frequ.txt'
#use accuracy intervals as in test procedure (0) or all (1)
intervals = 0 #1

# 211105_1_Frequ


#####################################################

# sample rate in Hz of the input data
r = np.divide(1, t)
#optical frequency
f = np.divide(c.c, Wavelength)

#load Data
a1 = np.genfromtxt('230331_1_Frequ.txt', dtype=float, comments='#', delimiter=None, converters=None, usecols=(columnno), unpack=False,invalid_raise=False)
a2 = np.genfromtxt('230401_1_Frequ.txt', dtype=float, comments='#', delimiter=None, converters=None, usecols=(columnno), unpack=False,invalid_raise=False)
a3 = np.genfromtxt('230402_1_Frequ.txt', dtype=float, comments='#', delimiter=None, converters=None, usecols=(columnno), unpack=False,invalid_raise=False)
an = np.append(a1,a2)
ann = np.append(an,a3)
c = pd.DataFrame(ann)



# create timestamps row
l = np.arange(len(c))
c.insert(loc=0, column='Time', value=np.divide(l, r))

#convert back to array
Dataf = c.to_numpy()

#select Data
Data = Dataf[int(anfang):int(ende), :]

ROW = Data.T[1]

#create fractional frequency stability plot
ROWf = ROW/f 

# Compute the overlapping ADEV
(t2, ad, ade, adn) = allantools.mdev(ROWf, rate=r, data_type="freq", taus="decade")

fig5 = plt.figure(5)
plt.errorbar(t2,ad, linestyle='-', marker='s', label='MADEV',color='g')
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Tau [s]')
plt.ylabel('MADEV [fractional]')
plt.grid()
plt.legend()
plt.grid(visible=True, which='both')
plt.tight_layout()