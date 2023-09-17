# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 13:06:36 2015

@author: Michele
"""

import numpy as np 
import matplotlib.mlab as mplm
import matplotlib.pyplot as plt
import sys
import pandas as pd
sys.path.append('./')


fs = 10 #sampling in Hz
channel=4

beat = np.genfromtxt('C:/Users/ssaintjalm/Desktop/phase_test/211023_1_Frequ.txt') # Frequency trace from FXE counter
N=len(beat[:,1])
start,stop = 0,N
time = np.arange(N)/fs
beat_a0 = beat[start:stop,channel+2]  

beat_norm=beat_a0/194e12
fffluctu=mplm.csd(beat_norm, beat_norm, Fs=fs,detrend='mean',scale_by_freq='True',NFFT=2**18) # result in 1/Hz
sqrtfflu=np.sqrt(fffluctu[0].real*194e12**2) # conversion to Hz²/Hz then Hz/sqrt(Hz)
ffreq = fffluctu[1] # Fourier frequencies

#############################

# CXA data
cxassb = pd.read_csv('C:/Users/ssaintjalm/Desktop/phase_test/Trace_0001.csv',skiprows=53)
fcxa=np.array(cxassb.iloc[:,0])
ssbcxa=np.array(cxassb.iloc[:,1])
fflucxa=np.sqrt((fcxa**2)*10**((ssbcxa+3)/10))  # conversion from dBc/Hz to Hz/sqrt(Hz)

# Phase station data
PSssb = pd.read_csv('C:/Users/ssaintjalm/Desktop/phase_test/phase_station.csv',skiprows=53)
fPS=np.array(PSssb.iloc[:,0])
ssbPS=np.array(PSssb.iloc[:,1])
ffluPS=np.sqrt((fPS**2)*10**((ssbPS+3)/10))  # conversion from dBc/Hz to Hz/sqrt(Hz)

# Requirements
freqreq1=[1e-4,1e-3,1e-2,1e-1,1]
req1=[1e4,1e2,30,30,30]
freqreq2=[1,10,100,1000,1e4,1e5,1e6]
req2=[3e4,3e3,3e2,3e1,5,4,4]

#### Frequency trace plot

fig1 = plt.figure(figsize=(15, 12))
ax = fig1.add_subplot(1, 1, 1)
plt.rc('font', family='calibri')
ax.set_xlabel('Time (ms)')
ax.set_ylabel('Frequency (Hz)')
pn1 = plt.plot(time,beat_a0, 'r', label=r"Optical beat")

for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
              ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(19)

plt.legend(loc='lower left',numpoints=1,frameon=True, fontsize=16)
plt.grid(True)


#### Frequency fluctuation plot

fig7 = plt.figure(figsize=(15, 12))
ax = fig7.add_subplot(1, 1, 1)

plt.rc('font', family='calibri')
ax.set_xlabel('Fourier frequency (Hz)')
ax.set_ylabel(r'Frequency fluctuation (Hz/sqrt(Hz))')

time_cst=int(1/fs*1000)
pn1, = plt.loglog(ffreq,sqrtfflu,label="FXE %i ms data" %time_cst)
pn2, = plt.loglog(fcxa,fflucxa, 'green', label="CXA")
pn3 = plt.loglog(fPS,ffluPS, 'orangered', label="Phase Station")
pn4 = plt.loglog(freqreq1,req1, 'black', label="Requirement")
pn5 = plt.loglog(freqreq2,req2, 'black')


for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
             ax.get_xticklabels() + ax.get_yticklabels()):
    item.set_fontsize(20)

plt.legend(loc='upper right',numpoints=1,frameon=True, fontsize=20)
plt.grid(which = 'both')

#plt.savefig('psds.png', bbox_inches='tight')


