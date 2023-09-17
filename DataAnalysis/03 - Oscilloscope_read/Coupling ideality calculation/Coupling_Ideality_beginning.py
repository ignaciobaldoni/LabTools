# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 17:18:11 2020

@author: ibaldoni
"""

'''
Coupling ideality:

The ratio of the power coupled from the resonator to the fundamental fiber mode
divided by the total power coupled to all guided and nonguided fiber modes

ko:     internal loss rate                                  ------> Constant
kex_0:  Coupling rate to the fundamental waveguide mode     ------> Varying
k/2pi:  Total linewidth
kp:     Parasitic coupling losses
I:      Coupling ideality           I=1 (ideal)     I<1 (Non ideal)
K:      Coupling parameter        
D1/2pi: FSR    
P:      Intracavity power
P_in:   Power input
'''
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks, peak_widths
#from numpy import trapz
#from scipy import integrate
#
#from scipy.misc import electrocardiogram
#from scipy.signal import find_peaks, argrelextrema
#from scipy.optimize import curve_fit
#from scipy import interpolate

size=(10,7)
c=299789452

general = '\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
interes = '20200424_Coupling_ideality_measures'

p=0

wavelength=[1565,1558,1552,1547,1542,1533,1527,1520]
depth = np.zeros(len(wavelength))
for jj in range(7,15):
    p=p+1
    med=pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                     +str(interes)+'\\scope_'+str(jj)+'.csv')
    med=med.drop(med.index[-1])
    med=med.drop(med.index[0])    
    
    t=med['x-axis']
    t = t.astype(float)
    
    res = med['1'].rolling(50).mean()
    res = res.astype(float)
    res = res/np.max(res)
    
#    laser = med['2'].rolling(50).mean()
#    laser = med['2'].astype(float)
#    laser = laser/np.max(laser)
#    
#    res_edit = res - 0.025*laser
    
    maximo = np.max(res)
    minimo = np.min(res)
    
    maximo_ind = np.min(np.where(res==maximo))
    minimo_ind = np.min(np.where(res==minimo))
    avg = np.mean(res)
    
    wl = wavelength[p-1]
    depth[p-1] = np.round(maximo - minimo,4)
    
    print('Wavelength = %s nm; depth = %s' % (wl, depth[p-1]))
    

    plt.figure(p)
    plt.plot(t,res)
    plt.hlines(avg,t.iloc[0],t.iloc[-1])
    plt.plot(t[minimo_ind],minimo,'rx')
    plt.plot(t[maximo_ind],maximo,'rx')
    plt.title('Wavelength = %s nm' % wl)
    
plt.figure(p+1)
plt.plot(wavelength,depth,'o')

    
    



#p=0
#wavelength=[1520,1530,1540,1520,1550,1560,1565]
#depth = np.zeros(len(wavelength))
#for jj in range(0,6):
#
#    p=p+1
#    med=pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
#                     +str(interes)+'\\scope_'+str(jj)+'.csv')
#    med=med.drop(med.index[-1])
#    med=med.drop(med.index[0])    
#    
#    t=med['x-axis']
#    t = t.astype(float)
#    
#    res = med['1'].rolling(50).mean()
#    res = res.astype(float)
#    res = res/np.max(res)
#    
##    laser = med['2'].rolling(50).mean()
##    laser = med['2'].astype(float)
##    laser = laser/np.max(laser)
##    
##    res_edit = res - 0.025*laser
#    
#    maximo = np.max(res)
#    minimo = np.min(res)
#    
#    maximo_ind = np.min(np.where(res==maximo))
#    minimo_ind = np.min(np.where(res==minimo))
#    avg = np.mean(res)
#    
#    wl = wavelength[p-1]
#    depth[p-1] = np.round(avg - minimo,4)
#    
#    print('Wavelength = %s nm; depth = %s' % (wl, depth[p-1]))
#    
#
#    plt.figure(p)
#    plt.plot(t,res)
#    plt.hlines(avg,t.iloc[0],t.iloc[-1])
#    plt.plot(t[minimo_ind],minimo,'rx')
#    plt.plot(t[maximo_ind],maximo,'rx')
#    plt.text(t.iloc[0],0.9,str(wl)+'nm')
#    
#plt.figure(p+1)
#plt.plot(wavelength,depth,'o')


























##ko = 1
##k_rad = 5
##kex_HOM = 5
##kp = k_rad + kex_HOM
#
#kp = 0.21
#ko = 0.0277312438994677
#
#P_in = 1
#FSR = 12E12
#kex_0 = np.linspace(ko,30,5000) 
#I = kex_0/(kex_0 + kp)
#K = kex_0/ko
#T = np.abs( 1 - (2/( K**(-1) + I**(-1) )))**2 
#P = P_in * FSR * (4/(kex_0*(K**(-1)+I**(-1))**2))
#P_graph = P/np.max(P[1:])
#T_graph = T/np.max(T[1:])
#
#
#log_kx = np.log10(kex_0)
#plt.plot(log_kx,T_graph,label = 'T')
#plt.plot(log_kx,P_graph,label = 'P')
#plt.legend()
#
##
##  
##k = 2*np.pi*total_linewidth 
#
##
##K = kex_0/ko
##K = k/ko - 1
##
#
###
##k = (ko + kex_0)/I