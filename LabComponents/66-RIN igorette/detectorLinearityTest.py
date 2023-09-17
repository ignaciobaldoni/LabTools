# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 09:40:59 2021

@author: akordts
"""

# python standard classes
import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time

# standard utilities for saving data
from Utilities import dataStructureConvention as nameConv
from Utilities import saveDictToHdf5

# tool libs
from Powermeter_PM100A import Thorlabs_PM100A as tool_PM
from OSCI_Oscilloscope.Osci_Keysight_DSOX1204A import Oszi_Keysight_DSOX1204A as tool_Osci


##############################################################################
# data file locations
##############################################################################

fs = '\\'
rootDataLocationPath = fs+fs+'Menloserver'+fs \
            +'mfs'+fs \
            +'03-Operations'+fs \
            +'02-DCP'+fs \
            +'03-Entwicklungsprojekte'+fs \
            +'9556-COSMIC'+fs \
            +'52-Messergebnisse'
operatorInitials = 'ARK'
measurementPurposeShort = 'linearity test of RIN-detector'

singleMeasureName = 'linearity test of RIN-detector'

# (folderLocation , dataFilePath)
fileTimeStamp = time.strftime("%H%M")
(folderLocation , dataFilePath) = nameConv.saveFileName(
        operatorInitials,
        singleMeasureName,
        measurementPurposeShort,
        rootDataLocationPath,
        subFolder = fileTimeStamp,
        fileSeperator = fs) 


(folderLocation , figureFilePath) = nameConv.saveFileName(
        operatorInitials,
        singleMeasureName,
        measurementPurposeShort,
        rootDataLocationPath,
        subFolder = fileTimeStamp,
        fileSeperator = fs,
        fileType = '.png') 

################################################################################
### tool initiliazation
################################################################################

# power meter
resourceStr = 'USB0::0x1313::0x8079::P1001184::INSTR'
powerMeter = tool_PM(resourceStr)

# osci
resourceStr = r'USB0::0x2A8D::0x1766::MY60104389::INSTR'
osci = tool_Osci(resourceStr)
################################################################################

powerValues_mW = []
dcVoltageValue_V = []
dict_MeasurementResult = {}

while True:
    
    input1 = input('change power, scale scope, press enter')
    # lineraity test of detector
    
    # make adjustement
    
    # measure power 
    
    power = powerMeter.readPower()
    powerValues_mW.append(power)
    
    # measure dc voltage 
    avgDcValue = osci.measureAverageValue(4)
    print(avgDcValue)
    dcVoltageValue_V.append(avgDcValue)
    
    ###########################################################################
    # save data
    dict_MeasurementResult['MeasurementData/powerValues_mW'] \
        = np.asarray(powerValues_mW)
    dict_MeasurementResult['MeasurementData/dcVoltageValue_V'] \
            = np.asarray(dcVoltageValue_V)
        
    # continously save Data
    saveDictToHdf5.save_dict_to_hdf5(
        dict_MeasurementResult, 
        dataFilePath)
    
    
    ###########################################################################
    # plot data and save figure
    fig = plt.figure(2)
    plt.clf()
    
    plt.scatter(powerValues_mW, dcVoltageValue_V)
    ax = plt.gca()
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    ax.set(xlabel='input power [mW]', ylabel=r'output voltage [V]' )
    ax.grid(which='both')
    
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    if figureFilePath != None:
        plt.savefig(figureFilePath)
    

 