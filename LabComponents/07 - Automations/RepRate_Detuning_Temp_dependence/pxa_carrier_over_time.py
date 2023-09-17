# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 10:27:43 2021

@author: Administrator
"""


import numpy as np
import matplotlib.pyplot as plt
import time
# import datetime as dt
import pandas as pd

from Synt_AgilentN5181A import AN5181A
# from RigolDG4162 import RigolDG4162
from Powermeter_PM100A import Thorlabs_PM100A

from AgilentN9030A import AgilentN9030A

from datetime import datetime

from OSA_Yokogawa import Yokogawa_AQ6370B


    
   
    
   
    
    
    
    
    

resourceStr_Synt = 'TCPIP0::A-N5181A-42764::inst0::INSTR'
synt = AN5181A(resourceStr_Synt)



# measurementPurpose = 'Repetition Rate vs. Power vs. Detuning'

##############################################################################
##############################################################################


resourceStr_PXA = 'TCPIP0::169.254.181.231::INSTR'
pxa = AgilentN9030A(resourceStr_PXA)

resourceStr_OSA = 'GPIB0::1::INSTR' # OSA Path with GPIB
osa = Yokogawa_AQ6370B(resourceStr_OSA)

pxa.setResolutionBandwidth(100e3) #1e3

# resourceStr_FG = 'TCPIP0::169.254.187.139::inst0::INSTR'
# fg = RigolDG4162(resourceStr_FG)




##############################################################################
##############################################################################    
Temperature_Voltage = 4.5
# pxa.setAutoTune()
time.sleep(3)

### ------------------- Run the program ------------------- ###

# sweep_power = np.arange(0,1,1)#np.arange(-1,1,1)
detuning = np.arange(300,310,10)
n_points_pxa = 1500
result = [0,0]









# begin = time.time()           # To measure time of acquisition
carrier = []    
Time = []
# The PXA requires 500 ms to make the window change.
time.sleep(.5)


'''
# Up to 10 Hz can "follow"
# The time measurement takes too much......time. And reduces the quality of 
# the acquisition
'''



for d in detuning:
    print(d)
    synt.set_frequency(d)
    time.sleep(.5) # Enough time for the system to change the detuning
    
    begin = time.time()
    carrier = []
    
    for i in range(0,n_points_pxa):
        
        # datetime object containing current date and time
        # now = datetime.now()
         
    
        # dd/mm/YY H:M:S
        # dt_string = now.strftime("%S")
        # print("date and time =", dt_string)
        
        data = pxa.readCurrentTraceData()
        
        psd = data['powerSpectralDensity_dBm']
        psd_max = psd.max()
        
        freq_carrier_index = np.where(psd == psd_max)[0]
        freq_carrier = data['frequencies_Hz'][freq_carrier_index][0]
        
        carrier.append(freq_carrier)
        # Time.append(dt_string)
        
    
            
    end = time.time()-begin
    
    
    time_for_plot = np.linspace(0,end,len(carrier))
    
    
    
    # df = {'Time':Time,'Carrier':carrier}
    # df2 = pd.DataFrame(df)
    
    # plt.plot(df2.Time,df2.Carrier)
    
    
    df = {'Time':time_for_plot,'Carrier':carrier}
    df2 = pd.DataFrame(df)
    
    Result = pd.DataFrame(df2)   
    
    
    
    Result.to_csv('20210810_Beat between two cw over time for With_RIO_Program_OFF_AndDefaultSettings_v2.csv' )
    
    trace = 'c'
    start = '1520'
    stop = '1580'
    resolution = '0.02'
    sensitivity = 'SHI3'
    
    # run the measurement
    wavelength, intensity = osa.get_trace(trace,start,stop,resolution)
    
    plt.figure(figsize=(12,8))
    plt.plot(wavelength,intensity)
    plt.ylim([-150,0])
    plt.grid()
    plt.xlabel('Wavelength [nm]',fontsize=20)
    plt.ylabel('PSD [dB/nm]',fontsize=20)
    plt.title('Control of the comb',fontsize=20)
    plt.tick_params(labelsize=17)
    # plt.savefig(measurementPurpose+'.png')
    
    Result.plot(x='Time')

pxa.disconnect();
synt.disconnect()

