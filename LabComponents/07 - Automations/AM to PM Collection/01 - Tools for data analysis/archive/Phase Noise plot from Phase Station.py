# -*- coding: utf-8 -*-
"""
Created on Wed May  3 16:10:23 2023

@author: ibaldoni
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

from scipy import integrate, fft

# %% Personal functions 
import sys
sys.path.append(r'\\menloserver\MFS\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\python Util functions')
from Plot_aux_functions import Plot_parameters, makeTable # Import all functions from the script
from util_Functions import shot_noise_cw, shot_noise_pulsed, therman_noise, jitter_calc

Plot_parameters(width=9)





def plot_PhaseNoise_fromPhaseStation(FOLDER,subfolders,
                                     plot_figures = True,
                                     sep = ',',
                                     headers = ['Frequency', 'PSD'], 
                                     saveFigs = True,
                                     filename_short = 'Phase noise',
                                     print_noise_floors = False,
                                     plot_jitter=False):
    
    
    
    if print_noise_floors:
    
   
        SN_am_dBc_Hz, SN_pm_dBc_Hz, SN_AM_to_PM_suppression = \
                                    shot_noise_pulsed(Optical_Power = 8e-3, 
                                              Responsitivity=0.3,
                                              Harmonic_number= 10e9,
                                              tau=75e-15,
                                              AM_to_PM_suppression=30)
        
        shot_noise_cw_dBcHz, _ = shot_noise_cw(Optical_Power = 8e-3, 
                                                  Responsitivity=0.3)
        
        Thermal_Noise = therman_noise(Optical_Power = 8e-3)


    for folder in subfolders:
        
        # Photodiode      = folder.split(sep='\\')[-2]
        # # print(Photodiode)
        # power_levels    = folder.split(sep='\\')[-1]
        # # print(power_levels)
        
        
        for_results = folder
        results_folder = os.path.join(for_results, 'Results')
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
            
        
        
        pm_files = [file for file in os.listdir(folder) if file.endswith("PM.csv")]
        for pm_file in pm_files:
            am_file = pm_file.replace("_PM.csv", "_AM.csv")
            if am_file not in os.listdir(folder):
                continue  # skip if corresponding AM file not found
    
            # read PM and AM files
            pm_df = pd.read_csv(os.path.join(folder, pm_file), sep=sep, names=headers)
            

            
            

            # plot PM and AM PSDs
            fig, ax = plt.subplots()#plt.figure()
            if plot_figures:
                plt.semilogx(pm_df['Frequency'], pm_df['PSD'], label=f'{filename_short}')
                plt.grid(visible=True, which='major', color='lightgrey', linestyle='-')  # style of major grid lines
                plt.grid(visible=True, which='minor', color='lightgrey', linestyle='--')
                
                if print_noise_floors:
                    
                    shot_noise_CW = np.ones_like(pm_df['PSD'])*shot_noise_cw_dBcHz
                    L_AM  = np.ones_like(pm_df['PSD'])*SN_am_dBc_Hz
                    L_PM  = np.ones_like(pm_df['PSD'])*SN_pm_dBc_Hz
                    L_AMtoPMsupp = np.ones_like(pm_df['PSD'])*SN_AM_to_PM_suppression
                    TN = np.ones_like(pm_df['PSD'])*Thermal_Noise
                    
                    
                    
                    plt.semilogx(pm_df['Frequency'], shot_noise_CW, 
                                 label=f'Shot noise (cw) = {shot_noise_cw_dBcHz:.2f} dBc/Hz',linestyle='--')
                    plt.semilogx(pm_df['Frequency'], L_AM, 
                                 label=f'Shot noise (AM) = {SN_am_dBc_Hz:.2f} dBc/Hz',linestyle='--')
                    plt.semilogx(pm_df['Frequency'], L_PM, 
                                 label=f'Shot noise (PM) = {SN_pm_dBc_Hz:.2f} dBc/Hz',linestyle='--')
                    plt.semilogx(pm_df['Frequency'], L_AMtoPMsupp, 
                                 label=f'Shot noise (AM to PM) = {SN_AM_to_PM_suppression:.2f} dBc/Hz',linestyle='--')
                    plt.semilogx(pm_df['Frequency'], TN, 
                                 label=f'Thermal noise = {Thermal_Noise:.2f} dBc/Hz',linestyle='--')
                
                plt.legend()
                # plt.title(f"{pm_file[:-7]}")    
                if print_noise_floors == False:
            
                    makeTable(pm_df['Frequency'], pm_df['PSD'], fig, 
                              print_freqs=[10000],
                              Table_height=0.2, Table_width = 0.3,
                              # x_pos = 0.15, y_pos = 0.16,
                              )
                
                plt.ylabel('Phase Noise ℒ(f) [dBc/Hz]')
                plt.xlabel('Frequency offset [Hz]')
                # plt.ylim([-195,-40])
                
                
                
                if plot_jitter:
                                       
                    freqs = np.array(pm_df['Frequency'])
                    psd = np.array(pm_df['PSD'])
                    
                    carrier = 10e9
                    
                    int_pn_rad, int_pn_sec = jitter_calc(psd, freqs,carrier)
    
                        
                    # fig, ax = plt.subplots()
                    # plt.semilogx(freqs,psd)
                    plt.ylabel('Phase noise [dBc/Hz]')
                    ax2 = ax.twinx()  
                    ax2.semilogy(freqs[1:][::-1],int_pn_sec,'r', label='Jitter')
                    ax2.set_ylabel('Timing noise [s/Hz]')
                    
                    # ax3 = ax.twinx()
                    # ax3.spines["right"].set_position(("axes", 1.2)) # adjust the position of ax3 to make room for the new axis label
                    # ax3.semilogy(freqs[1:][::-1], int_pn_rad*1e3, 'g')
                    # ax3.set_ylabel('Timing noise [mrad/Hz]')

                
                

        
                
            
                
                
                if saveFigs: plt.savefig(results_folder+'\\'+f'{pm_file[:-7]}_PhaseNoise.png')
                # flicker_noise = pm_df['PSD'][0]-10*np.log10(pm_df['Frequency'])
                # plt.semilogx(pm_df['Frequency'],flicker_noise, label = 'Flicker')

            
        
    
if __name__ == '__main__':
    
    FOLDER = (r'\\menloserver\MFS\03-Operations\03-Production\05-AU_PA'+\
              r'\AU07434-SmartComb-PMWG_Hensoldt\03-Endabnahme'+\
              r'\09-Microwave\AM to PM conversion\02 - Raw Data')
    
       
    folder0 = r'\Overnight measurement for RS'
    
    filename_short = 'Cross correlation'
    
       
    subfolders = [FOLDER + folder for folder in [folder0]]
    
    
    plot_PhaseNoise_fromPhaseStation(FOLDER,subfolders, 
                                     filename_short = filename_short, 
                                     saveFigs=False,
                                     print_noise_floors=False,
                                      plot_jitter=True
                                     )
    
    
    


    