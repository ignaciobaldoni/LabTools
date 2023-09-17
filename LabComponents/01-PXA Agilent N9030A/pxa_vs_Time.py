# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 10:48:01 2023

@author: ibaldoni

Script for collecting data from the CXA KeysightN9000B
"""

#%% Personal functions for plotting and units
import sys
sys.path.append(r'\\menloserver\MFS\03-Operations\02-DCP\01-DCP_Management\01-Gruppenmanagement\UMS\05_LabTools_TBD\10-CXA Keysight N9000b')
from CXA_KeysightN9000B import KeysightN9000B

sys.path.append(r'\\menloserver\MFS\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\python Util functions')
from Plot_aux_functions import Plot_parameters, makeTable
Plot_parameters()
import time

import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

folder_name = r'\\menloserver\mfs\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\HHI PD Spectrum'

optPower = 20
fileName    = f'OptPower {optPower} mW. Bias at 11 V. 50 GHz spectrum'  


if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        
        
# Select the parameters you would like to use
Res_BW      = 5000
start_freq  = 100.00e6
stop_freq   = 50e9
# span        = 13e9
center_freq = 25e9

PhaseNoise          = False
Spectrum_Analyzer   = True

new_measurement     = False

saveFigs            = True

### ----------------- Initiate CXA ------------------ ###

resourceStr = 'USB0::0x0957::0x0D0B::US51160137::INSTR'



cxa = KeysightN9000B(resourceStr)
cxa.connect(resourceStr)
 

result_name = folder_name+str('\\')+fileName

carrier = []

time_begin = time.time()
TIME=[]

measurement_time = 60*30

if Spectrum_Analyzer:
    while time.time()-time_begin < measurement_time:
        Time = time.time()-time_begin
        
        if new_measurement:
            cxa.setMode('SA')
            cxa.restartMeasurement()
            cxa.setStartFreq(start_freq)
            cxa.setStopFreq(stop_freq)
            cxa.setResolutionBandwidth(Res_BW)
            # cxa.setSpan(span)
            cxa.setCenterFrequency(center_freq)
            
        data = cxa.readCurrentTraceData()
    
        freqs = data['frequencies_Hz']
        psd = data['powerSpectralDensity_dBm']
        rbw = data['resolutionBandwidth_Hz']
        
        carrier_max = np.max(psd[1:])
        index_carrier_max = np.argmax(psd[1:])
        
        
        title = f'{carrier_max:.2f} dBm at {freqs[index_carrier_max]*1e-9:.2f} GHz'
        
        # print(carrier_max)
        carrier.append(carrier_max)
        TIME.append(Time)
        time.sleep(10)
        
    
plt.plot()    
plt.plot(TIME, carrier,'-o')
plt.xlabel('Seconds [s]')
plt.ylabel('10 GHz output power [dBm]')
plt.savefig(f'forRS_{time_begin}.png')    


cxa.disconnect();