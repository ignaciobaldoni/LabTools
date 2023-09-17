# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 17:56:39 2020

@author: ibaldoni
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numpy import trapz
from scipy import integrate

from scipy.misc import electrocardiogram
from scipy.signal import find_peaks, peak_widths
from scipy.optimize import curve_fit
#from scipy import optimize

size=(18,14)
c = 299789452
lambda_laser = 1542.142

calculo_cwlaser = 'off'
plot_combs = 'off'
peak_finding = 'off'
circa_sech2 = 'on'

resolution_OSA = 0.015

general = '\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
interes = '20200124_Fundamental_Soliton_Vielleicht\\'#'20200312_Thermal_Locking_Test\\'

for jj in range(7,8):  

    
    data=pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                     +str(interes)+'W000'+str(jj)+'.csv')
    data.columns = ["x", "signal"]

    
    data['f']=c/(data.x*1e-9)
    
    if plot_combs == 'on':
        plt.figure(jj+1, figsize=size)
        plt.plot(data.x,data.signal,linewidth=2)
        plt.xlabel('Wavelength (nm)',fontsize=27)
        plt.ylabel('Power (dBm/nm)',fontsize=27)
        plt.grid()
    #    plt.axvline(x=1542.6,color='r', linestyle='--',linewidth=0.7)
        plt.yticks(fontsize=25, rotation=0)
        plt.xticks(fontsize=25, rotation=0)
        plt.ylim(-80,-5)
    #    plt.title('Freq = %s MHz, EDFA = %s mA, Signal Gen = %s dBm'% (Variacion,EDFA, Sig_gen), fontsize=20)
        t=data.x
        
        plt.savefig(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                            +str(interes)+'OSA_'
                            +str(jj)+'.png')
#    
# Linear approach for calculating CW contribution
    if calculo_cwlaser == 'on':
        t=data.x  
        db = data['signal']
        lin = 10**(db/10)
        
        
        total=trapz(lin,t)
        print(total,'mW')   
    
        ini=1540
        fin=1544
            
        Fin=min(data.x, key=lambda x:abs(x-fin))
        Ini=min(data.x, key=lambda x:abs(x-ini))
        
        manola=np.where(data.t==Fin)
        Manola=manola[0].item()
        hola=np.where(data.t==Ini)
        Hola=hola[0].item()
        
        CW_Laser=lin[Hola:Manola]
        t_laser=t[Hola:Manola]
        laser=np.trapz(CW_Laser,t_laser)
        pge= np.round(laser/total*100,2)
        print(laser,'mW')
        print(pge,'%')
        print('------------------------------------------------')
        
        plt.plot(t,lin)
        plt.plot(t_laser,CW_Laser)
        plt.show()
        plt.savefig(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                            +str(interes)+'CW_Calculation_'
                            +str(jj)+'.png')
        plt.close()  
        
        
    if circa_sech2 == 'on':
        t = data.x
        peaks, _ = find_peaks(data.signal, distance=80)
        xx = data.signal       
        plt.plot(xx[peaks])
        
        def sech(x):
            return 1/np.cosh(x)
    
        def sech2(eje_x, a,b,c,d ):
            return a*np.log10((sech(b*(eje_x-c)))) + d              

        A = 0
        B = 1
        C = 1542
        D = -30
                    
        popt_sech2, pcov_sech2 = curve_fit(sech2, t[peaks], xx[peaks], p0=[A, B, C, D],maxfev=2000)
        
#        plt.plot(t[peaks], xx[peaks], "x")
        
        peaks, _ = find_peaks(sech2(t, *popt_sech2))
        results_half = peak_widths(sech2(t, *popt_sech2), peaks, rel_height = .5)
        
        Width = resolution_OSA*results_half[0]       
        
        
        bandwidth = c*(Width[0]*1e-9)/((lambda_laser*1e-9)**2)*1e-12
        print('Soliton bandwidth = %s THz'% bandwidth)
        
        ZZ = sech2(t, *popt_sech2)
        plt.plot(ZZ)
#        plt.plot(peaks, ZZ[peaks], "x")
        plt.hlines(*results_half[1:], color="C2")
        plt.show()
        


        plt.figure(figsize=size)
        plt.plot(data.x,data.signal,linewidth=2)
        plt.xlabel('Wavelength (nm)',fontsize=27)
        plt.ylabel('Power (dBm)',fontsize=27)
        plt.text(1500, -37,'~sech2(x)', fontsize=23)
        plt.grid()
        plt.yticks(fontsize=25, rotation=0)
        plt.xticks(fontsize=25, rotation=0)
        plt.ylim(-80,-5)
        plt.plot(t, sech2(t, *popt_sech2),linewidth=2.5)
        


        