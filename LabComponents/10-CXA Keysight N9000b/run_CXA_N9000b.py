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


resourceStr = 'USB0::0x2A8D::0x1A0B::MY60250816::INSTR'

# resourceStr = 'TCPIP0::10.0.2.225::5025::SOCKET'



cxa = KeysightN9000B(resourceStr)

cxa.connect(resourceStr)


Res_BW      = 1000
start_freq  = 9.00e6
stop_freq   = 11e6
span        = 1e6
center_freq = 10e6

PhaseNoise = True
Spectrum_Analyzer = True
 
if Spectrum_Analyzer:
    cxa.setMode('SA')
    cxa.restartMeasurement()
    cxa.setStartFreq(start_freq)
    cxa.setStopFreq(stop_freq)
    cxa.setResolutionBandwidth(Res_BW)
    cxa.setSpan(span)
    cxa.setCenterFrequency(center_freq)
    data = cxa.readCurrentTraceData()
    freqs = data['frequencies_Hz']
    psd = data['powerSpectralDensity_dBm']
    rbw = data['resolutionBandwidth_Hz']

    fig, ax = plt.subplots()
    ax.plot(freqs*1.e-6, psd)
    
    ax.set(xlabel='frequency [MHz]', ylabel='PSD [dBm]' + '(RBW = '+str(rbw*1.e-3)+'kHz)')
    ax.grid()
    plt.show()

if PhaseNoise:
    
    
    cxa.setAutoTune()
    cxa.setToSingleMeasurement(True)
    cxa.setMode('PNOISE')
    cxa.setCenterFrequency(center_freq)

    
    
    cxa.plotPhaseNoiseTrace()
    makeTable()


cxa.disconnect();