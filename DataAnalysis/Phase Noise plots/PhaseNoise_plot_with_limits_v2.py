# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 15:32:29 2023

@author: ibaldoni

For plotting Phase Noise from CXA, PXA or PhaseStation 53100A
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np


# %% Personal functions 
import sys
sys.path.append(r'\\menloserver\MFS\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\python Util functions')
from Plot_aux_functions import Plot_parameters, makeTable # Import all functions from the script
from util_Functions import shot_noise_cw, shot_noise_pulsed, thermal_noise, jitter_calc

Plot_parameters(width=10)

def printNoiseFloors(Optical_power = 1e-3,
                        MW_Power = 0,
                        MW_frequency = 10e9,
                        Responsitivity = 0.3,
                        Tau = 75e-15,
                        AM2PM_suppression = 30,):
    
    SN_am_dBc_Hz, SN_pm_dBc_Hz, SN_AM_to_PM_suppression = shot_noise_pulsed(
                                        Optical_Power = Optical_power, 
                                        Responsitivity = Responsitivity,
                                        Harmonic_number = MW_frequency,
                                        tau=Tau,
                                        AM_to_PM_suppression=AM2PM_suppression)
    
    shot_noise_cw_dBcHz, _ = shot_noise_cw(Optical_Power = Optical_power, 
                                              Responsitivity=Responsitivity)
    
    Thermal_Noise = thermal_noise(MW_Power = MW_Power , unit = 'dBm')
    
    return SN_am_dBc_Hz, SN_pm_dBc_Hz, SN_AM_to_PM_suppression, shot_noise_cw_dBcHz, Thermal_Noise



def plot_PhaseNoise_fromPhaseStation(subfolders,
                                     plot_figures = True,
                                     sep = ',',
                                     headers = ['Frequency', 'PSD'], 
                                     saveFigs = True,
                                     filename_short = 'Phase noise',
                                     print_noise_floors = False,
                                     plot_jitter=False,
                                     Timing_noise_mrad=False,
                                     Optical_power = 1e-3,
                                     MW_Power = 0,
                                     MW_frequency = 10e9,
                                     Responsitivity = 0.3,
                                     Tau = 75e-15,
                                     AM2PM_suppression = 30,                                     
                                     sameFig = False,
                                     Results_folder = False, 
                                     Table = False,
                                     Freqs_interest = [10,100,1000,10000,100000]):
    
    
    if print_noise_floors:
        print('Noise floors go here')
        SN_am_dBc_Hz, SN_pm_dBc_Hz, SN_AM_to_PM_suppression,\
            shot_noise_cw_dBcHz, Thermal_Noise =\
                printNoiseFloors(Optical_power = Optical_power,
                                MW_Power = MW_Power,
                                MW_frequency = MW_frequency,
                                Responsitivity = Responsitivity,
                                Tau = Tau,
                                AM2PM_suppression = AM2PM_suppression)
    
        
        


    for folder in subfolders:
        if Results_folder:
            results_folder = os.path.join(folder, 'Results')
            os.makedirs(results_folder, exist_ok=True)
        else:
            results_folder = None
    
        pm_files = [file for file in os.listdir(folder) if file.endswith("PM.csv")]
        print(pm_files)
        
        

        for pm_file in pm_files:
    
            # read PM files
            pm_df = pd.read_csv(os.path.join(folder, pm_file), sep=sep, names=headers)
            
    
            # plot PM and AM PSDs
            fig, ax = plt.subplots()
            if plot_figures:
                if sameFig: plt.figure(1)
                
                plt.semilogx(pm_df['Frequency'], pm_df['PSD'])#, label=f'{pm_file[:-4]}')
                
    
                if print_noise_floors:
                    noise_labels = [
                        # ('Shot noise (cw)', shot_noise_cw_dBcHz),
                        ('Shot noise (AM)', SN_am_dBc_Hz),
                        ('Shot noise (PM)', SN_pm_dBc_Hz),
                        ('Shot noise (AM to PM)', SN_AM_to_PM_suppression),
                        ('Thermal noise', Thermal_Noise)
                    ]
                    for label, value in noise_labels:
                        plt.semilogx(pm_df['Frequency'], np.ones_like(pm_df['PSD']) * value,
                                     label=f'{label} = {value:.2f} dBc/Hz', linestyle='--')
    
                
                if Table:
                    makeTable(pm_df['Frequency'], pm_df['PSD'], fig,
                              print_freqs=Freqs_interest,
                              Table_height=0.2, Table_width=0.3)
    
                
    
                if plot_jitter:
                    freqs = np.array(pm_df['Frequency'])
                    psd = np.array(pm_df['PSD'])
                    carrier = MW_frequency
                    int_pn_rad, int_pn_sec = jitter_calc(psd, freqs, carrier)
    
                    ax2 = ax.twinx()
                    ax2.semilogy(freqs[1:][::-1], int_pn_sec, 'r', label='Jitter')
                    ax2.set_ylabel('Timing noise [s/Hz]')
    
                    if Timing_noise_mrad:
                        ax3 = ax.twinx()
                        ax3.spines["right"].set_position(("axes", 1.2))
                        ax3.semilogy(freqs[1:][::-1], int_pn_rad * 1e3, 'g')
                        ax3.set_ylabel('Timing noise [mrad/Hz]')
                
                
                #### ----------- PLOT PARAMETERS ----------- ####
                plt.ylabel('Amplitude Noise [dBc/Hz]')
                plt.xlabel('Frequency offset [Hz]')
                
                plt.ylim([-210,-60])
                # plt.xlim([10,2.5e7])
                plt.legend()
                # plt.title(f'{pm_file[:-4]}')
                plt.grid(visible=True, which='both', color='lightgrey', linestyle='--')  
                


                if saveFigs: plt.savefig(f'{pm_file[:-7]}.png')

                
    return results_folder, pm_df
                
                
            


if __name__ == '__main__':
           
       
    FOLDER = (r'\\menloserver\MFS\03-Operations\03-Production\05-AU_PA'+\
              r'\AU06630-SmartComb-NIST_Optical_Frequency_Measurements'+\
              r'\08-Service_und_Support\RMA L1749-230330\06_Mikrowelle'+\
              r'\07_MW_Phase Noise\02_Phase Station\2023-06-15 - Suppression of 23 dB')
        

    
    # folder0 = r'\Overnight measurement for RS'
    # subfolders = [FOLDER + folder for folder in [folder0]]
    
    subfolders = [FOLDER,]
    
    
    filename_short  = 'Cross correlation'
    Optical_Power   = 1e-3
    MW_Power_dBm    = -6
    MW_Freq_Hz      = 10e9
    PD_Respons      = 0.3
    pulse_duration  = 2075e-15
    AM2PM_suppr_dB  = 30
    
    savefigs        = False
    Noise_floors    = True
    Jitter          = False
    Results_Folder  = False
    
    _ ,_ = plot_PhaseNoise_fromPhaseStation(subfolders,
                                    saveFigs = savefigs,
                                    filename_short = filename_short,
                                    print_noise_floors = Noise_floors,
                                    plot_jitter = Jitter,
                                    Optical_power = Optical_Power,
                                    MW_Power = MW_Power_dBm,
                                    MW_frequency = MW_Freq_Hz,
                                    Responsitivity = PD_Respons,
                                    Tau = pulse_duration,
                                    AM2PM_suppression = AM2PM_suppr_dB,
                                    sameFig = True, 
                                    Results_folder = Results_Folder)
    
    
    # readCXA_usb(folder, fileName,Names= ['Frequency','Variable'])
    

