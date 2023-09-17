
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 20:59:49 2023

@author: Benjamin Rauf

The code takes the data obtained in the optical domain and calculates how the 
noise would be in the microwave domain. It also integrates the phase noise.
"""

from __future__ import division
import numpy as np
import pandas as pd
import scipy.constants as c
import matplotlib.pyplot as plt
#

plt.rcParams['figure.figsize'] = 6.18, 3.81

#Set filename, column number, sample time, wavelength, beginning and end of Data
#measurement time

#choose Data: All Data is starting with 0
anfang = 0
ende = 39770
#set file name and column number starting from 0
columnno = 0
columno2 = 1
filename = 'Trace_0002.csv'

#load Data
a = np.loadtxt(filename, dtype=float, comments='#', delimiter=',', converters=None, skiprows=61, usecols=(columnno, columno2), unpack=False, ndmin=0)
c = pd.DataFrame(a)

#convert back to array
Dataf = c.to_numpy()

#select Data
Data = Dataf[anfang:ende, :]




#The rows for time and frequency data
Freq = Data.T[0]
ROW = Data.T[1]
lc = len(ROW)
#linearisation of data
lina = np.divide(ROW,10)
lin = 2*np.power(10, lina)
linaa = lin
#calculate integrated phasenoise
pn = np.trapz(lin, Freq)
pn1 = (pn**(1/2))*1000


fa =  Freq[anfang]
fe =  Freq[lc-1]
print('Integrated Phase Noise: ' f"{pn1:.5}" ' mrad ' 'from : ' f"{fa:.5}" ' Hz '  'to: ' f"{fe:.5}" ' Hz AS_IS')

filename = 'Trace_0003.csv'
a = np.loadtxt(filename, dtype=float, comments='#', delimiter=',', converters=None, skiprows=61, usecols=(columnno, columno2), unpack=False, ndmin=0)
c = pd.DataFrame(a)
Dataf = c.to_numpy()
Data = Dataf[anfang:ende, :]
Freqb = Data.T[0]
ROWb = Data.T[1]
lc = len(ROWb)
lina = np.divide(ROWb,10)
lin = 2*np.power(10, lina)
pn = np.trapz(lin, Freqb)
pn1 = (pn**(1/2))*1000
fa =  Freqb[anfang]
fe =  Freqb[lc-1]
print('Integrated Phase Noise: ' f"{pn1:.5}" ' mrad ' 'from : ' f"{fa:.5}" ' Hz '  'to: ' f"{fe:.5}" ' Hz  DCDC')

ROWa = 10*np.log10((10E9/192.1E12)**2)+ROW
ROWab =10*np.log10((10E9/192.1E12)**2)+ROWb
ROWda = (linaa+lin)/2
ROWd = 10*np.log10((10E9/194.4E12)**2)+10*np.log10(ROWda/1)

Freqc=[1,10,100,1E3,1E4,1E5,1E6]
ROWc=[-85,-110,-130,-140,-160,-160,-160]


filename = 'Trace_0000.csv'
a = np.loadtxt(filename, dtype=float, comments='#', delimiter=',', converters=None, skiprows=61, usecols=(columnno, columno2), unpack=False, ndmin=0)
c = pd.DataFrame(a)
Dataf = c.to_numpy()
Data = Dataf[anfang:ende, :]
FreqM = Data.T[0]
ROWM = Data.T[1]

fig1,ax = plt.subplots()
plt.plot(Freq, ROWa, label='CW-conv.to optic', linewidth = 0.5)
plt.plot(Freqb, ROWab, label='CEO-conv-to optic', linewidth = 0.5)
plt.plot(Freqb, ROWd, label='CEO+CW conv to optic', linewidth = 0.5)
plt.plot(Freqc, ROWc, label='PSD of SSB PN high-end', linewidth = 0.5)
plt.plot(FreqM, ROWM, label='10MHz', linewidth = 0.5)
ax.set_xlabel('Frequency Offset [Hz]')
ax.set_xscale('log')
ax.set_ylim(-240, -80)
ax.set_ylabel('Phase Noise [dBc/Hz]')
plt.grid(which="both")
plt.legend()
plt.tight_layout()

plt.show()
