from __future__ import division
import numpy as np
import pandas as pd
import scipy.constants as c
import matplotlib.pyplot as plt
#

plt.rcParams['figure.figsize'] = 6.18, 3.81

#Set filename, column number, sample time, wavelength, beginning and end of Data
#measurement time
t = 0.1
#choose Data: All Data is starting with 0
anfang = 0
ende = 39770
#set file name and column number starting from 0
columnno = 0
columno2 = 1
filename = 'pn1avg.csv'

#load Data
a = np.loadtxt(filename, dtype=float, comments='#', delimiter=',', converters=None, skiprows=61, usecols=(columnno, columno2), unpack=False, ndmin=0)
c = pd.DataFrame(a)

#convert back to array
Dataf = c.to_numpy()

#select Data
Data = Dataf[anfang:ende, :]

#lower cutoff-frequency
it = 1/t

#The rows for time and frequency data
Freq = Data.T[0]
ROW = Data.T[1]
lc = len(ROW)
print(ROW)
#linearisation of data
lina = np.divide(ROW,10)
lin = 2*np.power(10, lina)
#calculate integrated phasenoise
pn = np.trapz(lin, Freq)
pn1 = (pn**(1/2))*1000

fa =  Freq[anfang]
fe =  Freq[lc-1]
#calculate betasline
betasline = 8*np.log(2)/((np.pi)**2)*Freq
#calculate PSD of frequency
linfreq = lin*((Freq)**2)

#calculate PSD above betasline
PSDb = []
lb = len(betasline)
for i in range(0,lb):
    if betasline[i] < linfreq[i]:
        PSDb.append(linfreq[i])
    else:
            PSDb.append(0.0)

#implement lower cutoff-frequency
PSDbb = []
Freqb = []
for i in range(0,lc):
    if Freq[i] >= it:
        Freqb.append(Freq[i])
        PSDbb.append(PSDb[i])
#integrate area
A = np.trapz(PSDbb,Freqb)
#linewdith of laser
FWHM = (A*8*np.log(2))**(1/2)


fig1,ax = plt.subplots()
ax.plot(Freq, ROW, label='PSD', linewidth = 1.5)
ax.set_xlabel('Frequency Offset [Hz]')
ax.set_xscale('log')
# ax.set_ylim(-140, -40)
ax.set_ylabel('Phase Noise [dBc/Hz]')
plt.grid(which="both")
plt.tight_layout()

print('Integrated Phase Noise: ' f"{pn1:.5}" ' mrad ' 'from : ' f"{fa:.5}" ' Hz '  'to: ' f"{fe:.5}" ' Hz')

fig2,ax = plt.subplots()
ax.plot(Freq, PSDb, label='PSDbetas', linewidth = 1.5)
ax.plot(Freq, linfreq, label='PSD', linewidth = 1.5)
ax.plot(Freq, betasline, label='betasline', linewidth = 1.5)
ax.set_xlabel('Frequency Offset [Hz]')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_ylabel('PSD [Hz^2/Hz]')
plt.grid(which="both")
plt.legend()
plt.tight_layout()

print('FWHM: ' f"{FWHM:.5}" ' Hz ')

plt.show()
