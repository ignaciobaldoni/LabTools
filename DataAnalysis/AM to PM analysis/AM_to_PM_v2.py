# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 11:46:35 2023

@author: ibaldoni
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# %% Personal functions 
import sys
sys.path.append(r'\\menloserver\MFS\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\python Util functions')
from Plot_aux_functions import Plot_parameters, makeTable # Import all functions from the script
Plot_parameters(width=9)

               
FOLDER = (r'\\menloserver\MFS\03-Operations\03-Production\05-AU_PA\\'
          r'AU07434-SmartComb-PMWG_Hensoldt\03-Endabnahme\\'
          r'09-Microwave\AM to PM conversion\02 - Raw Data')


folder1 = r'\Freedom photonics MWU\Optical power 3.0 mW, MW power -15.2 dBm\\'
folder2 = r'\Freedom photonics MWU\Optical power 5.0 mW, MW power -11.4 dBm\\'
folder3 = r'\Freedom photonics MWU\Optical power 6.1 mW, MW power -8.67 dBm\\'
folder4 = r'\HHI Fraunhofer MWU\Optical power 3_0mW MW -18.8 dBm\\'
folder5 = r'\HHI Fraunhofer MWU\Optical power 5_0mW MW -14 dBm\\'
folder6 = r'\HHI Fraunhofer MWU\Optical power 8_10 mW MW -8.5 dBm\\'
folder7 = r'\HHI Fraunhofer MWU\Optical power 14.6 mW 7dBm MW (after HMC)'
folder8 = '\HHI Fraunhofer MWU\Optical power 14.6 mW (second scheme)'

folder0 = r'\Two_DUTs_One_OCXO_Ref'

Options = ['P','A']
sep = ','
headers = ['Frequency', 'PSD']

Folders = [FOLDER + folder for folder in [folder0]]#[folder1, folder2, folder3, folder4, folder5, folder6]]


AMtoPM_characterization = False
plot_figures = True


for folder in Folders:
    
    Photodiode      = folder.split(sep='\\')[-2]
    print(Photodiode)
    power_levels    = folder.split(sep='\\')[-1]
    print(power_levels)
    
    
    for_results = FOLDER+'\\'+Photodiode
    results_folder = os.path.join(for_results, 'Results')
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
        
    
    
    pm_files = [file for file in os.listdir(folder) if file.endswith("PM.csv")]
    data = []
    for pm_file in pm_files:
        am_file = pm_file.replace("_PM.csv", "_AM.csv")
        if am_file not in os.listdir(folder):
            continue  # skip if corresponding AM file not found

        # read PM and AM files
        pm_df = pd.read_csv(os.path.join(folder, pm_file), sep=sep, names=headers)
        am_df = pd.read_csv(os.path.join(folder, am_file), sep=sep, names=headers)
        
        difference = pm_df.PSD - am_df.PSD
        
        # plot PM and AM PSDs
        fig = plt.figure()
        if plot_figures:
            plt.semilogx(pm_df['Frequency'], pm_df['PSD'], label='PM Noise')
            plt.semilogx(am_df['Frequency'], am_df['PSD'], label='AM Noise')
            plt.grid(visible=True, which='major', color='lightgrey', linestyle='-')  # style of major grid lines
            plt.grid(visible=True, which='minor', color='lightgrey', linestyle='--')
            plt.legend()
            plt.title(f"Comparison of {pm_file[:-7]} AM and PM noise")
            plt.show()

        
        AMPM = makeTable(pm_df['Frequency'], difference, fig, print_freqs=[10000])
        plt.close()
        
        number_str = pm_file.split()[0]  # split the filename into words and take the first word
        if 'V' in number_str: number_str=number_str[:-1]
        
        if AMtoPM_characterization:  
            bias = float(number_str)  # convert to float
            am_to_pm = float(AMPM)
            data.append((bias, am_to_pm))
        
    if AMtoPM_characterization:    
        if 'HHI' in folder: plt.figure(2)
        df = pd.DataFrame(data, columns=['Bias', 'AM_to_PM'])
        df = df.sort_values(by='Bias')
        # plt.figure()
        plt.plot(df.Bias, df.AM_to_PM,'-o',label=power_levels)
        plt.grid()
        plt.title(Photodiode)
        plt.legend()
        plt.xlabel('Bias [V]')
        plt.ylabel('AM to PM suppression [dB]')
        plt.savefig(results_folder+'\\'+'AMtoPM_sup_HighPowerSmartComb_SecondScheme.png')
    