# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 13:47:20 2020

@author: ibaldoni
"""

'''
Q factor calculation using our setup for chip packaging

Método berreta haciendo un análisis de las resonancias sin ajuste. Mirando donde 
intersecan con el FHWM. 
'''


print('CUIDADO!! Metodo de calculo berreta')

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
interes = '20200324_Chip_alignment_setup__Q_factor_calculation'

wl = 1542.142*1e-9  # Wavelength in m
#1550*1e-9  

FSR = 12

plots = 'n'
PRUEBA = 'n'

myPath = str(general) + str(interes) 
print(myPath)
            
def freq(x):
    return c/(x*1e-9)*(1e-12)         

p=0

Quality_factor  =   pd.Series()
Losses          =   pd.Series()
for jj in range(29,43):
    p=p+1
    med=pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                     +str(interes)+'\\scope_'+str(jj)+'.csv')
    
    med=med.drop(med.index[0])    
    t=med['x-axis']
    t = t.astype(float)
    res=med['1'].rolling(50).mean()
    res=res.astype(float)
    
    nuevo_t     = pd.Series()
    nuevo_res   = pd.Series()

    for i in range(1,len(res)-2):
        if ((res.iloc[i] < res.iloc[i-1]) 
            and (res.iloc[i] > res.iloc[i+1])
            and (res.iloc[i] > res.iloc[i+2]) 
            and (res.iloc[i] < 0.99*np.mean(res))):
            valor = res.iloc[i]
            nuevo_res = nuevo_res.append(pd.Series([valor], index=[i]))
     
    nuevo_t = - nuevo_res + 10
    maxima = nuevo_t.idxmax()
    
    primer_coso = nuevo_t[0:250]
    ultimo_coso = nuevo_t[(len(nuevo_t)-200):len(nuevo_t)-1]
    
    maxima1 = primer_coso.idxmax()
    maxima2 = ultimo_coso.idxmax()
    
#    Full width at half maximum
    medio = np.mean(res)
    fwhm = 0.5*(medio + res[maxima])

    # Betweeen maxima1 y maxima2 there are 500 MHz
    
    minimo=1000
    for i in range(51,maxima):
        if abs(res[i]-fwhm)<minimo:
            index_izq = i
            minimo = abs(res[i]-fwhm)

    minimo=1000
    for i in range(maxima,len(res)):
        if abs(res[i]-fwhm)<minimo:
            index_der = i
            minimo = abs(res[i]-fwhm)
          
        
    # We define the new x axis according to the position of the sidebands
    
    fp = [0,250,500]
    xp = [t[maxima1],t[maxima],t[maxima2]]
    
    index_freq1     =   np.interp(t[index_izq], xp, fp)
    index_freq2     =   np.interp(t[index_der], xp, fp)
    
    res_width_freq  =   index_freq2-index_freq1
    
   

#    Quality factor calculated from bandwidth        
    
    
    
    
    c = 299792458   # Speed of light
    vo = c/wl
    
    Q = vo/(res_width_freq*1E6)     
    
    
#       Quality factor calculated according to losses that I am not sure
    Res_freq =  FSR*1e9     # Frequency of the chip
    T_rt = 1/Res_freq       # Roundtrip time 

#    Finess
#    F = Res_freq/(Width*1e6)
    
##    But I can calculate the losses according to my previous analysis of the Q
    losses = (vo*T_rt) * 2*np.pi/Q
    
    Q_plot = np.round(Q,4)
    Width = np.round(res_width_freq,2)


    Quality_factor = Quality_factor.append(pd.Series([Q], index=[p-1]))
    Losses         = Losses.append(pd.Series([losses], index=[p-1]))
    
    if plots == 'y':
        plt.figure(p)
        plt.plot(t,res)
        plt.plot(t[maxima],res[maxima],'r*')
        
        plt.plot(t[maxima1],res[maxima1],'r*')  
        
        plt.plot(t[maxima2],res[maxima2],'r*')
        
        plt.hlines(fwhm, -0.0003,0.0003,'g', linewidth = 0.7)
        
        plt.plot(t[index_izq],res[index_izq],'ko')
        plt.plot(t[index_der],res[index_der],'ko')
        plt.text(t.iloc[0],1.05*fwhm,str(Width)+'MHz')
        plt.text(t.iloc[0],0.95*fwhm,str(Q*1e-6)+'million')
        plt.text(t.iloc[0],0.85*fwhm,'Losses = '+str(np.round(losses,4)))
        
        
    if PRUEBA == 'Y':
        res = res**(-1)
        
        altura = 1.025*np.mean(res)
        peaks, _ = find_peaks(res,height=altura)
        results_half = peak_widths(res, peaks, rel_height = .5)
#        plt.plot(peaks, x[peaks], "x")
        
#        Width = resolution_OSA*results_half[0]       
        
        
#        bandwidth = c*(Width[0]*1e-9)/((lambda_laser*1e-9)**2)*1e-12
#        print('Soliton bandwidth = %s THz'% bandwidth)
        
        ZZ = res
        plt.plot(res)
        plt.plot(peaks, res[peaks], "x")
        plt.hlines(*results_half[1:], color="C2")
        plt.show()
        


#        plt.figure(figsize=size)
#        plt.plot(data.x,data.signal,linewidth=2)
#        plt.xlabel('Wavelength (nm)',fontsize=27)
#        plt.ylabel('Power (dBm)',fontsize=27)
#        plt.text(1500, -37,'~sech2(x)', fontsize=23)
#        plt.grid()
#        plt.yticks(fontsize=25, rotation=0)
#        plt.xticks(fontsize=25, rotation=0)
#        plt.ylim(-80,-5)
#        plt.plot(t, sech2(t, *popt_sech2),linewidth=2.5)
        


Q_factor_avg = Quality_factor.mean()
Losses = Losses.mean()


print('Average Q factor of this chip: %s million'% np.round(Q_factor_avg*1e-6,4))


#Fin=min(data.x, key=lambda x:abs(x-fin))
#            Ini=min(data.x, key=lambda x:abs(x-ini))

print(Losses)






