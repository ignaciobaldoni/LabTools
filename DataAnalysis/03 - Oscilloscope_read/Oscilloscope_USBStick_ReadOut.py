# -*- coding: utf-8 -*-
"""
Created on Wed May 13 10:44:38 2020

@author: ibaldoni
"""


import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

plt.rc('xtick', labelsize=17) 
plt.rc('ytick', labelsize=17) 
plt.rcParams.update({'font.size': 17})
plt.rcParams['figure.figsize'] = (14, 10)

import pandas as pd
from scipy.interpolate import interp1d



# Parameters for the analysis
center_frequency    = 194e12 #[Hz]
time_frequency      = 1/center_frequency
Delay               = 5e-12 #[ps]

calibration = False
calibration_center_frequency = False
calibration_delay = [True if calibration_center_frequency == False else False] 

plot_oscilloscope               = True
plot_oscilloscope_calibrated    = True


ignore_warnings = True



## Star the code
if ignore_warnings == True:
    import warnings
    warnings.filterwarnings("ignore")

import os
directory_data = os.getcwd()+'\\raw data'  
path, dirs, files = next(os.walk(directory_data))

exceptions_in = ['SC_77mW_5ps_EDFA300.csv']

p = 0
for i in files[:]:
    if all((ele_in in i) for ele_in in exceptions_in):

        print(i)
        med=pd.read_csv(directory_data +'/' + i)
        
        med=med.drop(med.index[0])  
        med = med.rename(columns={"x-axis":"time", "1":"delay", "2":"AK"})
        
        t = med.time
        t = t.astype(float)
        delay = med.delay
        delay = delay.astype(float)
        AK = med.AK
        AK = AK.astype(float)
        
        
        # Plot the file
        if plot_oscilloscope == True:
            plt.figure()
            plt.plot(t,delay,label = 'Channel 1')
            plt.plot(t,AK,'-',label = 'Autocorrelation')
            plt.xlabel('Time [s]')
            plt.ylabel('Voltage [V]')
            plt.grid()
            plt.legend()
            
            
        if calibration == True:
        
            if calibration_center_frequency == True:
                Label = 'Calibration with center frequency'
                print(Label)
                
                Height = 0.98*np.max(AK)
                
                peaks, _ = find_peaks(AK, height=1,distance=1)
                            
                index = np.where(AK== np.max(AK))[0][0]

                
                n = index+1
                while (AK[n]-AK[n+1])>0:
                    n+=1
                m = n+1    
                while (AK[m]-AK[m+1])<0:
                    m+=1
                
                # print(m-index)
                x = [t[index],t[m]]
                y = [0,time_frequency]
                
            elif calibration_delay == True:
                Label = 'Calibration with delay'
                print(Label)
                x = [0,len(AK)]
                y = [0,Delay]
                
            
    
    
            time_calibration = interp1d(x, y,fill_value='extrapolate')
            
            if plot_oscilloscope_calibrated == True:
                plt.figure()
                plt.plot(1E12*time_calibration(t),AK)
                plt.xlabel('Time [ps]')
                plt.ylabel('Voltage [V]')
                plt.title(Label)
                plt.grid()