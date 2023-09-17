# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 13:27:18 2020
​
@author: ibaldoni
"""
​
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
​
from scipy.constants import speed_of_light
from scipy.fftpack import fft, fftshift, ifftshift
from scipy.signal import welch
​
​
#%% 
​
fileName = 'W0000'
plotSpan = 40;
yLimits = [-70,-8]
SkipRow = 29
​

​
fileFormat = '.csv'
​
pdData =pd.read_csv(fileName+fileFormat, 
                skiprows=SkipRow, 
                names=['wavelength','power'],
                dtype={
                       'wavelength': np.float64,
                       'power': np.float64
                       }
                )
# turn to numpy array
npData = pdData.to_numpy()
​
#plotParameter
Figsize = (10,4)
FontSize = 10
LabelSize = 10
LineWidth = 0.3
​
fig = plt.figure(figsize=Figsize)
​
plt.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)
plt.minorticks_on()
plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
​
plt.plot(
    npData[:,0],
    npData[:,1],
    '-',
    linewidth=LineWidth,
    label='Resonator')
​
plt.tick_params(labelsize=LabelSize)
plt.xlabel('Wavelength [nm]',fontsize=FontSize)
plt.ylabel('Power [dBm]',fontsize=FontSize)
​
maxElementIndex = np.argmax(npData, axis=0)
​
centerWavelength = npData[maxElementIndex[1],0]
​
​
plt.xlim(centerWavelength-plotSpan,centerWavelength+plotSpan)    
plt.ylim(yLimits)
​
​
# save figure
plt.savefig(fileName +'.pdf')
plt.savefig(fileName +'.png', dpi=900)
​
​
#plt.show()
# filter out pump data points
maxElementIndex = np.argmax(npData, axis=0)
centerWavelength = npData[maxElementIndex[1],0]
pumpwidth = 0.3
selectionMask = (npData[:,0] < centerWavelength-pumpwidth) | (npData[:,0] > centerWavelength+pumpwidth)
npData_noPump = npData[selectionMask]
​
# convert to watt figures
npData_noPump_pw = 10**(npData_noPump/10)
​
# convert frequencies axes
np_freqs = speed_of_light/(npData_noPump[:,0]*10**(-9));
​
fig2 = plt.figure(figsize=Figsize)
plt.plot(
    np_freqs,
    npData_noPump_pw[:,1],
    '-',
    linewidth=LineWidth,
    label='Resonator')
​
​
# create impulse shape figure
np_fftData = np.fft.fft(npData_noPump_pw[:,1])
fig1 = plt.figure(figsize=Figsize)
plt.plot(
    np_fftData,
    '-',
    linewidth=LineWidth,
    label='Resonator')
plt.show()