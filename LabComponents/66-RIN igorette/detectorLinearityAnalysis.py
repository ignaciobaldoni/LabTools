# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 13:01:58 2021

@author: akordts
"""

# python standard classes
import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import time

# standard utilities for saving data
from Utilities import saveDictToHdf5

################################################################################
### fitting function
def func(x, a, b):
    return a*x + b

################################################################################
### load data
################################################################################

figureFilePath = r'\\menloserver\MFS\03-Operations\02-DCP'\
    +r'\03-Entwicklungsprojekte\9556-COSMIC\52-Messergebnisse'\
    +r'\20210921-ARK-linearity test of RIN-detector\results\detectorLinearity.png'

filePath = r'\\menloserver\MFS\03-Operations\02-DCP\03-Entwicklungsprojekte'\
    +r'\9556-COSMIC\52-Messergebnisse'\
    +r'\20210921-ARK-linearity test of RIN-detector\1252\rawData'\
    +r'\1252_linearity test of RIN-detector.h5'
    
dict_MeasurementResult = saveDictToHdf5.load_dict_from_hdf5(filePath)

powerValues_mW = dict_MeasurementResult['MeasurementData']['powerValues_mW']
dcVoltageValue_V = dict_MeasurementResult['MeasurementData']['dcVoltageValue_V']

###########################################################################
# sort values and delete faulty measurement point
arr1inds = powerValues_mW.argsort()
powerValues_mW = powerValues_mW[arr1inds[:]]
dcVoltageValue_V = dcVoltageValue_V[arr1inds[:]]

#remove faulty measuremetn 
errorIndex = 38
powerValues_mW = np.delete(powerValues_mW,errorIndex)
dcVoltageValue_V = np.delete(dcVoltageValue_V,errorIndex)

###########################################################################
# fit linear function 
fitIndex = 32
# fitIndex = 0
popt, pcov = curve_fit(
                    func, 
                    powerValues_mW[fitIndex:], 
                    dcVoltageValue_V[fitIndex:]
                    )

###########################################################################
# plot data and save figure
fig = plt.figure(3)
plt.clf()


ax = plt.gca()
ax.set_xscale('log')
ax.set_yscale('log')
# ax.set_ylim([5e-2,5])

ax.set(xlabel='input power [mW]', ylabel=r'output voltage [V]' )
ax.grid(which='both')

plt.scatter(powerValues_mW, dcVoltageValue_V)

# plot fit
plotIndex = 21
plotIndex = 0
plt.plot(
        powerValues_mW[plotIndex:], 
        func(powerValues_mW[plotIndex:],*popt),
        'r-',
        label='fit: %5.3f V/mW * $P_{in}$ + %5.3fV'% tuple(popt))

plt.legend()
plt.show()

if figureFilePath != None:
    plt.savefig(figureFilePath)