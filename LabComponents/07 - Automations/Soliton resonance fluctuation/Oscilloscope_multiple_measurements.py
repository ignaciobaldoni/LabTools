"""
Created on Thu Jan 28 17:49:12 2021

@author: Ignacio

Automation code
"""

from Width_measurement import Width_measurement
from Width_calculation import Width_calculation

from labTools_utilities import saveDictToHdf5
import matplotlib.pyplot as plt
import numpy as np

import os.path
import datetime as dt
import os
import sys
import importlib.util
import time
from distutils import dir_util

######################### Import the laser's module #########################
# spec = importlib.util.spec_from_file_location("NewFocusControl", "C:\\Users\\Administrator.MenloPC208\\Desktop\\New Focus Control\\pyLaser\\NewFocusControl.py")
# module = importlib.util.module_from_spec(spec)
# sys.modules[spec.name] = module 
# spec.loader.exec_module(module)
#############################################################################

Multiple_measurements = True
n_measurements = 400
show_plots = False

year = dt.datetime.today().year
month = dt.datetime.today().month
day =  dt.datetime.today().day

month = '0'+str(month) if len(str(month)) == 1 else month
day = '0'+str(day) if len(str(day)) == 1 else day

save_path = '//menloserver/MFS/03-Operations/02-DCP/03-Entwicklungsprojekte/'

save_path_local = 'D:/MicroCombLab/save_Local/'
project = '9552-KECOMO/'
folder = '52-Messergebnisse/'
fileType = '.h5'

### Today
date = str(year)+str(month)+str(day)

in_raw_data = '1-Raw Data/' 
in_data_analysis = '2-Data Analysis/' 
in_results  = '3-Results/'

measurementPurposeShort = 'D63_2_12GHz_metalic_setup/'
file        = 'Test_of_driftings_'
iteration   ='Only_measurement'

directory1 = save_path + project + folder +  \
    date + measurementPurposeShort + in_raw_data
    
directory2 = save_path + project + folder + \
    date + measurementPurposeShort + in_data_analysis
    
directory3 = save_path + project + folder + \
    date + measurementPurposeShort + in_results

directory0 = save_path_local + \
    date + measurementPurposeShort + in_raw_data

if not os.path.exists(directory0):
    os.makedirs(directory0)
    
if not os.path.exists(directory1):
    os.makedirs(directory1)
    
if not os.path.exists(directory2):
    os.makedirs(directory2)

if not os.path.exists(directory3):
    os.makedirs(directory3)


fileName = os.path.join(save_path_local, 
                        # project+ \
                        # folder+ \
                        date +  \
                        measurementPurposeShort + \
                        in_raw_data +  \
                        file +  \
                        iteration + \
                        fileType)       

saveResults = os.path.join(save_path_local,
                            # project+ \
                            # folder+ \
                            date +  \
                            measurementPurposeShort + \
                            in_results +  \
                            file +  \
                            iteration + \
                            fileType)      

if Multiple_measurements == True:
    for i in range(0,n_measurements+1):
        iteration = '_'+str(i)
        fileName = os.path.join(save_path_local, 
                                # project+ \
                                # folder+ \
                                date +  \
                                measurementPurposeShort + \
                                in_raw_data +  \
                                file +  \
                                iteration + \
                                fileType)  
            
        
        Width_measurement(fileName)
        print(i)
        
        if i%200 == 0: #Saves data in the server every 200 traces recorded
            print('----------------------------')
            print('Saving data in the server...')
            print('----------------------------')
            path_in_server = os.path.join(save_path, 
                                project+ \
                                folder+\
                                date +  \
                                measurementPurposeShort + \
                                in_raw_data)  
            dir_util.copy_tree(directory0, path_in_server)
            #This function allows to overwrite the files.
        

else:
    fileName = os.path.join(save_path, 
                            project+ \
                            folder+ \
                            date +  \
                            measurementPurposeShort + \
                            in_raw_data +  \
                            file +  \
                            iteration + \
                            fileType)
    Width_measurement(fileName)
    
        
############################## SHOW PLOTS ###################################
if show_plots == True:
    
    dict_Result = saveDictToHdf5.load_dict_from_hdf5(fileName)
    
    timeTrace = dict_Result['measurementData'] \
                                ['fiberResonatorTransmission_traceData'] \
                                ['time_axes']
    
    # get fiber loop cavity transmission trace
    voltageTrace = dict_Result['measurementData'] \
                                ['fiberResonatorTransmission_traceData'] \
                                ['voltage_axes']
                                
    # get ring resonator transmission trace
    ringResonatorTransmissionTrace \
        = dict_Result['measurementData'] \
                    ['ringResonatorTransmission_traceData'] \
                    ['voltage_axes']
                    
    # get function generator transmission trace
    functionGeneratorTrace \
    = dict_Result['measurementData'] \
                ['funtionGeneratorRamp_traceData'] \
                ['voltage_axes']
              
    plt.figure(1) 
    plt.plot(timeTrace,voltageTrace,label ='Fiber Loop Cavity')
    plt.plot(timeTrace,ringResonatorTransmissionTrace,label ='Ring resonator')
    plt.plot(timeTrace,functionGeneratorTrace,label ='Function generator')
    plt.xlabel('time (s)')
    plt.ylabel('Channel data')
    plt.legend()
    
    
##############################################################################   


# NewFocusControl.NewFocus(1)
# Width_calculation(fileName, saveResults)