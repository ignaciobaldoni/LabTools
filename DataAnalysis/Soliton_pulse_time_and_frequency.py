# -*- coding: utf-8 -*-
"""
Created on Tue May 18 20:30:57 2021

@author: ibaldoni
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import os.path

from scipy import integrate

#%% 

files = ['//menloserver/MFS/03-Operations/02-DCP/03-Entwicklungsprojekte/9556-COSMIC/52-Messergebnisse/20210219_12GHz_D63_3_C12_F4_OSA_Measurements/1-Raw Data/D63_3_C12_F4/W0006.csv',
         '//menloserver/MFS/03-Operations/02-DCP/03-Entwicklungsprojekte/9552-KECOMO/52-Messergebnisse/20200302_Soliton_mit_neue_Verstäker/W0005.csv',
         '//menloserver/MFS/03-Operations/02-DCP/03-Entwicklungsprojekte/9556-COSMIC/52-Messergebnisse/20210426_12GHz_Single_soliton_locked/W0000.csv',
        ]
plt.close('all')

fileType_img = '.png' 

fit_spectrum        = True
print_cw_calc       = True
save_results        = False
save_text_file      = False
pulse_in_t          = True
ignore_warnings     = True 

if ignore_warnings == True:
    import warnings
    warnings.filterwarnings("ignore")

#Frequency_or_wavelength = 'F' # or 'W'


size_fig    = (12,8)
fig_resolution = 100    # a.k.a., dpi
skipRow = 41

p=0
Figsize = (12,8)

laser_wavelength = 1542.142 
c=299789452.0

def freq(x):
    return c/(x*1e-9)*(1e-12)     

##############################################################################
#     RUN analysis for every file we are interested
    
for f in files: 
    fileName = f
    p+=1
    Name = f[len(f)-4-5:-4]
    print(Name)
    header_list = ["Wavelength", "Power"]
    med=pd.read_csv(fileName,skiprows = skipRow, names=header_list)

    
    
    if fit_spectrum == False:
        plt.figure(num = p)
        plt.plot(med.Wavelength,med.Power)
        plt.xlabel('Wavelength (nm)')
        plt.xlabel('Power (dBm/nm)')
        Ylim = [-70,5]
        plt.ylim(Ylim)
        plt.grid()
    

         
    if fit_spectrum == True:
        from scipy.signal import find_peaks, peak_widths
        from scipy.optimize import curve_fit
        
##############################################################################        
#        cw laser contribution calculation 
        lin = 10**(med.Power/10) # Power originally is on dBm/nm      
        total=integrate.simps(lin,med.Wavelength); 
        
        
        centro = np.where(lin==np.max(lin))[0][0]
        
        CW_Laser=lin[centro-int(0.005*centro):centro+int(0.005*centro)]
        
        t=med.Wavelength
        t_laser=t[centro-int(0.005*centro):centro+int(0.005*centro)]
        
        laser=np.trapz(CW_Laser,t_laser)
        pge= np.round(laser/total*100,2)
        comb_contribution = (100-pge)/100*total
        
        if print_cw_calc == True:
            print('Total power of the comb (including laser) is',total*1e3,'uW')
            print('Laser power:',laser*1e3,'uW')
            print('laser represents',pge,'% of the total comb power')
            print('And comb power:\t\t',comb_contribution*1e3,'uW')
##############################################################################        
#        Pulse parameters calculation
        
        centro = np.where(lin==np.max(lin))[0][0]

        linn = np.concatenate((lin[:centro-int(0.005*centro)],lin[centro+int(0.005*centro):]))
        wl =  np.concatenate((med.Wavelength[:centro-int(0.005*centro)],med.Wavelength[centro+int(0.005*centro):]))
        
        
        
        center_freq = freq(laser_wavelength)

        def sech(x):
           return 1/np.cosh(x) 
        def sech2_v2(x,A,lambda0,B):

            x = x-laser_wavelength
            return A*(sech((x-lambda0)/B))**2
        
     
               
        magic_number = 20
        initial_values3 = [laser_wavelength,30,40]
        rep_rate = 12.13e9
        Ylim = [-75,-12]
            
        
        if (med.Wavelength.iloc[-1] > 1602 and med.Wavelength.iloc[-1] < 1610):#1600:

            magic_number = 20
            initial_values3 = [laser_wavelength,.010,0.04]
            rep_rate = 12.13e9
            Ylim = [-40,0]
            

        if med.Wavelength.iloc[0] < 1468:#1600:

            magic_number = 200   
            initial_values3 = [laser_wavelength,30,40]
            rep_rate = 19.71e9
            Ylim = [-75,-12]

         



        ##### Fit with sech2(x) in the linear domain   
        peaks, _ = find_peaks(linn, distance=magic_number)#,prominence=(None, 0.6))
                
        sigma = np.ones(len(linn[peaks]))*0.5
        popt4, pcov4 =  curve_fit(sech2_v2, wl[peaks], linn[peaks],initial_values3,sigma= sigma)
        


        ##### Plots of the fits with sech2(x) in the linear domain       
        plt.figure(figsize = size_fig); plt.plot(wl,linn)
        plt.plot(med.Wavelength[peaks], linn[peaks],'o-')    
        plt.plot(wl, sech2_v2(wl, *popt4), 'm--',
              label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt4))
        plt.title(str(np.round(rep_rate*1e-9,5))+' GHz',fontsize=17)
        plt.grid()
        plt.ylabel('Power (mW)',fontsize = 17)
        plt.xlabel('Wavelength (nm)',fontsize = 17)
        plt.tick_params(labelsize=17)
        if save_results == True:
            plt.savefig(Name+'_linearPlot_'+fileType_img)
        
        
        # Definition of the pulse parameters

        spectrum_width_nm   = popt4[2]*2 # Bandwidth  
        spectrum_width_THz  = (c*np.abs(spectrum_width_nm*1e-9)/(laser_wavelength*1e-9)**2)

        Avg_power   = comb_contribution*1e-3
        E_pulse     = Avg_power / rep_rate        
        
        def acosh(x):
            return np.log(x+np.sqrt(x**2-1))
        
        
        # Taking into account the time-bandwidth product we calculate pulse time duration       
        factor_sech2 = ((2/np.pi)*acosh(np.sqrt(2)))**2        
        t_pulse = (factor_sech2/spectrum_width_THz)
        t_pulse_fs = t_pulse*1e15

        Peak_power = 0.88*E_pulse/t_pulse  # Sech2 
        
#        print('Relation between pulse and spectrum:', t_pulse*spectrum_width_THz)
        
        if save_text_file == True:
            import sys
            sys.stdout = open("Results2.txt", "a")
            print('Repetition rate: \t', rep_rate*1e-9, 'GHz')
            print('Average power: \t\t', comb_contribution*1e3, 'uW')
            print('Pulse time duration: \t', t_pulse_fs, 'fs')
            print('Energy per pulse: \t', E_pulse*1e15,'nJ')
            print('Peak power: \t\t',Peak_power*1e3,'mW')
            print('Width spectrum: \t',spectrum_width_nm ,'nm')
            print('Width spectrum: \t',spectrum_width_THz*1e-12 ,'THz')
            print('------------------------------------------------------------')
            
        # conversion back again to dbm/nm
        fit_dbm =  10*np.log10(sech2_v2(wl, *popt4))
        
        plt.figure(figsize = size_fig)
        plt.plot(med.Wavelength,med.Power)
        plt.plot(wl, fit_dbm, 'm--',
              label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt4))
        plt.ylim(Ylim)
        plt.legend()
        plt.title(str(np.round(rep_rate*1e-9,5))+' GHz',fontsize=17)
        plt.grid()
        plt.ylabel('Power (dBm/nm)',fontsize = 17)
        plt.xlabel('Wavelength (nm)',fontsize = 17)
        plt.tick_params(labelsize=17)
        if save_results == True:
            plt.savefig(Name+'_logPlot_'+fileType_img)
        
        
    if pulse_in_t == True:
        plt.figure()
        plt.plot(np.fft.ifftshift(np.fft.ifft(np.sqrt(10**(med.Power/10)))))    
        plt.show()  
  

