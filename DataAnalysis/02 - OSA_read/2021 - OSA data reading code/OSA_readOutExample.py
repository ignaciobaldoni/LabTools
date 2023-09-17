# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 09:20:57 2022

@author: ibaldoni

File to read OSA spectrum saved in .h5 file
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import datetime as dt
import os.path

from scipy import integrate

#from scipy.signal import find_peaks, peak_widths
#from scipy.optimize import curve_fit

#%% 

OSA_Calibration = 4.17

plt.close('all')

fileType_img = '.png' 

spectrum_plot       = True
fit_spectrum        = True

print_cw_calc       = True
save_results        = False
save_text_file      = False
pulse_in_t          = False
ignore_warnings     = True



SmartComb   = True
SolitonComb = False 

save_resultstoday = False

if ignore_warnings == True:
    import warnings
    warnings.filterwarnings("ignore")


size_fig    = (14,6)
fig_resolution = 100    # a.k.a., dpi
skipRow = 41

p=0
Figsize = (12,8)

laser_wavelength = 1542.142 
c=299789452.0

def freq(x):
    return c/(x*1e-9)*(1e-12)     

header_list = ["wavelength", "PSD"]

#sim_ASE = pd.read_table("ASE_1stStage_46mWpump.dat", sep=",", names=['wavelength', 'PSD_ASE_sim'])
#sim_ASE05 = pd.read_table("0.5ASE_1stStage_46mWpump.dat", sep=",", names=['wavelength', 'PSD_ASE_sim'])


import os
directory_data = os.getcwd()  
path, dirs, files = next(os.walk(directory_data))

if SmartComb == True:
    exceptions_in = ['.CSV']
    p = 0
    for i in files[:]:
        if all((ele_in in i) for ele_in in exceptions_in):
            fileName = i
            p+=1
            print('-----------------------------------------------')
            print(fileName)
            

            
            
            Name = fileName[len(fileName):-4]
            header_list = ["wavelength", "PSD"]
            med=pd.read_csv(fileName,skiprows = skipRow, names=header_list)
            

        
        
            wavelength      = med['wavelength']
            wavelength_nm   = wavelength
            PSD             = med['PSD']
            
            PSD = PSD + OSA_Calibration #4.35 # 4.35 comes from the calibration of the OSA with a powermeter


            if spectrum_plot == True:
                plt.figure()
                plt.plot(wavelength_nm,PSD,label='low power cw',alpha=0.5)
                plt.xlabel('Wavelength [nm]')
                plt.ylabel('Power [dBm/nm]')
                #plt.plot(sim_ASE.wavelength, sim_ASE.PSD_ASE_sim, linewidth = 2,label = 'Simulated ASE')
                #plt.plot(sim_ASE05.wavelength, sim_ASE05.PSD_ASE_sim, linewidth = 2, label = 'Simulated 50% ASE')
                plt.title(str(fileName[:-4]))
                plt.legend()
                Ylim = [-60,10]
                plt.ylim(Ylim)
                Xlim = [1500,1590]
                plt.xlim(Xlim)
                plt.grid()
                plt.savefig(str(fileName[:-4])+'.png')
            
                        
            if fit_spectrum == True:
        ##############################################################################        
        #        cw laser contribution calculation 
                lin = 10**(PSD/10) # Power originally is on dBm/nm      
                total=integrate.simps(lin,wavelength_nm)
    
                center = np.where(lin==np.max(lin))[0][0]
                
                bandwidth_dwdm = 0.0017
                
                CW_Laser=lin[center-int(bandwidth_dwdm*center):center+int(bandwidth_dwdm*center)]
                
                t=wavelength_nm
                t_laser=t[center-int(bandwidth_dwdm*center):center+int(bandwidth_dwdm*center)]
                
                laser=np.trapz(CW_Laser,t_laser)
                pge= np.round(laser/total*100,2)
                comb_contribution = (100-pge)/100*total
                
                if print_cw_calc == True:
                    print('Total amplified power is',total,'mW')
                    print('Laser power:',laser*1e3,'uW')
                    #print('laser represents',pge,'% of the total comb power')
                    #print('And comb power:\t\t',comb_contribution*1e3,'uW')
            
                    print('Center:',t[center],'with power',PSD.iloc[center],'dBm/nm')

                    
    
            
