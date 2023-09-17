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

import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

folder_name = r'\\menloserver\mfs\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\HHI PD Spectrum'

optPower = 9.25
fileName    = f'OptPower {optPower} mW. Bias at 15.8 V. 10 GHz output'  


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
# resourceStr = 'TCPIP0::10.0.2.225::5025::SOCKET'


cxa = KeysightN9000B(resourceStr)
cxa.connect(resourceStr)
 

result_name = folder_name+str('\\')+fileName



if Spectrum_Analyzer:
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
    

    
    
    

    fig, ax = plt.subplots()
    ax.plot(freqs*1e-6, psd, color='#00441b',label = title)
    
    # ax.set(xlabel='frequency [MHz]', ylabel='PSD [dBm]' + f' (RBW = {rbw*1e-3:.1f} kHz )')
    ax.set(xlabel='frequency [MHz]', ylabel=f' (RBW = {rbw*1e-3:.1f} kHz )')
    ax.grid(alpha=0.25)
    plt.ylim([-120,10])
    plt.legend()
    plt.title(f'Spectrum with optical power {optPower} mW')
    
    # makeTable(freqs, psd, fig, x_pos = 0.6,y_pos=0.6, print_freqs=[10e6,10.2e6])
    if saveFigs: plt.savefig(result_name+'_SA.png')
    df = pd.DataFrame({'freqs': freqs, 'psd': psd})
    if saveFigs: df.to_csv(result_name+'_SA.csv', index=False)
    plt.show()
    
    # cxa.savePNGimage('Prueba.png')
    
if PhaseNoise:
    
    if new_measurement:
        cxa.setAutoTune()
        cxa.setToSingleMeasurement(True)
        cxa.setMode('PNOISE')
        cxa.setCenterFrequency(center_freq)
     
    # 1 = raw data, 2 = average
    traces = [1,2] 
    
    colors = ['#00441b','orange','#762a83','#5aae61','#d395dd','darkblue','darkblue','darkblue','darkblue']
    frequencies, spectrum, fig = cxa.plotPhaseNoiseTrace(traceNumber=traces,
                                                         default_colors = colors)
    makeTable(frequencies, spectrum, fig, print_freqs=[100, 1000, 10000])
    plt.grid(True, which='major', color='k',linestyle='-')  # style of major grid lines
    plt.grid(True, which='minor', color='grey', linestyle='--')  # style of minor grid lines
    if saveFigs: plt.savefig(result_name+'_PhaseNoise.png')
    
    df_PN = pd.DataFrame({'frequencies': frequencies, 'spectrum': spectrum})
    if saveFigs: df.to_csv(result_name+'_PN.csv', index=False)

cxa.disconnect();