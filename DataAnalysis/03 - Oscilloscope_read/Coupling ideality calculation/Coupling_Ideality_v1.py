# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 17:28:24 2020

@author: ibaldoni
"""

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
interes = '20200429_First_attempts_of_automation'

p=0

wavelength=np.linspace(1520,1570,11)
depth = np.zeros(len(wavelength))
for jj in wavelength:
    print(jj)
    p=p+1
    med=pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                     +str(interes)+'\\Data_'+str(int(jj))+'_GAP_0.7.csv')
    
    med=med.drop('Unnamed: 0',axis=1)
    med = med.rename(columns={"0":"transmission"})

    
#    t=med['x-axis']
#    t = t.astype(float)
    
    res = med['transmission'].rolling(10).mean()
    res = res.astype(float)
    
#    'Normalize'
#    res = -res/np.min(res)
    
    indice = res.index

    
    maximo = np.max(res)
    minimo = np.min(res)
    
    maximo_ind = np.min(np.where(res==maximo))
    minimo_ind = np.min(np.where(res==minimo))
    avg = np.mean(res)
    invento = (maximo+avg)*0.5
    
    wl = wavelength[p-1]
    
    if np.abs(maximo - minimo) > 0.05:            
        depth[p-1] = np.round(invento - minimo,4)
        plt.figure(p)
        plt.title('Wavelength = %s nm'%jj)
        plt.plot(res,'o-')
    #    plt.plot(t,res)
        plt.hlines(avg,res.index[0],res.index[-1],'g')
        plt.hlines(invento,res.index[0],res.index[-1],'m')
        plt.plot(minimo_ind,minimo,'rx')
        plt.plot(maximo_ind,maximo,'rx')
    
    else:
        depth[p-1] = 0
        print('No resonances on sight')
    
    print('Wavelength = %s nm; depth = %s' % (wl, depth[p-1]))
    

    
    
plt.figure(p+1)
plt.plot(wavelength,depth,'o')
