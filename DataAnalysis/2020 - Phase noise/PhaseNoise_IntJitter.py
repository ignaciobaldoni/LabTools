# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 13:20:24 2020

@author: ibaldoni
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from scipy import integrate, fft

def reset_my_index(df):
  res = df[::-1].reset_index(drop=True)
  return(res)

DATA = pd.read_csv('Data_for_python.csv',sep=';')

f_carrier = 10.1 * 1e9
f_new = 100 *1e6
f_scaling = 20*np.log10(f_carrier/f_new)

data = reset_my_index(DATA)

freq = data['Frequency']
noise = data['Raw_data']

noise = noise[375:] 
freq = freq[375:]

noise_linear = np.sqrt(2*(10**(noise/10)))  #Phase noise in radian**2/Hz

data['PN (rad/Hz)'] = noise_linear 

fig, ax1 = plt.subplots()
ax1.plot(freq, noise)
ax1.set_xscale('log')
ax1.set_ylabel('Phase noise (dBc/Hz)')
ax1.set_xlabel('Frequency (Hz)')
int_pn = np.abs(integrate.cumtrapz(noise_linear,np.log10(freq)))

ax2 = ax1.twinx()  
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.plot(freq[1:],np.sqrt(int_pn)*1e3,'r')
ax2.set_ylabel('Integrated PN (mrad)')