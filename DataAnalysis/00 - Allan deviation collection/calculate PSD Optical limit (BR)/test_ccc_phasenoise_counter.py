from __future__ import division
import numpy as np
import allantools
import pandas as pd
import scipy.constants as c
import matplotlib.pyplot as plt
import scipy.signal
#
OADEV = 0
MADEV = 1
ADEV = 2

#Set filename, column number, sample time, wavelength, beginning and end of Data#
#and the limits of the (Modified) Allan Plot

#set calculation of stability to OADEV or MADEV or ADEV:
DEV = ADEV
#set sample time in seconds
t = 0.1
#set wavelength in meter #1542.14 1064 698.45
Wavelength = 1542.12E-9
#choose Data: All Data is starting with 0
anfang = 12*3600*10+19.76*3600*10#19.76*3600*10
ende = anfang+1*3600*10#51.62*3600*10#
#limits of the (Modified) Allan Plot
bottom = 1E-19
top = 1E-16
#set file name and column number starting from 0
columnno = 7
filename = '230401_1_Frequ.txt'
#set tau values in Allan-plot
ta = "decade"#"decade"#"all"
#set Frequency data Axis
axdata = "mHz"#"mHz"#"Hz"
#show phasenosie limit 1E-19 in Phaseplot (1=yes)
limitpn = 1 #0#1
#use accuracy intervals as in test procedure (0) or all (1)
intervals = 0 #1


#####################################################

# sample rate in Hz of the input data
r = np.divide(1, t)
#optical frequency
f = np.divide(c.c, Wavelength)

#load Data
a1 = np.genfromtxt('230331_1_Frequ.txt', dtype=float, comments='#', delimiter=None, converters=None, usecols=(columnno), unpack=False,invalid_raise=False)
a2 = np.genfromtxt('230401_1_Frequ.txt', dtype=float, comments='#', delimiter=None, converters=None, usecols=(columnno), unpack=False,invalid_raise=False)
a3 = np.genfromtxt('230402_1_Frequ.txt', dtype=float, comments='#', delimiter=None, converters=None, usecols=(columnno), unpack=False,invalid_raise=False)
a4 = np.genfromtxt('230403_1_Frequ.txt', dtype=float, comments='#', delimiter=None, converters=None, usecols=(columnno), unpack=False,invalid_raise=False)
an = np.append(a1,a2)
ann = np.append(an,a3)
annn = np.append(ann,a4)
a = annn
c = pd.DataFrame(a)


#create timestamps row
l = np.arange(len(c))
c.insert(loc=0, column='Time', value=np.divide(l, r))

#convert back to array
Dataf = c.to_numpy()

#select Data
Data = Dataf[int(anfang):int(ende), :]

#The rows for time and frequency data
TIME = Data.T[0]
TIMEk = TIME-TIME[0]
TIMEh = np.divide(TIMEk, 3600)
ROW = Data.T[1]

lc = len(TIME)

hunni = 1000*r
tausi = 10000*r

#
plt.rcParams['figure.figsize'] = 6.18, 3.81
#plot frequency

fig1 = plt.figure(1)
if axdata == "mHz":
    plt.plot(TIMEh, ROW*1000, '.-', color='b', linewidth=0.1, markersize=0.2, alpha=0.35)
if axdata =="Hz":
      plt.plot(TIMEh, ROW, '.-', color='b', linewidth=0.1, markersize=0.2, alpha=0.35)
plt.xlim(left=TIMEh[0])
plt.xlabel('Time [h]')
if axdata == "mHz":
    plt.ylabel('Frequency [mHz]')
else:
    plt.ylabel('Frequency [Hz]')        
plt.grid()
plt.tight_layout()

# if intervals == 0:
#     #set the random time intervals to calculate the accuracy at 100/1000s:
#     #100s intervals:
    
#     Accuracies100 = []
#     AbsAccuracies100 = []

#     if lc > hunni:

#         hunderts=int(r*100-1)
#         hunderts1=int(hunderts+1)

#         zweihunderts=int(r*200-1)
#         zweihunderts1=int(zweihunderts+1)

#         dreihunderts=int(r*300-1)

#         tauseinhs=int(r*1100-1)
#         tauseinhs0=int(r*1000)

#         ztauseinhs=int(r*2100-1)
#         ztauseinhs0=int(r*2000)

#         dtauseinhs=int(r*3100-1)
#         dtauseinhs0=int(r*3000)

#         vtauseinhs=int(r*4100-1)
#         vtauseinhs0=int(r*4000)

#         vtausdhs=int(r*4300-1)
#         vtausdhs0=int(r*4200)

#         vtausfhs=int(r*4500-1)
#         vtausfhs0=int(r*4400)

#         #calculation 100s intervals:

#         m1 = abs(np.mean(ROW[0:hunderts]))
#         mf1 = m1/f
#         Accuracies100.append(mf1)
#         AbsAccuracies100.append(m1)

#         m2 = abs(np.mean(ROW[hunderts1:zweihunderts]))
#         mf2 = m2/f
#         Accuracies100.append(mf2)
#         AbsAccuracies100.append(m2)

#         m3 = abs(np.mean(ROW[zweihunderts1:dreihunderts]))
#         mf3 = m3/f
#         Accuracies100.append(mf3)
#         AbsAccuracies100.append(m3)

#         m4 = abs(np.mean(ROW[tauseinhs0:tauseinhs]))
#         mf4 = m4/f
#         Accuracies100.append(mf4)
#         AbsAccuracies100.append(m4)

#         m5 = abs(np.mean(ROW[ztauseinhs0:ztauseinhs]))
#         mf5 = m5/f
#         Accuracies100.append(mf5)
#         AbsAccuracies100.append(m5)

#         m6 = abs(np.mean(ROW[dtauseinhs0:dtauseinhs]))
#         mf6 = m6/f
#         Accuracies100.append(mf6)
#         AbsAccuracies100.append(m6)

#         m7 = abs(np.mean(ROW[vtauseinhs0:vtauseinhs]))
#         mf7 = m7/f
#         Accuracies100.append(mf7)
#         AbsAccuracies100.append(m7)

#         m8 = abs(np.mean(ROW[vtausdhs0:vtausdhs]))
#         mf8 = m8/f
#         Accuracies100.append(mf8)
#         AbsAccuracies100.append(m8)

#         m9 = abs(np.mean(ROW[vtausfhs0:vtausfhs]))
#         mf9 = m9/f
#         Accuracies100.append(mf9)
#         AbsAccuracies100.append(m9)

#     else :
#         Accuracies100.append(0)
#         AbsAccuracies100.append(0)

#     #1000s intervals:
#     Accuracies1000 = []
#     AbsAccuracies1000 = []
        
#     if lc>tausi:
#         tauss=int(r*1000-1)
#         tauss0=int(r*0)

#         ztauss=int(r*2000-1)
#         ztauss0=int(r*1000)

#         dtauss=int(r*3000-1)
#         dtauss0=int(r*2000)

#         vtauss=int(r*4000-1)
#         vtauss0=int(r*3000)

#         ftauss=int(r*5000-1)
#         ftauss0=int(r*4000)

#         sstauss=int(r*6000-1)
#         sstauss0=int(r*5000)

#         stauss=int(r*7000-1)
#         stauss0=int(r*6000)

#         atauss=int(r*8000-1)
#         atauss0=int(r*7000)

#         ntauss=int(r*9000-1)
#         ntauss0=int(r*8000)

#         #calc 1000s intervals:

#         m100 = abs(np.mean(ROW[tauss0:tauss]))
#         mf100 = m100/f
#         Accuracies1000.append(mf100)
#         AbsAccuracies1000.append(m100)

#         m200 = abs(np.mean(ROW[ztauss0:ztauss]))
#         mf200 = m200/f
#         Accuracies1000.append(mf200)
#         AbsAccuracies1000.append(m200)

#         m300 = abs(np.mean(ROW[dtauss0:dtauss]))
#         mf300 = m300/f
#         Accuracies1000.append(mf300)
#         AbsAccuracies1000.append(m300)

#         m400 = abs(np.mean(ROW[vtauss0:vtauss]))
#         mf400 = m400/f
#         Accuracies1000.append(mf400)
#         AbsAccuracies1000.append(m400)

#         m500 = abs(np.mean(ROW[ftauss0:ftauss]))
#         mf500 = m500/f
#         Accuracies1000.append(mf500)
#         AbsAccuracies1000.append(m500)

#         m600 = abs(np.mean(ROW[sstauss0:sstauss]))
#         mf600 = m600/f
#         Accuracies1000.append(mf600)
#         AbsAccuracies1000.append(m600)

#         m700 = abs(np.mean(ROW[stauss0:stauss]))
#         mf700 = m700/f
#         Accuracies1000.append(mf700)
#         AbsAccuracies1000.append(m700)

#         m800 = abs(np.mean(ROW[atauss0:atauss]))
#         mf800 = m800/f
#         Accuracies1000.append(mf800)
#         AbsAccuracies1000.append(m800)

#         m900 = abs(np.mean(ROW[ntauss0:ntauss]))
#         mf900 = m900/f
#         Accuracies1000.append(mf900)
#         AbsAccuracies1000.append(m900)
        
#     else :
#         Accuracies1000.append(0)
#         AbsAccuracies1000.append(0)

#     ma100 = min(Accuracies100)
#     ma1000 = min(Accuracies1000)

#     maa100 = 1000*min(AbsAccuracies100)
#     maa1000 = 1000*min(AbsAccuracies1000)

# if intervals == 1:
#     #set the random time intervals to calculate the accuracy at 100/1000s:
#     #100s intervals:
#     hunni = 300*r
#     tausi = 3000*r
    
#     Accuracies100 = []
#     AbsAccuracies100 = []

#     if lc > hunni:

#         hundgrenze = int(np.round((lc-100*r), -3))
#         ROWac = ROW[0:hundgrenze]
#         noofl = hundgrenze/(100*r)
#         noofl = noofl.astype(int)
#         ROWacc = [ROWac[i:i + int(100*r)] for i in range(0, len(ROWac), int(100*r))]
#         for i in range(0,noofl):
#             Accuracies100.append((abs(np.mean(ROWacc[i])))/f)
#             AbsAccuracies100.append((abs(np.mean(ROWacc[i]))))

#     else :
#         Accuracies100.append(0)
#         AbsAccuracies100.append(0)

#     #1000s intervals:
#     Accuracies1000 = []
#     AbsAccuracies1000 = []

#     if lc>tausi:
        
#         tausgrenze = int(np.round((lc-1000*r), -4))
#         ROWacd = ROW[0:tausgrenze]
#         noofld = tausgrenze/(1000*r)
#         noofld = noofld.astype(int)
#         ROWaccd = [ROWacd[i:i + int(1000*r)] for i in range(0, len(ROWacd), int(1000*r))]
#         for i in range(0,noofld):
#             Accuracies1000.append(abs(((np.mean(ROWaccd[i])))/f))
#             AbsAccuracies1000.append((abs(np.mean(ROWaccd[i]))))
        
#     else :
#         Accuracies1000.append(0)
#         AbsAccuracies1000.append(0)

#     ma100 = min(Accuracies100)
#     #ma100 = np.sqrt((1/noofl)*np.sum(np.square(Accuracies100)))-(np.sqrt((1/noofl)*np.sum(np.square(Accuracies100)))/(4*noofl))
#     #ma1000 = np.sqrt((1/noofld)*np.sum(np.square(Accuracies1000)))-(np.sqrt((1/noofld)*np.sum(np.square(Accuracies1000)))/(4*noofld))
#     ma1000 = min (Accuracies1000)

#     maa100 = 1000*np.mean(AbsAccuracies100)
#     maa1000 = 1000*np.mean(AbsAccuracies1000)


#calculate Phase data

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

# #plot phase

# fig2= plt.figure(2)
# plt.plot(TIME2h, ROW2, '.-', color='b', linewidth=0.1, markersize=0.2, alpha=0.3)
# if limitpn == 1:
#     plt.plot(TIME2h, f*r*1E-19*TIME2, '.-', color='r', linewidth=0.3, markersize=0.0, alpha=0.9, label = "1E-19")
#     plt.plot(TIME2h, -f*r*1E-19*TIME2, '.-', color='r', linewidth=0.3, markersize=0.0, alpha=0.9)
# plt.xlim(left=TIME2h[0])
# plt.xlabel('Time [h]')
# plt.ylabel('Phase [cycles]')
# plt.grid()
# if limitpn == 1:
#     plt.legend()
# plt.tight_layout()


#create fractional frequency stability plot
ROWf = np.divide(ROW, f)

# tau values
t = TIME
# fractional frequency data
y = ROWf
# sample rate in Hz of the input data

# Compute the overlapping ADEV
if DEV == 0:
    (t2, ad, ade, adn) = allantools.oadev(y, rate=r, data_type="freq", taus=ta)
if DEV == 1:
    (t2, ad, ade, adn) = allantools.mdev(y, rate=r, data_type="freq", taus=ta)
if DEV == 2:
    (t2, ad, ade, adn) = allantools.adev(y, rate=r, data_type="freq", taus=ta)
(t2c, adc, adec, adnc) = allantools.adev(y, rate=r, data_type="freq", taus=ta)

#retrieve stabilities for 1s, 100s, 1000s
ad00 = pd.DataFrame(ad)
ad00.insert(loc=0, column='tau', value=t2)

eins = ad00[(ad00['tau'] == 1)]
ta1 = eins.to_numpy()
sigma1 = ta1[0][1]
sigmaa1m = f*1000*sigma1

if lc>hunni:
    hun = ad00[(ad00['tau'] == 100)]
    ta100 = hun.to_numpy()
    sigma100 = ta100[0][1]
    sigmaa100m = f*1000*sigma100
    
if lc>tausi:
    tausend = ad00[(ad00['tau'] == 1000)]
    ta1000 = tausend.to_numpy()
    sigma1000 = ta1000[0][1]
    sigmaa1000m = f*1000*sigma1000
#
try:
    #--------Confidence-intervals for each (tau,adev) pair separately.
    if DEV == 2:
       cis=[]
       for (t,dev,deverr) in zip(t2,ad,adn):
        edf = allantools.edf_greenhall( alpha=0, d=2, m=1, N=deverr, overlapping = False, modified=False )
        (low,high) = allantools.confidence_interval( dev=dev, ci=0.68268949213708585, edf=edf )
        cis.append( (low,high) )
     
       err_low = [ d-ci[0] for (d,ci) in zip(ad,cis)]
       err_high = [ ci[1]-d for (d,ci) in zip(ad,cis)]    
    #--------Confidence-intervals for each (tau,mdev) pair separately.
    if DEV == 1:
       cis=[]
       for (t,mdev,deverr) in zip(t2,ad,adnc):    
        edf = allantools.edf_greenhall( alpha=0, d=2, m=1, N=deverr, overlapping = False, modified=False )
        (low,high) = allantools.confidence_interval( dev=mdev, ci=0.68268949213708585, edf=edf )
        cis.append( (low,high) )
     
       err_low = [ d-ci[0] for (d,ci) in zip(ad,cis)]
       err_high = [ ci[1]-d for (d,ci) in zip(ad,cis)]   
     
    #--------Confidence-intervals for each (tau,oadev) pair separately.
    if DEV == 0:
       cis=[]
       for (t,odev,deverr) in zip(t2,ad,adn):
        edf = allantools.edf_greenhall( alpha=0, d=2, m=1, N=deverr, overlapping = False, modified=False )
        (low,high) = allantools.confidence_interval( dev=odev, ci=0.68268949213708585, edf=edf )
        cis.append( (low,high) )
     
       err_low = [ d-ci[0] for (d,ci) in zip(ad,cis)]
       err_high = [ ci[1]-d for (d,ci) in zip(ad,cis)]   
   
#estimate uncertainty of Allan Devaiation as standard uncertainty (1/sqrt(N))
except ZeroDivisionError:
    lcc=np.divide(lc, r)
    lca=np.divide(t2, lcc)
    lcs=np.sqrt(lca)
    err_low= 0.5*np.multiply(ad, lcs)
    err_high=err_low

#tau functions

def tau(x, A, B,x0):
    y = x0+A*np.power(x, B)
    return y

# Plot the Stability

#fig3 = plt.figure(3)
#plt.loglog(t2, ad, 'o-')
#plt.errorbar(t2,ad,yerr=aderror, linestyle='-', marker='s', label='MADEV')
#plt.errorbar(t2,ad,yerr=(err_low ,err_high), linestyle='-', marker='s', label='MADEV')
#plt.plot(t2, tau(t2, 5E-18, -1.5, 0), linestyle=':', color ='g', label='\u03c4 \u207b\u00b3\u2215\u00b2')
#plt.plot(t2, tau(t2, 5E-18, -0.5, 0), linestyle='--', color ='r', label='\u03c4 \u207b\u00bd')
#plt.ylim(bottom, top) #set ylim(bottom, top)
#plt.xlim(left=t2[0])
#plt.legend(loc='upper right',framealpha=1.0)
#plt.yscale('log')
#plt.xscale('log')
#plt.xlabel('Time [s]')
#if DEV == 0:
#    plt.ylabel('OADEV [fractional]')
#if DEV == 1:
#    plt.ylabel('MADEV [fractional]')
#if DEV == 2:
#    plt.ylabel('ADEV [fractional]')
#plt.grid()
#plt.grid(visible=True, which='both')
#plt.tight_layout()




# print('Fractional Frequency Stability at 1 second:',  f"{sigma1:.3}")
# if lc>hunni:
#     print('Fractional Frequency Stability at 100 seconds:',  f"{sigma100:.3}")
# if lc>tausi:
#     print('Fractional Frequency Stability at 1000 seconds:',  f"{sigma1000:.3}")
# if lc>hunni:
#     print('Relative Fractional Accuracy at 100 seconds:', f"{ma100:.3}", '±', f"{sigma100:.3}")
# if lc>tausi:
#     print('Relative Fractional Accuracy at 1000 seconds:', f"{ma1000:.3}", '±', f"{sigma1000:.3}")
# if lc>hunni:
#     print('Relative Accuracy at 100 seconds:', f"{maa100:.3}", '±', f"{sigmaa100m:.3}", 'mHz')
# if lc>tausi:
#     print('Relative Accuracy at 1000 seconds:', f"{maa1000:.3}", '±', f"{sigmaa1000m:.3}", 'mHz')
# #control value: sample mean
# samplemean = np.mean(ROW)
# samplemeanr = samplemean/f

# print('Sample Mean:',  f"{samplemean:.6}", f"{samplemeanr:.6}")

##calulate Phasenoise PSD of Counter Data
(fpsd, Spsd) = scipy.signal.periodogram(np.pi*2*ROW2, fs=r, window='boxcar', nfft=None, detrend='constant', return_onesided=True, scaling='density', axis=- 1)
#discard first value number
fpsd = np.flip(fpsd)
Spsd = np.flip(Spsd)
# #plot
# fig4= plt.figure(4)
# plt.loglog(fpsd, 2*Spsd)
# plt.xlabel('frequency [Hz]')
# plt.ylabel('PSD [rad**2/Hz]')
# plt.grid()
# plt.grid(visible=True, which='both')
# ##calculate integrated phasenoise
lin = 2*Spsd
pn = np.trapz(fpsd, lin)
pn1 = (pn)**(1/2)*1000
fe =  fpsd[0]
fa =  fpsd[len(fpsd)-1]
print('Integrated Phase Noise: ' f"{pn1:.5}" ' mrad ' 'from : ' f"{fa:.5}" ' Hz '  'to: ' f"{fe:.5}" ' Hz')
fpsdx = np.where(fpsd >=0.07)
fpsdx = fpsdx[0]
fpsda = np.where(fpsd >=1.0)
fpsda = fpsda[0]
fpsdaa = fpsda[-1]
fpsdxxx=fpsd[fpsdaa:fpsdx[-1]]
linxxx=lin[fpsdaa:fpsdx[-1]]
pnx = np.trapz(fpsdxxx, linxxx)
pn1x = (pnx)**(1/2)*1000
fex =  fpsd[fpsdaa]
fax =  fpsd[fpsdx[-1]]
print('Integrated Phase Noise: ' f"{pn1x:.5}" ' mrad ' 'from : ' f"{fax:.5}" ' Hz '  'to: ' f"{fex:.5}" ' Hz')

Spsdlog=10*np.log10(Spsd/1)
# fig7= plt.figure(7)
# plt.semilogx(fpsd,Spsdlog)
# plt.xlabel('frequency [Hz]')
# plt.ylabel('PSD [dBc/Hz]')
# plt.grid()
# plt.grid(visible=True, which='both')

#Calculate Allan deviation from PSD
FREQ = np.flip(fpsd)


l = len(FREQ)
fH = FREQ[l-1]

Sp = np.flip(Spsd)
Sy_ = []



for i in range (1, l):
    Syi = ((FREQ[i]/f)**2)*Sp[i]
    Sy_.append(Syi)

Syp = pd.DataFrame(Sy_)
Sy = Syp[0]

t = [0.1,0.2,0.4,1,2,4,10,20,40,100,200,400,1000,2000,4000,10000]
tl = len(t)
I_=[]
for j in range (0, tl):
    tau = t[j]    
    Integral_ = []
    if DEV ==2:
        gd = len(FREQ)
        FREQs = FREQ[1:gd]
        Int = np.trapz((2*(Sy*((np.sin(np.pi*FREQs*tau))**4)/((np.pi*FREQs*tau)**2))),FREQs)
        I_.append(Int)
    if DEV ==1:
        m = tau/0.001
        t0 = 0.001
        gd = len(FREQ)
        FREQs = FREQ[1:gd]
        Int = np.trapz(((2/(m**4))*(Sy*((np.sin(np.pi*FREQs*tau))**6)/(((np.pi*FREQs*t0)**2)*(np.sin(((np.pi*FREQs*t0))))**2))),FREQs)
        I_.append(Int)

sigma = np.sqrt(I_)
e = pd.DataFrame(sigma)
e.insert(loc=0, column='tau', value = t)
e2 = e.to_numpy()

taus = e2.T[0]
sigmas = e2.T[1]


fig5 = plt.figure(5)
if DEV ==2:
    plt.plot(taus, sigmas, linestyle='-', marker='s', label ='ADEV from PSD Data')
    plt.errorbar(t2,ad,yerr=(err_low ,err_high), linestyle='-', marker='s', label='ADEV',color='g')
if DEV ==1:
        plt.plot(taus, sigmas, linestyle='-', marker='s', label ='MADEV from PSD Data')
        plt.errorbar(t2,ad,yerr=(err_low ,err_high), linestyle='-', marker='s', label='MADEV',color='g')
plt.yscale('log')
plt.xscale('log')
plt.xlabel('Tau [s]')
if DEV ==2:
    plt.ylabel('ADEV [fractional]')
if DEV ==1:
    plt.ylabel('MADEV [fractional]')
plt.ylim(bottom, top) #set ylim(bottom, top)
plt.xlim(left=t2[0])
plt.grid()
plt.legend()
plt.grid(visible=True, which='both')
plt.tight_layout()


eins = e[(e['tau'] == 1)]
ta1 = eins.to_numpy()
sigma1 = ta1[0][1]

print('Fractional Frequency Stability at 1 second from Phase Data:',  f"{sigma1:.3}")
print('cutoff-frequency:',  f"{fH:.3}", 'Hz')

plt.show()


# #Set filename, column number, sample time, wavelength, beginning and end of Data
# #measurement time
# t = 0.1
# #choose Data: All Data is starting with 0
# anfang = 0
# ende = 39770
# #set file name and column number starting from 0
# columnno = 0
# columno2 = 1
# filename = 'pn1avg.csv'

# #load Data
# a = np.loadtxt(filename, dtype=float, comments='#', delimiter=',', converters=None, skiprows=61, usecols=(columnno, columno2), unpack=False, ndmin=0)
# c = pd.DataFrame(a)

# #convert back to array
# Dataf = c.to_numpy()

# #select Data
# Data = Dataf[anfang:ende, :]

# #lower cutoff-frequency
# it = 1/t

# #The rows for time and frequency data
# Freq = Data.T[0]
# ROW = Data.T[1]
# lc = len(ROW)
# #linearisation of data
# lina = np.divide(ROW,10)
# lin = 2*np.power(10, lina)
# #calculate integrated phasenoise
# pn = np.trapz(lin, Freq)
# pn1 = (pn**(1/2))*1000

# fa =  Freq[anfang]
# fe =  Freq[lc-1]
# #calculate betasline
# betasline = 8*np.log(2)/((np.pi)**2)*Freq
# #calculate PSD of frequency
# linfreq = lin*((Freq)**2)

# #calculate PSD above betasline
# PSDb = []
# lb = len(betasline)
# for i in range(0,lb):
#     if betasline[i] < linfreq[i]:
#         PSDb.append(linfreq[i])
#     else:
#             PSDb.append(0.0)

# #implement lower cutoff-frequency
# PSDbb = []
# Freqb = []
# for i in range(0,lc):
#     if Freq[i] >= it:
#         Freqb.append(Freq[i])
#         PSDbb.append(PSDb[i])
# #integrate area
# A = np.trapz(PSDbb,Freqb)
# #linewdith of laser
# FWHM = (A*8*np.log(2))**(1/2)


# # fig8,ax = plt.subplots()
# # ax.plot(fpsd,Spsdlog, label='Counter', linewidth = 0.5)
# # ax.plot(Freq, ROW, label='PSD', linewidth = 0.5)
# # ax.set_xlabel('Frequency Offset [Hz]')
# # ax.set_xscale('log')
# # ax.set_ylim(-140, -40)
# # ax.set_ylabel('Phase Noise [dBc/Hz]')
# # plt.grid(which="both")
# # plt.tight_layout()

# print('Integrated Phase Noise: ' f"{pn1:.5}" ' mrad ' 'from : ' f"{fa:.5}" ' Hz '  'to: ' f"{fe:.5}" ' Hz')

# m=20*np.log10(10E9/192.1E12)

# Freq1 = Freq
# ROW1 = ROW

# #choose Data: All Data is starting with 0
# anfang = 0
# ende = 39770
# #set file name and column number starting from 0
# columnno = 0
# columno2 = 1
# filename = 'Trace_0002.csv'

# #load Data
# a = np.loadtxt(filename, dtype=float, comments='#', delimiter=',', converters=None, skiprows=61, usecols=(columnno, columno2), unpack=False, ndmin=0)
# c = pd.DataFrame(a)

# #convert back to array
# Dataf = c.to_numpy()

# #select Data
# Data = Dataf[anfang:ende, :]



# #The rows for time and frequency data
# Freq = Data.T[0]
# ROW = Data.T[1]
# lc = len(ROW)
# #linearisation of data
# lina = np.divide(ROW,10)
# lin = 2*np.power(10, lina)
# linaa = lin
# #calculate integrated phasenoise
# pn = np.trapz(lin, Freq)
# pn1 = (pn**(1/2))*1000

# fa =  Freq[anfang]
# fe =  Freq[lc-1]


# # filename = 'Trace_0003.csv'
# # a = np.loadtxt(filename, dtype=float, comments='#', delimiter=',', converters=None, skiprows=61, usecols=(columnno, columno2), unpack=False, ndmin=0)
# # c = pd.DataFrame(a)
# # Dataf = c.to_numpy()
# # Data = Dataf[anfang:ende, :]
# # Freqb = Data.T[0]
# # ROWb = Data.T[1]
# # lc = len(ROWb)
# # lina = np.divide(ROWb,10)
# # lin = 2*np.power(10, lina)
# # pn = np.trapz(lin, Freqb)
# # pn1 = (pn**(1/2))*1000
# # fa =  Freqb[anfang]
# # fe =  Freqb[lc-1]


# # Freqc=[1,10,100,1E3,1E4,1E5,1E6]
# # ROWc=[-85,-110,-130,-140,-160,-160,-160]

# # ROWa = m+ROW
# # ROWab =m+ROWb
# # ROWda = (linaa+lin)/2
# # ROWd = 10*np.log10((10E9/194.4E12)**2)+10*np.log10(ROWda/1)


# # fig9,ax = plt.subplots()
# # ax.plot(fpsd,Spsdlog+m, label='Counter conv to optic', linewidth = 0.5)
# # ax.plot(Freqb, ROWd, label='CEO+CW conv to optic', linewidth = 0.5)
# # ax.plot(Freq1, ROW1+m, label='PSD conv to optic', linewidth = 0.5)
# # ax.plot(Freqc, ROWc, label='PSD of SSB PN high-end', linewidth = 0.5)
# # ax.set_xlabel('Frequency Offset [Hz]')
# # ax.set_xscale('log')
# # ax.set_ylim(-140, -40)
# # ax.set_ylabel('Phase Noise [dBc/Hz]')
# # plt.grid(which="both")
# # plt.tight_layout()




# # plt.show()
