# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 10:27:43 2021

@author: Administrator
"""


import numpy as np
import matplotlib.pyplot as plt
import time
import datetime as dt
import pandas as pd

from Synt_AgilentN5181A import AN5181A
# from RigolDG4162 import RigolDG4162
from Powermeter_PM100A import Thorlabs_PM100A

from AgilentN9030A import AgilentN9030A

measurementPurpose = 'Repetition Rate vs. Power vs. Detuning'

##############################################################################
##############################################################################

resourceStr_Synt = 'TCPIP0::A-N5181A-42764::inst0::INSTR'
synt = AN5181A(resourceStr_Synt)

resourceStr_PXA = 'TCPIP0::169.254.181.231::INSTR'
pxa = AgilentN9030A(resourceStr_PXA)

pxa.setResolutionBandwidth(2e2) #1e3

# resourceStr_FG = 'TCPIP0::169.254.187.139::inst0::INSTR'
# fg = RigolDG4162(resourceStr_FG)

Str_Powermeter = 'USB0::0x1313::0x8079::P1001184::INSTR'
powermeter = Thorlabs_PM100A(Str_Powermeter)


##############################################################################
##############################################################################    
Temperature_Voltage = 4.5
# pxa.setAutoTune()
time.sleep(3)

### ------------------- Run the program ------------------- ###

# sweep_power = np.arange(0,1,1)#np.arange(-1,1,1)
sweep_detuning = np.arange(120,350,10)
n_points_pxa = 200
result = [0,0,0,0,0]



power = Temperature_Voltage

shift_frequency = 5e4
for d in sweep_detuning:
    synt.set_frequency(d)
    time.sleep(.5) # Enough time for the system to change the detuning
    
    
    # pxa.setAutoTune();time.sleep(4)
    
    # We need to move the window of the PXA Measurement
    data0 = pxa.readCurrentTraceData()
    psd0 = data0['powerSpectralDensity_dBm']
    psd_max0 = psd0.max()
    freq_carrier_index0 = np.where(psd0 == psd_max0)[0]
    freq_carrier0 = data0['frequencies_Hz'][freq_carrier_index0][0]
    pxa.setStartFreq(freq_carrier0-shift_frequency)
    pxa.setStopFreq(freq_carrier0+shift_frequency)

    
    # begin = time.time()           # To measure time of acquisition
    carrier = []    
    # The PXA requires 500 ms to make the window change.
    time.sleep(.5)
    
    
    resourceStr = 'USB0::0x1313::0x8079::P1001184::INSTR'
    powermeter = Thorlabs_PM100A(resourceStr)
    powermeter_power = powermeter.readPower()
    
    
    for i in range(0,n_points_pxa):
        # date_time = dt.datetime.now()
        # d = date_time.strftime("%H:%M:%S")
        
        data = pxa.readCurrentTraceData()
        
        psd = data['powerSpectralDensity_dBm']
        psd_max = psd.max()
        
        freq_carrier_index = np.where(psd == psd_max)[0]
        freq_carrier = data['frequencies_Hz'][freq_carrier_index][0]
        
        carrier.append(freq_carrier)
        
    # tiempo = time.time() - begin  # To measure time of acquisition
    # print(tiempo,'sec')
    std_ = np.std(carrier)      #standard deviation of freq_carrier
    mean_ = np.mean(carrier)    #mean value of freq_carrier
    
    
    

    
    newrow = [power,d, mean_, std_,powermeter_power]
    result = np.vstack([result, newrow])
        
Result = pd.DataFrame(result,columns=['Voltage','Detuning','CarrierMean','CarrierStd','PW_Power'])   

pxa.disconnect();
synt.disconnect()
Result = Result.drop(0)
# Result.CarrierMean.plot()
# plt.plot(Result.CarrierMean, marker='o', color='b')
# plt.errorbar(Result.index,Result.CarrierMean, yerr=Result.CarrierStd, fmt=None, color='b')

plt.figure(figsize=(12,8))
plt.errorbar(Result.Detuning, Result['CarrierMean']*1e-9, yerr=Result['CarrierStd']*1e-9,marker='o')
plt.xlabel('Detuning [MHz]',fontsize=20)
# plt.ylabel('Beat detection [GHz]',fontsize=20)
# plt.title('Beat between two RIO Laser in single soliton step vs. detuning',fontsize=20)
# plt.tick_params(labelsize=17)
# plt.grid()
# plt.savefig('Beat between two RIO Laser in single soliton step vs. detuning.png')
    
Result.to_csv('20210810_single soliton (AOM) vs. Detuning vs. Power at %s V.csv'%power)