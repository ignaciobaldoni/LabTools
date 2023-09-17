
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 20:30:57 2021

@author: ibaldoni

File to read OSA spectrum saved in .h5 file
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import os.path

from scipy import integrate

from labTools_utilities import saveDictToHdf5
from scipy.signal import find_peaks, peak_widths
from scipy.optimize import curve_fit

#%% 

plt.close('all')

fileType_img = '.png' 

spectrum_plot       = True
fit_spectrum        = True

print_cw_calc       = False
save_results        = False
save_text_file      = False
pulse_in_t          = False
ignore_warnings     = True


OSA_Calibration = 3.417

SmartComb   = False
SolitonComb = True 

save_resultstoday = True

if ignore_warnings == True:
    import warnings
    warnings.filterwarnings("ignore")

#Frequency_or_wavelength = 'F' # or 'W'


size_fig    = (14,6)
fig_resolution = 100    # a.k.a., dpi
skipRow = 41

p=0
Figsize = (12,8)

laser_wavelength = 1542.142 
c=299789452.0

def freq(x):
    return c/(x*1e-9)*(1e-12)     

##############################################################################
#     Find files we are interested in



import os
directory_data = os.getcwd()  
path, dirs, files = next(os.walk(directory_data))


if SolitonComb == True:

    exceptions_in = ['.h5',]
    p = 0
    for i in files[0:1]:
        if all((ele_in in i) for ele_in in exceptions_in):
            fileName = i
            fileName = r'\\menloserver\MFS\03-Operations\02-DCP\03-Entwicklungsprojekte\9556-COSMIC\52-Messergebnisse' \
               + r'\20220218_IB_FullPreAmplifierStage\104334_OSA_singleSol.h5'
            p+=1
            print(fileName)
            
            dict_Result = saveDictToHdf5.load_dict_from_hdf5(fileName)
            
            resolution      = dict_Result['resolution_nm']
            wavelength      = dict_Result['wavelenghts_nm']
            wavelength_nm   = wavelength*1e9
            PSD             = dict_Result['psd_dBm_per_nm']
            
            PSD = PSD + OSA_Calibration
            
            if spectrum_plot == True:
                plt.figure()
                plt.plot(wavelength_nm,PSD)
                plt.xlabel('Wavelength [nm]')
                plt.ylabel('Power [dBm/nm]')
                plt.title(str(fileName[:-3]))
                Ylim = [-70,15]
                plt.ylim(Ylim)
                plt.grid()
            
            
            
            if fit_spectrum == True:
                
        ##############################################################################        
        #        cw laser contribution calculation 
                lin = 10**(PSD/10) # Power originally is on dBm/nm      
                #lin = 10**(np.diff(PSD)*0.02/10)
                #wavelength_nm = wavelength_nm[1:]
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
                    print('Total power of the comb (including laser) is',total*1e3,'uW')
                    print('Laser power:',laser*1e3,'uW')
                    print('laser represents',pge,'% of the total comb power')
                    print('And comb power:\t\t',comb_contribution*1e3,'uW')
                
                
    ##############################################################################        
    #        Pulse parameters calculation
            
            center = np.where(lin==np.max(lin))[0][0]
    
            linn = np.concatenate((lin[:center-int(bandwidth_dwdm*center)],lin[center+int(bandwidth_dwdm*center):]))
            wl =  np.concatenate((wavelength_nm[:center-int(bandwidth_dwdm*center)],wavelength_nm[center+int(bandwidth_dwdm*center):]))
            
            
            
            center_freq = freq(laser_wavelength)
    
            def sech(x):
               return 1/np.cosh(x) 
            def sech2_v2(x,A,lambda0,B):
    
                x = x-laser_wavelength
                return A*(sech((x-lambda0)/B))**2
            
         
                   
            magic_number = 20
            initial_values3 = [laser_wavelength,30,40]
            rep_rate = 12.13e9
            Ylim = [-70,15]
                
    
    
            ##### Fit with sech2(x) in the linear domain   
            peaks, _ = find_peaks(linn, distance=magic_number)#,prominence=(None, 0.6))
                    
            sigma = np.ones(len(linn[peaks]))*0.5
            popt4, pcov4 =  curve_fit(sech2_v2, wl[peaks], linn[peaks],initial_values3,sigma= sigma)
            
    
    
            ##### Plots of the fits with sech2(x) in the linear domain       
            plt.figure(figsize = size_fig,); plt.plot(wl,linn)
            #plt.plot(wavelength_nm[peaks], linn[peaks],'o-')    
            plt.plot(wl, sech2_v2(wl, *popt4), 'm--',
                  label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt4))
            
            
            peak_sech, _ = find_peaks(sech2_v2(wl, *popt4))
            x = sech2_v2(wl, *popt4)
            results_half = peak_widths(sech2_v2(wl, *popt4), peak_sech, rel_height=0.5)
            
    
            plt.plot(wl[peak_sech], x[peak_sech], "x")
            
    
            
            plt.title(str(np.round(rep_rate*1e-9,5))+' GHz',fontsize=17)
            plt.grid()
            plt.ylabel('Power [mW]',fontsize = 17)
            plt.xlabel('Wavelength [nm]',fontsize = 17)
            plt.tick_params(labelsize=17)
            plt.hlines(results_half[1], 1533.101,1565)
            if save_results == True:
                plt.savefig(fileName+'_linearPlot_'+fileType_img)
            
          
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
                print('Energy per pulse: \t', E_pulse*1e12,'pJ')
                print('Peak power: \t\t',Peak_power*1e3,'mW')
                print('Width spectrum: \t',spectrum_width_nm ,'nm')
                print('Width spectrum: \t',spectrum_width_THz*1e-12 ,'THz')
                print('------------------------------------------------------------')
            else:
                print('Repetition rate: \t', rep_rate*1e-9, 'GHz')
                print('Average power: \t\t', comb_contribution*1e3, 'uW')
                print('Pulse time duration: \t', t_pulse_fs, 'fs')
                print('Energy per pulse: \t', E_pulse*1e12,'pJ')
                print('Peak power: \t\t',Peak_power*1e3,'mW')
                print('Width spectrum: \t',spectrum_width_nm ,'nm')
                print('Width spectrum: \t',spectrum_width_THz*1e-12 ,'THz')
                print('------------------------------------------------------------')
                
            # conversion back again to dbm/nm
            fit_dbm =  10*np.log10(sech2_v2(wl, *popt4))
            
            middle = 10*np.log10(results_half[1])[0]
            
            
            
            plt.figure(figsize = size_fig)
            #plt.plot(wavelength_nm,med.Power)
            plt.hlines(middle,1533.53,1555.56,color='k',linewidth=2.35,
                       linestyle='--',zorder = 10)
            plt.text(1557,middle+1.5,'3 dB',
                     color ='k', 
                     fontsize = 20)
            plt.plot(wl,10*np.log10(linn),zorder=0,alpha=0.8)
            plt.plot(wl, fit_dbm, 'r-',linewidth = 2.25,
                  #label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt4)
                  zorder=0)
            
            
            #plt.legend()
            #plt.title(str(np.round(rep_rate*1e-9,5))+' GHz',fontsize=17)
            #plt.grid()
            plt.ylabel('Power\n[10 dB/div.]',
                       fontsize = 17)
            
            ax = plt.gca()        
            ax.axes.yaxis.set_ticklabels([])
            
            plt.xlabel('Wavelength [nm]',fontsize = 17)
            plt.tick_params(labelsize=17,width=2, length=10)
            plt.text(1500,-30,'~$sech^2$',color ='red', fontsize = 20)
            #plt.xlim(1542.5,1548)
            
    
            plt.yticks(np.arange(Ylim[0], Ylim[1], 10))
            plt.ylim(Ylim)
            
            if save_resultstoday == True:
                plt.savefig(fileName[:-4]+'transparent_logPlot_'+fileType_img,transparent = True)
            
            
        if pulse_in_t == True:
            plt.figure()
            plt.plot(np.fft.ifftshift(np.fft.ifft(np.sqrt(10**(PSD/10)))))    
            plt.show()  
    
'-----------------------------------------------------------------------------'    
'-----------------------------------------------------------------------------'    
'-----------------------------------------------------------------------------'    
'-----------------------------------------------------------------------------'    
'-----------------------------------------------------------------------------'    
'-----------------------------------------------------------------------------'

if SmartComb == True:
    exceptions_in = ['.CSV',]
    p = 0
    for i in files:
        if all((ele_in in i) for ele_in in exceptions_in):
            fileName = i
            p+=1
            print(fileName)
            
            Name = fileName[len(fileName):-4]
            header_list = ["wavelength", "PSD"]
            med=pd.read_csv(fileName,skiprows = skipRow, names=header_list)
        
            
            wavelength      = med['wavelength']
            wavelength_nm   = wavelength
            PSD             = med['PSD']
            
            PSD = PSD + OSA_Calibration
            
            if spectrum_plot == True:
                plt.figure()
                plt.plot(wavelength_nm,PSD)
                plt.xlabel('Wavelength [nm]')
                plt.ylabel('Power [dBm/nm]')
                plt.title(str(fileName[:-3]))
                Ylim = [-70,15]
                plt.ylim(Ylim)
                plt.grid()
            
            
            
            if fit_spectrum == True:
        ##############################################################################        
        #        cw laser contribution calculation 
                lin = 10**(PSD/10) # Power originally is on dBm/nm      
                total=integrate.simps(lin,wavelength_nm)
    
                center = np.where(lin==np.max(lin))[0][0]
                
                bandwidth_dwdm = 0.00
                
                CW_Laser=lin[center-int(bandwidth_dwdm*center):center+int(bandwidth_dwdm*center)]
                
                t=wavelength_nm
                t_laser=t[center-int(bandwidth_dwdm*center):center+int(bandwidth_dwdm*center)]
                
                laser=np.trapz(CW_Laser,t_laser)
                pge= np.round(laser/total*100,2)
                comb_contribution = (100-pge)/100*total
                
                if print_cw_calc == True:
                    print('Total power (including laser) is',total,'uW')
                    print('Laser power:',laser*1e3,'uW')
                    print('laser represents',pge,'% of the total comb power')
                    print('And comb power:\t\t',comb_contribution*1e3,'uW')
                    
    
                
    #        Pulse parameters calculation
            
                center = np.where(lin==np.max(lin))[0][0]
        
                linn = np.concatenate((lin[:center-int(bandwidth_dwdm*center)],lin[center+int(bandwidth_dwdm*center):]))
                wl =  np.concatenate((wavelength_nm[:center-int(bandwidth_dwdm*center)],wavelength_nm[center+int(bandwidth_dwdm*center):]))
                
                
                
                center_freq = freq(laser_wavelength)
        
                def sech(x):
                   return 1/np.cosh(x) 
                def sech2_v2(x,A,lambda0,B):
        
                    x = x-laser_wavelength
                    return A*(sech((x-lambda0)/B))**2
                
             
                       
                magic_number = 20
                initial_values3 = [laser_wavelength,30,40]
                rep_rate = 12.13e9
                Ylim = [-70,15]
                    
        
        
                ##### Fit with sech2(x) in the linear domain   
                peaks, _ = find_peaks(linn, distance=magic_number)#,prominence=(None, 0.6))
                        
                sigma = np.ones(len(linn[peaks]))*0.5
                popt4, pcov4 =  curve_fit(sech2_v2, wl[peaks], linn[peaks],initial_values3,sigma= sigma)
                
        
        
                ##### Plots of the fits with sech2(x) in the linear domain       
                plt.figure(figsize = size_fig,); plt.plot(wl,linn)
                #plt.plot(wavelength_nm[peaks], linn[peaks],'o-')    
                plt.plot(wl, sech2_v2(wl, *popt4), 'm--',
                      label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt4))
                
                
                peak_sech, _ = find_peaks(sech2_v2(wl, *popt4))
                x = sech2_v2(wl, *popt4)
                results_half = peak_widths(sech2_v2(wl, *popt4), peak_sech, rel_height=0.5)
                
        
                plt.plot(wl[peak_sech], x[peak_sech], "x")
                
        
                
                plt.title(str(np.round(rep_rate*1e-9,5))+' GHz',fontsize=17)
                plt.grid()
                plt.ylabel('Power [mW]',fontsize = 17)
                plt.xlabel('Wavelength [nm]',fontsize = 17)
                plt.tick_params(labelsize=17)
                plt.hlines(results_half[1], 1533.101,1565)
                if save_results == True:
                    plt.savefig(fileName+'_linearPlot_'+fileType_img)
                
              
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
                    print('Energy per pulse: \t', E_pulse*1e12,'pJ')
                    print('Peak power: \t\t',Peak_power*1e3,'mW')
                    print('Width spectrum: \t',spectrum_width_nm ,'nm')
                    print('Width spectrum: \t',spectrum_width_THz*1e-12 ,'THz')
                    print('------------------------------------------------------------')
                else:
                    print('Repetition rate: \t', rep_rate*1e-9, 'GHz')
                    print('Average power: \t\t', comb_contribution*1e3, 'uW')
                    print('Pulse time duration: \t', t_pulse_fs, 'fs')
                    print('Energy per pulse: \t', E_pulse*1e12,'pJ')
                    print('Peak power: \t\t',Peak_power*1e3,'mW')
                    print('Width spectrum: \t',spectrum_width_nm ,'nm')
                    print('Width spectrum: \t',spectrum_width_THz*1e-12 ,'THz')
                    print('------------------------------------------------------------')
                    
                # conversion back again to dbm/nm
                fit_dbm =  10*np.log10(sech2_v2(wl, *popt4))
                
                middle = 10*np.log10(results_half[1])[0]
                
                
                
                plt.figure(figsize = size_fig)
                #plt.plot(wavelength_nm,med.Power)
                plt.hlines(middle,1533.53,1555.56,color='k',linewidth=2.35,
                           linestyle='--',zorder = 10)
                plt.text(1557,middle+1.5,'3 dB',
                         color ='k', 
                         fontsize = 20)
                plt.plot(wl,10*np.log10(linn),zorder=0,alpha=0.8)
                plt.plot(wl, fit_dbm, 'r-',linewidth = 2.25,
                      #label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt4)
                      zorder=0)
                
                
                #plt.legend()
                #plt.title(str(np.round(rep_rate*1e-9,5))+' GHz',fontsize=17)
                #plt.grid()
                plt.ylabel('Power\n[10 dB/div.]',
                           fontsize = 17)
                
                ax = plt.gca()        
                ax.axes.yaxis.set_ticklabels([])
                
                plt.xlabel('Wavelength [nm]',fontsize = 17)
                plt.tick_params(labelsize=17,width=2, length=10)
                plt.text(1500,-30,'~$sech^2$',color ='red', fontsize = 20)
                #plt.xlim(1542.5,1548)
                
        
                plt.yticks(np.arange(Ylim[0], Ylim[1], 10))
                plt.ylim(Ylim)
                
                if save_resultstoday == True:
                    plt.savefig(Name+'transparent_logPlot_'+fileType_img,transparent = True)
                
                
            if pulse_in_t == True:
                plt.figure()
                plt.plot(np.fft.ifftshift(np.fft.ifft(np.sqrt(10**(med.Power/10)))))    
                plt.show()  