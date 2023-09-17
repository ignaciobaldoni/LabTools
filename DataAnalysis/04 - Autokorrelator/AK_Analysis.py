# -*- coding: utf-8 -*-
"""
Created on Wed May 13 10:44:38 2020

@author: ibaldoni
"""


import numpy as np
from scipy.signal import find_peaks, peak_widths
import matplotlib.pyplot as plt

plt.rc('xtick', labelsize=17) 
plt.rc('ytick', labelsize=17) 
plt.rcParams.update({'font.size': 17})
plt.rcParams['figure.figsize'] = (14, 10)

import pandas as pd
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit


# Parameters for the analysis
center_frequency    = 194e12 #[Hz]
time_frequency      = 1/center_frequency
Delay               = 5e-12 #[ps]
guess_duration      = 4850e-15
guess_coherence     = 1250e-15

calibration_center_frequency = True
calibration_delay = [True if calibration_center_frequency == False else False] 

plot_oscilloscope               = False
plot_oscilloscope_calibrated    = True

fit_gaussian    = True
fit_sech2       = False

CoherenceTime   = True

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
            plt.plot(t,delay,t,AK,'-o')
            plt.xlabel('Time [s]')
            plt.ylabel('Voltage [V]')
            plt.grid()
        
        if calibration_center_frequency == True:
            Label = 'Calibration with center frequency'
            print(Label)
            
            Height = 0.98*np.max(AK)
            
            peaks, _ = find_peaks(AK, height=1,distance=1)
            
            #plt.plot(t[peaks], AK[peaks], "o")
            
            index = np.where(AK== np.max(AK))[0][0]
            # print(index)
            # plt.plot(t[index+1],AK[index+1],'o')
            
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
        minimum = AK.iloc[0]

if fit_gaussian == True:
    def gaussian_AK(tau,deltaTau):
        return np.exp(-(2*np.log(2)*tau/deltaTau)**2)+minimum
    
    #plt.plot(1E12*time_calibration(t),gaussian_AK(time_calibration(t),guess_duration))
    popt, pcov = curve_fit(gaussian_AK, time_calibration(t), AK,p0=[guess_duration])
    Pulse_duration = np.round(popt[0]/1.41*1e12,4)
    plt.plot(1E12*time_calibration(t), gaussian_AK(time_calibration(t),*popt), 'r--',label = 'Pulse duration = %s ps'%Pulse_duration)
    plt.legend()

if fit_sech2 == True:

    def sinh(x):
        return (np.exp(x)-np.exp(-x))/2
    def coth(x):
        return (np.exp(x)+np.exp(-x))/(np.exp(x)-np.exp(-x))
    
    def sech2_AK(tau,deltaTau):
        return minimum + 3/((sinh(2.7196*tau/deltaTau))**2)*(2.7196*tau/deltaTau*coth(2.7196*tau/deltaTau)-1)
    
    popt2, pcov2 = curve_fit(sech2_AK, time_calibration(t), AK,p0=[guess_duration])
    plt.plot(1E12*time_calibration(t), sech2_AK(time_calibration(t),*popt2), 'k--')



if CoherenceTime == True:
    
    def lorentzian(tau, a, gam ):
        x0 = 0
        return a * gam**2 / ( gam**2 + (tau - x0 )**2)+minimum
    
    
        
    peaks2, _ = find_peaks(AK, prominence=0.15)
    
    # plt.figure()
    # plt.plot(time_calibration(t)*1e12,AK)
    # plt.plot(time_calibration(t[peaks2])*1e12,AK[peaks2],'o')
    
    sigma = np.ones(len(AK))
    
    

    sigma[peaks2]= 0.015
    sigma[index] = 0.001
    
    popt3, pcov3 = curve_fit(lorentzian, time_calibration(t), AK,p0=[8,guess_coherence],sigma = sigma)
    coherence_time = np.round(popt3[1]*1e12,4)
    plt.plot(time_calibration(t)*1e12,lorentzian(time_calibration(t),*popt3), '--',label = 'Coherence time ~ %s ps'%coherence_time)
    plt.legend()






# def sech2_AK(tau,deltaTau):
#     return 0

# Tt = np.linspace(-1e-12,1e-12,10000)
# tau = 0.5e-12 #[s]
# duration = 100e-15 #[s]

# def gaussian(x, mu, sig):
#     return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))


# def AK_Field(tau):
           
    
#     E = np.exp(1j*center_frequency*Tt)*gaussian(Tt,0,duration)
#     E_delay = np.exp(1j*center_frequency*Tt)*gaussian(Tt,tau,duration)
    
#     return (E**2+E_delay**2+2*E*E_delay)




# # E = np.exp(1j*center_frequency*Tt)*gaussian(Tt,0,0.125e-12)
# # E_delay = np.exp(1j*center_frequency*Tt)*gaussian(Tt,tau,0.125e-12)

# # # plt.plot(AK_Field(tau),label='AK')
# # plt.plot(E,label='E')
# # plt.plot(E_delay,label='E delay')
# # plt.legend()



# delay = 0.5e-12
# tau = np.linspace(-delay,delay,5000)

# AK2 = np.zeros(5000)

# for i in range(0,5000):
#     AK2[i] = 1e12*np.trapz(AK_Field(tau[i])*np.conj(AK_Field(tau[i])),Tt)

# plt.figure()
# plt.plot(tau*1e12,AK2*0.5)
# plt.xlabel('Delay [ps]')
# plt.ylabel('(a.u)')




# plt.plot(tau*1e12,gaussian_AK(tau,250e-15))






# # plt.figure()        
# # plt.plot(AK2)

# # tau = 0.5e-12
# # E = 2*np.exp(1j*center_frequency*Tt)
# # E_delay = 2*np.exp(1j*center_frequency*(Tt+tau))

# # plt.plot(Tt,E_delay)
# # plt.plot(Tt,E)


        

        
        
    