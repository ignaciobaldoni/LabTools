# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 14:23:42 2021

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

# helper modules and functions for RIN measurement
from getScalarRangeData import getScalarRangeData
from initESAforRINmeasurement import initESAforRINmeasurement
from plotRinFigures import plotRinFigures

# ToDo
    # load rin state 
    # continous saving of data
    # plotting
    
    # control data and units
    # cleaning and seperation of 
    # record dc voltage at the same time 


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
measurementPurposeShort = 'corssCor - limits'

# singleMeasureName = 'CrosCor configuration - EDFA_3A5 - lock on - input -B - PI300kHz - 6G8'
singleMeasureName = 'crossCor configuration - averaging test'

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
##############################################################################
##############################################################################


##############################################################################
# define measurement settings
##############################################################################

dict_MeasurementResult = {}

dc_voltage_V = 4.27
        
startFreq = 1e6
stopFreq = 1e7
avgPts = 1000

dict_MeasurementResult['MeasurementData/dc_voltage_V'] \
        = np.asarray(dc_voltage_V)
        
dict_MeasurementResult['SettingsData/startFreq_Hz'] \
        = startFreq
        
dict_MeasurementResult['SettingsData/stopFreq_Hz'] \
        = stopFreq
        
dict_MeasurementResult['SettingsData/avgPerTrace'] \
        = avgPts
        
##############################################################################
##############################################################################


##############################################################################
# run measurememt
##############################################################################
rm = visa.ResourceManager()
resource = 'GPIB1::9::INSTR'
visaobj = rm.open_resource(resource)
visaobj.timeout = None

initESAforRINmeasurement(visaobj)

freqValues = []
powValues = []
psdVals_VrmsPrtHz = []
rbwValues = []


powerTraces = []
avgVals = []
stdVals = []
durationValues = []


# create figure
plt.ion()
fig, axs = plt.subplots(2)
axs[0].set(xlabel='time [s]', 
           ylabel='avg RIN level [dBc/Hz]' )
axs[0].grid()
# axs[0].set_yscale('log')
line1, = axs[0].plot(durationValues, avgVals,'o')

axs[1].set(xlabel='time [s]', 
           ylabel='std RIN level [dBc/Hz]' )
axs[1].grid()
# axs[1].set_yscale('log')
line2, = axs[1].plot(durationValues, stdVals,'o')

startTime = time.time()

while True:
    sweepPts = None
    
    # measure single trace
    freqs,pows,rbwValue = getScalarRangeData(
                            visaobj,
                            sweepPts,
                            startFreq,
                            stopFreq,
                            avgPts
                        )
    
    psdVs_Vrms2PHz = np.array(pows)/rbwValue
    psdVs_VrmsPrtHz = np.sqrt(psdVs_Vrms2PHz)
    psdVals_VrmsPrtHz = psdVals_VrmsPrtHz + psdVs_VrmsPrtHz.tolist()
    
    powerTraces.append(psdVs_Vrms2PHz)    
    
    # avgTrace = np.mean(powerTraces,axis=0)
    avgVal = np.mean(powerTraces)
    avgValRIN = 20*np.log10(np.sqrt(avgVal)/dc_voltage_V)
    avgVals = avgVals + [avgValRIN]
    
    stdVal = np.std(powerTraces)
    stdValRIN = 20*np.log10(np.sqrt(stdVal)/dc_voltage_V)
    stdVals = stdVals + [stdValRIN]
    
    powValues = powValues + pows
    rbwValues = rbwValues + [rbwValue]
    
    currentTime = time.time()
    duration = currentTime - startTime
    duration = duration/3600
    durationValues = durationValues + [duration]   
    
    dict_MeasurementResult['MeasurementData/rbwValues'] \
            = np.asarray(rbwValues)
    dict_MeasurementResult['MeasurementData/freqValues_Hz'] \
            = np.asarray(freqs)
    dict_MeasurementResult['MeasurementData/powerTraces_Vrms2PHz'] \
        = np.asarray(powerTraces) 
        
    dict_MeasurementResult['MeasurementData/avgVals'] \
        = np.asarray(avgVals) 
    dict_MeasurementResult['MeasurementData/stdVals'] \
        = np.asarray(stdVals) 
    dict_MeasurementResult['MeasurementData/stdVals'] \
        = np.asarray(stdVals) 
    
    # continously save Data and figure
    saveDictToHdf5.save_dict_to_hdf5(
        dict_MeasurementResult, 
        dataFilePath)
    
    
    # make scatter plot 
    line1.set_xdata(durationValues)
    line1.set_ydata(avgVals)
    axs[0].set_xlim(0,duration)
    axs[0].set_ylim([np.min(avgVals),np.max(avgVals)])
    
    line2.set_xdata(durationValues)
    line2.set_ydata(stdVals)
    axs[1].set_xlim(0,duration)
    axs[1].set_ylim([np.min(stdVals),np.max(stdVals)])
    
    # redraw just the points
    fig.canvas.draw()
    fig.canvas.flush_events()
    

visaobj.close()