# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 13:51:21 2021

@author: akordts


Igorevna

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
measurementPurposeShort = 'pump stabilisation'

# singleMeasureName = 'CrosCor configuration - EDFA_3A5 - lock on - input -B - PI300kHz - 6G8'
# singleMeasureName = 'CC conf - EDFA3A7 - feedback 7G0 - output'
singleMeasureName = 'cc conf - EDFA 3A7 - lb1005 lock - chip coupling'

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

dc_voltage_V = 4.12

#select intervals
selectedIntervals = [ 
                0,           # 0-1 Hz x25min per avg
                1,           # 1-10 Hz x2min per avg
                1,           # 10-100 Hz x13s per avg
                1,           # 100-1k Hz
                1,           # 1k-10k Hz
                1,           # 10k-100k Hz
                1,           # 100k-1M Hz
                1            # 1M-10M Hz
            ]

# selectedIntervals = [0,0,0,0,0,0,0,1]

avgNumValues = [
                2,           # 0-1 Hz  x25min per avg
                1,           # 1-10 Hz x2min per avg
                5,           # 10-100 Hz x13s per avg
                10,           # 100-1k Hz 1.3s
                100,           # 1k-10k Hz
                100,           # 10k-100k Hz
                100,           # 100k-1M Hz
                100            # 1M-10M Hz        
            ]

# avgNumValues = [1,1,100,200,5000,5000,10000,10000]
# avgNumValues = [1,1,1,1,1000,1000,1000,1000]

# predefined frequency ranges 
freRangeValues = 10.**np.arange(-1,8,1)

# test high end res 
# test low end range

# freRangeValues = [0.5e-3,0.5,10,100,1e3,1e4,1e5,1e6,1e6+1000]

# measurement set to always use max sweep points
# # set number of points per interval
#     # <number> ::= 51|101|201|401|801|1601|3201
# sweepPointValues = [
#                 3201,           # 0-1 Hz
#                 3201,           # 1-10 Hz
#                 3201,           # 10-100 Hz
#                 3201,           # 100-1k Hz
#                 3201,           # 1k-10k Hz
#                 3201,           # 10k-100k Hz
#                 3201,           # 100k-1M Hz
#                 3201            # 1M-10M Hz        
#             ]

#update data dict
dict_MeasurementResult['SettingsData/selectedIntervals'] \
        = np.asarray(selectedIntervals)
dict_MeasurementResult['SettingsData/avgNumValues'] \
        = np.asarray(avgNumValues)
dict_MeasurementResult['SettingsData/freRangeValues'] \
        = np.asarray(freRangeValues)
        
dict_MeasurementResult['MeasurementData/dc_voltage_V'] \
        = np.asarray(dc_voltage_V)
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

for index in np.arange(len(selectedIntervals)):
    if(selectedIntervals[index]):
        # measure dc value
        # measure spectrum 
        
        # currently maximum points are used
        # sweepPts = sweepPointValues[index]
        sweepPts = None
        
        startFreq = freRangeValues[index]
        stopFreq = freRangeValues[index+1]
        avgPts = avgNumValues[index]
        
        freqs,pows,rbwValue = getScalarRangeData(
                                    visaobj,
                                    sweepPts,
                                    startFreq,
                                    stopFreq,
                                    avgPts
                                )
        
        print('rbwValue: ' + str(rbwValue))
        
        psdVs_VrmsPrtHz = np.sqrt(np.array(pows)/rbwValue)
        
        freqValues = freqValues + freqs
        powValues = powValues + pows
        psdVals_VrmsPrtHz = psdVals_VrmsPrtHz + psdVs_VrmsPrtHz.tolist()
        rbwValues = rbwValues + [rbwValue]
        
        
        
        # save data
            #update data dict
        dict_MeasurementResult['MeasurementData/rbwValues'] \
                = np.asarray(rbwValues)
        dict_MeasurementResult['MeasurementData/freqValues_Hz'] \
                = np.asarray(freqValues)
        dict_MeasurementResult['MeasurementData/powValues_Vrms2'] \
            = np.asarray(powValues)
        dict_MeasurementResult['MeasurementData/powValues_Vrms_rtHz'] \
            = np.asarray(psdVals_VrmsPrtHz) 
            
        # continously save Data and figure
        saveDictToHdf5.save_dict_to_hdf5(
            dict_MeasurementResult, 
            dataFilePath)
        
        # plot data
        plotRinFigures(
            freqValues,
            psdVals_VrmsPrtHz,
            dc_voltage_V,
            figureFilePath,
            singleMeasureName
            )
    


visaobj.close()