# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 17:40:30 2021

@author: ibaldoni
"""

from labTools_utilities import saveDictToHdf5
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import os.path

######################### LOAD FILE ##########################################

year = dt.datetime.today().year
month = dt.datetime.today().month
day =  dt.datetime.today().day -1

month = '0'+str(month) if len(str(month)) == 1 else month
day = '0'+str(day) if len(str(day)) == 1 else day

save_path = '//menloserver/MFS/03-Operations/02-DCP/03-Entwicklungsprojekte/'
project = '9556-COSMIC/'
folder = '52-Messergebnisse/'
fileType = '.h5'

### Today
date = str(year)+str(month)+str(day)

in_raw_data = '1-Raw Data/' 
in_data_analysis = '2-Data Analysis/' 
in_results  = '3-Results/'

measurementPurposeShort = '_Soliton_steps_at_1550_chips/'
subfolder               = str(date)+'_F3_100Hz_2560mA_v2/'
file                    = 'Test_of_driftings_'

save_figs = True

fileType_img = '.png' 
size_fig    = (12,8)
fig_resolution = 100    # a.k.a., dpi

for i in range(0,1):
    iteration   = 'Only_measurement'

    fileName = os.path.join(save_path, project+ \
                                        folder+ \
                                        date +  \
                                        measurementPurposeShort + \
                                        subfolder + \
                                        in_raw_data +  \
                                        file +  \
                                        iteration + \
                                        fileType)    
    
    ##############################################################################
    
    dict_Result = saveDictToHdf5.load_dict_from_hdf5(fileName)
    
    timeTrace = dict_Result['measurementData'] \
                                ['fiberResonatorTransmission_traceData'] \
                                ['time_axes']
    timeTrace = timeTrace*1000
    # get fiber loop cavity transmission trace
    voltageTrace = dict_Result['measurementData'] \
                                ['fiberResonatorTransmission_traceData'] \
                                ['voltage_axes']
                                
    # get ring resonator transmission trace
    # Actually, is the generated light trace but for compatibilty purposes 
    # between the oscilloscope measurements and the analysis, we mantain the 
    # same name as the oscilloscope script
    
    ringResonatorTransmissionTrace \
        = dict_Result['measurementData'] \
                    ['ringResonatorTransmission_traceData'] \
                    ['voltage_axes']
    
    plt.figure(num=1, figsize=size_fig, dpi=fig_resolution) 
    plt.plot(timeTrace,voltageTrace/np.max(voltageTrace),linewidth = 0.1)
    plt.plot(timeTrace,ringResonatorTransmissionTrace/np.max(ringResonatorTransmissionTrace))
    plt.tick_params(labelsize=17)
    plt.xlabel('Time (ms)',fontsize=20)
    plt.ylabel('Voltage (a.u)',fontsize=20)
    if save_figs == True:
        saveResults = os.path.join(save_path, project+ \
                                    folder+ \
                                    date +  \
                                    measurementPurposeShort + \
                                    subfolder + \
                                    in_results +  \
                                    file +  \
                                    iteration + \
                                    fileType_img) 
        plt.savefig(saveResults)
    
    