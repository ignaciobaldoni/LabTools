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
# from Powermeter_PM100A import readPower

from AgilentN9030A import AgilentN9030A

resourceStr = 'TCPIP0::A-N9030A-60137.local::hislip0::INSTR'





from AgilentN9030A import AgilentN9030A


measurementPurpose = 'Repetition Rate vs. Power vs. Detuning'

##############################################################################
##############################################################################

resourceStr_Synt = 'TCPIP0::A-N5181A-42764::inst0::INSTR'
synt = AN5181A(resourceStr_Synt)

resourceStr_PXA = 'TCPIP0::169.254.181.231::INSTR'
pxa = AgilentN9030A(resourceStr_PXA)

# resourceStr_FG = 'TCPIP0::169.254.187.139::inst0::INSTR'
# fg = RigolDG4162(resourceStr_FG)

# Str_Powermeter = 'USB0::0x1313::0x8079::P1001184::INSTR'


##############################################################################
##############################################################################    

### ------------------- Run the program ------------------- ###

sweep_power = np.arange(0,1,1)#np.arange(-1,1,1)
sweep_detuning = np.arange(100,160,10)
n_points_pxa = 50


result = [0,0,0,0]

for p in sweep_power:
    power = p
    # fg.is_enable()
    # fg.set_offset(p)
    # time.sleep(2)
    # power = readPower(Str_Powermeter)

    for d in sweep_detuning:
        # synt.set_frequency(d)
        time.sleep(2)
        begin = time.time()
        carrier = []    #np.zeros(n_points_pxa) 
        for i in range(0,n_points_pxa):
            # date_time = dt.datetime.now()
            # d = date_time.strftime("%H:%M:%S")
            
            data = pxa.readCurrentTraceData()
            
            psd = data['powerSpectralDensity_dBm']
            psd_max = psd.max()
            
            freq_carrier_index = np.where(psd == psd_max)[0]
            freq_carrier = data['frequencies_Hz'][freq_carrier_index]
            
            carrier.append(freq_carrier)
        tiempo = time.time() - begin
        print(tiempo,'sec')
        std_ = np.std(carrier)      #standard deviation of freq_carrier
        mean_ = np.mean(carrier)    #mean value of freq_carrier
        
        

        
        newrow = [power,d, mean_, std_]
        result = np.vstack([result, newrow])
        
Result = pd.DataFrame(result,columns=['Power','Detuning','CarrierMean','CarrierStd'])   

pxa.disconnect();
Result = Result.drop(0)
Result.CarrierMean.plot()
# plt.plot(Result.CarrierMean, marker='o', color='b')
# plt.errorbar(Result.index,Result.CarrierMean, yerr=Result.CarrierStd, fmt=None, color='b')


plt.errorbar(Result.index, Result['CarrierMean'], yerr=Result['CarrierStd'],marker='o')