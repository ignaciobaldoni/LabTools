from __future__ import division
import numpy as np
import allantools
import pandas as pd
from scipy.optimize import curve_fit
import scipy.constants as c

import matplotlib.pyplot as plt
#
OADEV = 0
MADEV = 1
ADEV = 2

#Set filename, column number, sample time, wavelength, beginning and end of Data#
#and the limits of the (Modified) Allan Plot

#set calculation of stability to OADEV or MADEV or ADEV:
DEV = MADEV
#set sample time in seconds
t = 1.0
#set wavelength in meter #1542.14 1064 698.45
frequency = 10E9
Wavelength = 1542.14E-9
#choose Data: All Data is starting with 0
anfang = 21.3*3600#
ende = 62.2*3600#
#limits of the (Modified) Allan Plot
bottom = 1E-18
top = 1E-15
#set file name and column number starting from 0
columnno = 8
columnno2 = 9
columnno3 = 7
columnno4 = 10
filename = 'PhaseFreq_A_1_230616_19.txt'
#set Frequency data Axis
axdata = "mHz"#"mHz"#"Hz"
#show phasenosie limit 1E-18 in Phaseplot (1=yes)
limitpn = 1 #0#1


#####################################################

# sample rate in Hz of the input data
r = np.divide(1, t)
#optical frequency
f = frequency
fopt = np.divide(c.c, Wavelength)

#load Data
a = np.genfromtxt(filename, dtype=None, comments='#', delimiter=None, converters=None, usecols=(columnno), unpack=False,invalid_raise=False)
b = np.genfromtxt(filename, dtype=None, comments='#', delimiter=None, converters=None, usecols=(columnno2), unpack=False,invalid_raise=False)
c = b-a
c= pd.DataFrame(c)

u = np.genfromtxt(filename, dtype=None, comments='#', delimiter=None, converters=None, usecols=(columnno3), unpack=False,invalid_raise=False)
v = np.genfromtxt(filename, dtype=None, comments='#', delimiter=None, converters=None, usecols=(columnno4), unpack=False,invalid_raise=False)
copt = u-2*v
copt= pd.DataFrame(copt)


#create timestamps row
l = np.arange(len(c))
c.insert(loc=0, column='Time', value=np.divide(l, r))
copt.insert(loc=0, column='Time', value=np.divide(l, r))

#convert back to array
Dataf = c.to_numpy()
Datafo = copt.to_numpy()
#select Data
Data = Dataf[int(anfang):int(ende), :]
Dataopt = Datafo[int(anfang):int(ende), :]
#The rows for time and frequency data
TIME = Data.T[0]
TIMEk = TIME-TIME[0]
TIMEh = np.divide(TIMEk, 3600)
ROW = Data.T[1]
ROWopt = Dataopt.T[1]
lc = len(TIME)

plt.rcParams['figure.figsize'] = 6.18, 3.81
#plot frequency

fig1 = plt.figure(1)
if axdata == "mHz":
    plt.plot(TIMEh, ROW*1000, '.-', color='b', linewidth=0.2, markersize=0.2, alpha=0.35, label = "MW")
    plt.plot(TIMEh, (ROWopt*1000/fopt)*f, '.-', color='g', linewidth=0.2, markersize=0.2, alpha=0.35, label = "CC")
if axdata =="Hz":
    plt.plot(TIMEh, ROW, '.-', color='b', linewidth=0.1, markersize=0.2, alpha=0.35, label = "MW")
    plt.plot(TIMEh, (ROWopt/fopt)*f, '.-', color='b', linewidth=0.2, markersize=0.2, alpha=0.35, label = "CC")
plt.xlim(left=TIMEh[0])
plt.xlabel('Time [h]')
if axdata == "mHz":
    plt.ylabel('Frequency [mHz]')
else:
    plt.ylabel('Frequency [Hz]')        
plt.grid()
plt.legend()
plt.tight_layout()



#calculate Phase data of MW data

result_phi = []
erstwert = np.multiply(ROW[0], t)
result_phi.append(erstwert)
for i in range(1, lc):
    k = i-1
    phig = np.multiply(ROW[i], t)
    #phig = np.trapz(ROW[k:i], x=None, dx=t)
    addendum = result_phi[k]
    phires = np.add(addendum, phig)
    result_phi.append(phires)
#create Time and Phase array
lrp = np.arange(len(result_phi))
d = pd.DataFrame(result_phi)
d.insert(loc=0, column='Time', value=np.divide(lrp, r))
d2 = d.to_numpy()
#time and phase array
TIME2 = d2.T[0]
TIME2h = np.divide(TIME2, 3600)
ROW2 = d2.T[1]

#calculate Phase data of opt data

result_phiopt = []
erstwertopt = np.multiply(ROWopt[0], t)
result_phiopt.append(erstwertopt)
for i in range(1, lc):
    k = i-1
    phigopt = np.multiply(ROWopt[i], t)
    #phig = np.trapz(ROW[k:i], x=None, dx=t)
    addendumopt = result_phiopt[k]
    phiresopt = np.add(addendumopt, phigopt)
    result_phiopt.append(phiresopt)
#create Time and Phase array
lrp = np.arange(len(result_phiopt))
dopt = pd.DataFrame(result_phiopt)
dopt.insert(loc=0, column='Time', value=np.divide(lrp, r))
d2opt = dopt.to_numpy()
#time and phase array
TIME2 = d2opt.T[0]
TIME2h = np.divide(TIME2, 3600)
ROW2opt = d2opt.T[1]

#plot phase

fig2= plt.figure(2)
plt.plot(TIME2h, ROW2, '.-', color='b', linewidth=0.1, markersize=0.2, alpha=0.5, label = "MW")
plt.plot(TIME2h, (ROW2opt/fopt)*f, '.-', color='g', linewidth=0.1, markersize=0.2, alpha=0.5, label = "CC")
if limitpn == 1:
    plt.plot(TIME2h, f*r*1E-18*TIME2, '.-', color='r', linewidth=0.3, markersize=0.0, alpha=0.9, label = "1E-18")
    plt.plot(TIME2h, -f*r*1E-18*TIME2, '.-', color='r', linewidth=0.3, markersize=0.0, alpha=0.9)
    plt.plot(TIME2h, f*r*1E-19*TIME2, '.-', color='y', linewidth=0.3, markersize=0.0, alpha=0.9, label = "1E-19")
    plt.plot(TIME2h, -f*r*1E-19*TIME2, '.-', color='y', linewidth=0.3, markersize=0.0, alpha=0.9)
plt.xlim(left=TIME2h[0])
plt.xlabel('Time [h]')
plt.ylabel('Phase [cycles]')
plt.grid()
if limitpn == 1:
    plt.legend()
plt.tight_layout()


plt.show()
