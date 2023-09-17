# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 10:04:05 2020

@author: ibaldoni
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numpy import trapz
from scipy import integrate

from scipy.misc import electrocardiogram
from scipy.signal import find_peaks
from scipy.optimize import curve_fit

size=(18,14)
c=299789452

general = '\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
interes = '20201204_DualPump - 12GHz soliton generation (DWDM)\\'
interes2 = '04_Fourth run\\1 - Raw Data\\'

num_measurements = 1
laser_wavelength = 1542.142
calculo_cwlaser = 'on'
drawings='on'

myPath = str(general) + str(interes) 
print(myPath)
            
def freq(x):
    return c/(x*1e-9)*(1e-12)         

for jj in range(0,num_measurements): 
    
    
    New_path = myPath + 'W000'+str(jj)+'.csv'
    
    data=pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                     +str(interes)+str(interes2)+'W000'+str(jj)+'.csv')
#    data=pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
#                     +str(interes)+'W000'+str(jj)+'.csv', sep = ';')
    data.columns = ["x", "signal"]
       
    if calculo_cwlaser == 'on':
            t=data.x    
            rbw = t.diff().mean()
            dbm_nm = data['signal']

            # Chequear esto por favor
#            dbm_nm = dbm #+15  #10*np.log10(rbw)
            lin = 10**(dbm_nm/10)
            
            dnm = 0.02
            
            total=integrate.simps(lin,t)#trapz(lin,t)
            
#            total = total*F_mult_OSA
            print(total,'mW')
            
#            F_mult_OSA = 391    #1.18/total
#            print('Factor multiplicativo: %s ' % F_mult_OSA)
        
            ini     =   laser_wavelength - 0.05
            fin     =   laser_wavelength + 0.15
                
            # 1.5 is an only stimation. This should be done with the specs of the laser
            Fin=min(data.x, key=lambda x:abs(x-fin))
            Ini=min(data.x, key=lambda x:abs(x-ini))
            
            data_fin=np.where(data.x==Fin)
            Data_fin=data_fin[0].item()
            hallo=np.where(data.x==Ini)
            Hallo=hallo[0].item()
            
            CW_Laser=lin[Hallo:Data_fin]
            t_laser=t[Hallo:Data_fin]
            
            
            laser=np.trapz(CW_Laser,t_laser)
#            laser = laser*F_mult_OSA
            pge= np.round(laser/total*100,2)
            print(laser,'mW')
            print(pge,'%')
            print('----------------------------------------')
            comb_contribution = (100-pge)/100*total
            print(comb_contribution*1e6,'nW')
            print('----------------------------------------')
            
            
            
            
            if drawings == 'on': 
                fig, ax = plt.subplots(figsize=size)
                ax.plot(t, lin)
                ax.plot(t_laser,CW_Laser)
                ax.text(t[0],np.max(lin)*0.5,str(pge)+'%',fontsize=17)
                
                ax2 = ax.secondary_xaxis("top",functions=(freq,freq))
    
                ax2.set_xlabel("Frequency (THz)")
                ax.set_xlabel("Wavelength (nm)")
                plt.ylabel('Signal (mW)')
                plt.show()
                plt.savefig(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                            +str(interes)+str(interes2)+'CW_Calculation_'
                            +str(jj)+'1.png')
                
                fig, ax = plt.subplots(figsize=size)
                ax.plot(t, dbm_nm)
                ax.plot(t_laser,dbm_nm[Hallo:Data_fin])
                ax.text(t[0],np.max(dbm_nm)*0.5,str(pge)+'%',fontsize=17)
                
                ax2 = ax.secondary_xaxis("top",functions=(freq,freq))
    
                ax2.set_xlabel("Frequency (THz)")
                ax.set_xlabel("Wavelength (nm)")
                plt.ylabel('Signal (dB/nm)')
                plt.ylim([-90,0])
                plt.show()
                plt.savefig(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                            +str(interes)+str(interes2)+'CW_Calculation_'
                            +str(jj)+'2.png')
            
            
            

#            f=3.8e3 #According to RIO ORION Datasheet
#            Ax=c/f
#            
#            l=laser_wavelength*1e-9
#            Al = l/Ax
#            
#            fin=(l+Al)*1e9
#            ini=(l-Al)*1e9