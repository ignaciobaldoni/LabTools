# -*- coding: utf-8 -*-
"""
Created on Wed May  3 16:10:23 2023

@author: ibaldoni

This python script ONLY at the moment, plots the phase noise coming from the Phase Station 53100A
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np


# %% Personal functions 
import sys
sys.path.append(r'\\menloserver\MFS\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\python Util functions')
from Plot_aux_functions import Plot_parameters, makeTable # Import all functions from the script
from util_Functions import shot_noise_cw, shot_noise_pulsed, thermal_noise, jitter_calc #PhaseStation_PhaseNoise_csv

Plot_parameters(width=10)

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
                                     sameFig = False):
    
    
    if print_noise_floors:
    
        SN_am_dBc_Hz, SN_pm_dBc_Hz, SN_AM_to_PM_suppression = shot_noise_pulsed(
                                            Optical_Power = Optical_power, 
                                            Responsitivity = Responsitivity,
                                            Harmonic_number = MW_frequency,
                                            tau=Tau,
                                            AM_to_PM_suppression=AM2PM_suppression)
        
        shot_noise_cw_dBcHz, _ = shot_noise_cw(Optical_Power = Optical_power, 
                                                  Responsitivity=Responsitivity)
        
        Thermal_Noise = thermal_noise(MW_Power = MW_Power , unit = 'dBm')
        


    for folder in subfolders:
        results_folder = os.path.join(folder, 'Results')
        os.makedirs(results_folder, exist_ok=True)
    
        pm_files = [file for file in os.listdir(folder) if file.endswith("PM.csv")]
        print(pm_files)
        
        

        for pm_file in pm_files:
    
            # read PM files
            pm_df = pd.read_csv(os.path.join(folder, pm_file), sep=sep, names=headers)
    
            # plot PM and AM PSDs
            fig, ax = plt.subplots()
            if plot_figures:
                # if sameFig: plt.figure(1)
                # plt.ylim([-120,-30])
                # plt.xlim([10,2.5e7])
                plt.semilogx(pm_df['Frequency'], pm_df['PSD'])#, label=f'{filename_short}')
                plt.grid(visible=True, which='both', color='lightgrey', linestyle='--')  # style of grid lines
    
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
    
                # plt.legend()
                if not print_noise_floors:
                    makeTable(pm_df['Frequency'], pm_df['PSD'], fig,
                              print_freqs=[10000],
                              Table_height=0.2, Table_width=0.3)
    
                plt.ylabel('Phase Noise ℒ(f) [dBc/Hz]')
                plt.xlabel('Frequency offset [Hz]')
                plt.title(f'{pm_file[:-4]}')
    
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



                if saveFigs: plt.savefig(results_folder+'\\'+f'{pm_file[:-7]}_PhaseNoise_53100A.png')
                
    return results_folder
                # flicker_noise = pm_df['PSD'][0]-10*np.log10(pm_df['Frequency'])
                # plt.semilogx(pm_df['Frequency'],flicker_noise, label = 'Flicker')
                
            


if __name__ == '__main__':
    
    FOLDER = (r'\\menloserver\MFS\03-Operations\02-DCP\01-DCP_Management'+\
              r'\01-Gruppenmanagement\UMS\06_Measurements TBD\20230607 - Comb-MW comparison measurements'+\
              r'\HHI Fraunhofer AU06630\Cross correlation')
    
    # folder0 = r'\Overnight measurement for RS'
    # subfolders = [FOLDER + folder for folder in [folder0]]
    
    subfolders = [FOLDER,]
    
    
    filename_short  = 'Cross correlation'
    Optical_Power   = 1e-3
    MW_Power_dBm    = -6
    MW_Freq_Hz      = 10e9
    PD_Respons      = 0.3
    pulse_duration  = 75e-15
    AM2PM_suppr_dB  = 30
    
    savefigs        = False
    Noise_floors    = False
    Jitter          = False
    
    ResultsFolder = plot_PhaseNoise_fromPhaseStation(subfolders,
                                    saveFigs = savefigs,
                                    filename_short = filename_short,
                                    print_noise_floors = Noise_floors,
                                    plot_jitter = Jitter,
                                    Optical_power = Optical_Power,
                                    MW_Power = MW_Power_dBm,
                                    MW_frequency = MW_Freq_Hz,
                                    Responsitivity = PD_Respons,
                                    Tau = pulse_duration,
                                    AM2PM_suppression = AM2PM_suppr_dB)
    
    # fileName = r'\RohdeSchwarz_AU07434v2_PM.csv'
    # PhaseStation_PhaseNoise_csv(subfolders[0],fileName)
    
    plt.close('all')
    
    Rin_pathFile = r'\RIN_Igor_3.28V.xlsx'
    RIN = pd.read_excel(FOLDER+Rin_pathFile)
    print(RIN.head())
    AM_to_PM_suppresion = 0
    plt.figure(1)
    
    plt.semilogx(RIN.Frequency, RIN.RIN_dBc_Hz-AM_to_PM_suppresion, label = f'AM to PM suppresion ~ {AM_to_PM_suppresion}dB')
    print(f'AM to PM suppresion = {AM_to_PM_suppresion}')
    plt.grid(visible=True, which='both', color='lightgrey', linestyle='--')  # style of grid lines
    # plt.legend()
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('RIN [dBc/Hz]')
    # plt.title('Relative intesity noise')
    plt.savefig('hRIN.png')