# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 10:51:58 2023

@author: ibaldoni
"""
    
import matplotlib.pyplot as plt
from FSWP_Control_RhodeSchwarz_class import RhodeSchwarz_FSWP
import time
import pandas as pd
import numpy as np
import sys
sys.path.append(r'\\menloserver\MFS\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\python Util functions')
from Plot_aux_functions import Plot_parameters, makeTable,add_grids
Plot_parameters(width=8)
plt.figure()
add_grids()
def Mode(mode):
    if mode == 'PNO':
        SpectrumMode = False
        PhaseNoiseMode = True
        Ylabel = 'ℒ Phase Noise [dBc/Hz]'
    elif mode == 'SAN':
        PhaseNoiseMode = False
        SpectrumMode = True
        Ylabel = 'PSD [dBm/Hz]'
        
    return PhaseNoiseMode, SpectrumMode, Ylabel


################------ RUN SCRIPT ------################

resourceStr = 'USB0::0x0AAD::0x0120::101559::INSTR'
fswp = RhodeSchwarz_FSWP(resourceStr)

Measurement_details = 'Test of 80 MHz'
mode = 'SAN'    
fswp.ContinuousMeasurement('OFF')
savefiles = True





begin = int(time.time())
file_path = f'{begin}_{mode}_{Measurement_details}'
PhaseNoiseMode, SpectrumMode, YLabel = Mode(mode)
# fswp.windowsAvailable()

if SpectrumMode == True:
    fswp.switchSpectrumTrace(mode='SAN')
      
    # fswp.startFrequency(start=1E6)     
    # fswp.stopFrequency(stop=81E6)    
    # fswp.centerFrequency(center=80E6)            
    # fswp.setResolutionBandwidth(bandwidth=0.01e6)
    
    
    center  = fswp.queryCenterFrequency()
    start   = fswp.queryStartFrequency()
    stop    = fswp.queryStopFrequency()   
    ResBW   = fswp.queryResolutionBandwidth()
    time.sleep(1.50)
    
    Data = fswp.SpectrumTrace(traceNumber = 1)   
    frequency_axis = np.linspace(start*1E-6,stop*1E-6,len(Data))
    
    plt.plot(frequency_axis, Data)
    plt.ylabel(YLabel)
    plt.xlabel('Frequency [MHz]')
    
    # Create a DataFrame
    df = pd.DataFrame({'Frequency': frequency_axis, 'Amplitude': Data})
    # df.to_csv(csv_file_path, index=False)
    if savefiles: df.to_csv(f'{file_path}.csv', index=False)
    if savefiles: plt.savefig(f'{file_path}.png')


if PhaseNoiseMode == True:        
    # fswp.PNoise_Status(traceNumber = 'Phase Noise')
    fswp.switchSpectrumTrace(mode='PNO')
    results = fswp.PhaseNoiseTrace(traceNumber = 1)    
    plt.semilogx(results.Frequency,results.dBc_Hz)
    plt.ylabel(YLabel)
    plt.xlabel('Frequency [Hz]')
    if savefiles: results.to_csv(f'{file_path}.csv', index=False)
    if savefiles: plt.savefig(f'{file_path}.png')