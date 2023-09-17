# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 10:37:20 2023

@author: ibaldoni

FSWP_Reader 2.0

"""

## Personal functions 
import sys
sys.path.append(r'\\menloserver\MFS\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\python Util functions')
from Plot_aux_functions import Plot_parameters, makeTable # Import all functions from the script
from util_Functions import shot_noise_cw, shot_noise_pulsed, thermal_noise, jitter_calc

Plot_parameters(width=10)

import pandas as pd
import matplotlib.pyplot as plt

def get_data_ranges(path, traces):
    with open(path, 'r') as file:
        lines = file.readlines()
        
        def find_range(start_index, end_index):
            for i, line in enumerate(lines[start_index:end_index]):
                if line[0].isdigit():
                    start_index = i + start_index
                    break
            for i, line in enumerate(lines[start_index:end_index]):
                if line[0].isalpha():
                    end_index = i + start_index
                    break
            return start_index, end_index

        trace1_start, trace1_end = find_range(0, len(lines))
        
        trace2_start, trace2_end = 0, 0
        if traces > 1:
            trace2_start, trace2_end = find_range(trace1_end + 1, len(lines))
            
        trace3_start, trace3_end = 0, 0
        if traces > 2:
            trace3_start, trace3_end = find_range(trace2_end + 1, len(lines))
            
        trace4_start, trace4_end = 0, 0
        if traces > 3:
            trace4_start, trace4_end = find_range(trace3_end + 1, len(lines))

    return trace1_start, trace1_end, trace2_start, trace2_end, trace3_start, trace3_end, trace4_start, trace4_end





folder = r'\\menloserver\MFS\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\Coherent PD with FSWP\\'
    

subfolder = 'MiniCircuits amplifier\\'
files = ['7.5 mW (6.44 dBm) Bias 6.50 V.CSV',
          '13.0 mW (11.35 dBm) Bias 6.5 V.CSV',
          '17.5 mW (14.65 dBm) Bias 11 V.CSV']

subfolder = 'HMC amplifier\\'
files = ['7.5 mW (1.98 dBm) Bias 12 V.CSV',
          '13.0 mW (7.29 dBm) Bias 8 V.CSV',
          '17.5 mW (10.53 dBm) Bias 11.9 V.CSV']

subfolder = 'No amplifier\\'
files = ['7.5 mW (-11.46 dBm) Bias 6.59.CSV',
          '13.0 mW (-5.77 dBm) Bias 9.86 V.CSV',
          '17.0 mW (-2.38 dBm) Bias 13.58 V.CSV',
          '7.5 mW (-11.46 dBm) Bias 6.6 V (Longer XCorr).CSV']


subfolder = 'No amplifier longer XCorr\\'

files = [
    # '7.8 mW (-11.89 dBm) Bias 6.6 V.CSV',
         # '7.667 mW (-12 dBm) Bias 6.6 V.CSV',
           # '17.5 mW (-3.12 dBm) Bias 13.5 V.CSV',
            '17.5 mW (-3.24 dBm) Bias 12.0 V.CSV',
           # '17.5 mW (-3.43 dBm) Bias 10.0 V.CSV',
           '17.5 mW (-3.77 dBm) Bias 8.0 V.CSV',
           # 'HHI 17.5 mW (-5.19 dBm) Bias 18.5 V.CSV',
           'HHI 17.5 mW (-5.84 dBm) Bias 13.0 V.CSV',
          # 'HHI 7.5 mW (-12.8 dBm) Bias 13 V.CSV'
          
         ]





for i in files:    
    path = folder + subfolder + i 
    
    
    # -159.77 dBc/Hz
    
    trace1_start, trace1_end, trace2_start,\
        trace2_end, trace3_start, trace3_end, trace4_start,\
            trace4_end = get_data_ranges(path, traces=2)
    
    def read_trace_data(start, end):
        return pd.read_csv(path, sep=';', decimal=',',  on_bad_lines='skip', skiprows=start, nrows=end - start, names=['frequency', 'value','NaNs'])
    
    med = read_trace_data(trace1_start, trace1_end)
    med2 = read_trace_data(trace2_start, trace2_end)
    # med3 = read_trace_data(trace3_start, trace3_end)
    # med4 = read_trace_data(trace4_start, trace4_end)
    
    frequency1 = med.frequency.astype(float)
    value1 = med.value.astype(float)
    
    frequency2 = med2.frequency.astype(float)
    value2 = med2.value.astype(float)
    
    
    # plt.semilogx(frequency2, value2,label=f'{i[:-4]}')
    plt.semilogx(frequency1, value1,label=f'{i[:-4]}')
    
    plt.grid(visible=True, which='both', color='lightgrey', linestyle='--')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Phase Noise [dBc/Hz]')
    plt.show()
    plt.legend()
    # plt.title(subfolder[:-2])
    plt.title('Comparison Finisar and HHI PD')
    
plt.xlim(300,1e6)


rin = pd.read_csv('RIN_17.5mW_100avg.csv',skiprows=7,sep=',', names=['Frequency','Mag^2 (V^2 / Hz)',' PSD (dBV^2 / Hz)','RIN',' Integrated Volts RMS', 'Integrated RIN (RMS) '])

# print(rin.head())
amsupression = 24
# plt.plot(rin.Frequency,rin.RIN,alpha = 0.5, label = f'RIN 17.5 mW')

plt.plot(rin.Frequency,rin.RIN-amsupression,alpha = 0.25, label = f'RIN 17.5 mW - {amsupression} dB')
plt.legend()

rin = pd.read_csv('RIN_7.5mW_100avg.csv',skiprows=7,sep=',', names=['Frequency','Mag^2 (V^2 / Hz)',' PSD (dBV^2 / Hz)','RIN',' Integrated Volts RMS', 'Integrated RIN (RMS) '])

# print(rin.head())
amsupression = 23
# plt.plot(rin.Frequency,rin.RIN,alpha = 0.5, label = f' RIN 7.5 mW ')
# plt.plot(rin.Frequency,rin.RIN-amsupression,alpha = 0.25, label = f'RIN 7.5 mW - {amsupression} dB')
plt.legend()
plt.savefig('Finisar vs. HHI with RIN.png')


