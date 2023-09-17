# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 16:27:55 2023

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
          r'09-Microwave\AM to PM conversion')


folder1 = r'\HHI Fraunhofer MWU\Around maximum 10.5 V Bias voltage optical power 8 mW'


Options = ['P','A']
sep = ','
headers = ['Frequency', 'PSD']

Folders = [FOLDER + folder for folder in [
                                          folder1, 
                                          ]]


for folder in Folders:
    
    Photodiode      = folder.split(sep='\\')[-4]
    power_levels    = folder.split(sep='\\')[-3]
    
    
    
    
    for_results = FOLDER+'\\'+Photodiode
    results_folder = os.path.join(for_results, 'Results')
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
        
    
    
    pm_files = [file for file in os.listdir(folder) if file.endswith("PM.csv")]
    data = []
    data2= []
    for pm_file in pm_files:
        optical_power   = pm_file.split(sep='mW')[-2][11:]
        opt_power = float(optical_power)
        
        am_file = pm_file.replace("_PM.csv", "_AM.csv")
        if am_file not in os.listdir(folder):
            continue  # skip if corresponding AM file not found

        # read PM and AM files
        pm_df = pd.read_csv(os.path.join(folder, pm_file), sep=sep, names=headers)
        am_df = pd.read_csv(os.path.join(folder, am_file), sep=sep, names=headers)
        
        difference = pm_df.PSD - am_df.PSD
        
        # plot PM and AM PSDs
        fig = plt.figure()
        # plt.semilogx(pm_df['Frequency'], pm_df['PSD'], label='PM Noise')
        # plt.semilogx(am_df['Frequency'], am_df['PSD'], label='AM Noise')
        # plt.grid(visible=True, which='major', color='lightgrey', linestyle='-')  # style of major grid lines
        # plt.grid(visible=True, which='minor', color='lightgrey', linestyle='--')
        # plt.legend()
        # plt.title(f"Comparison of {pm_file[:-7]} AM and PM noise")
        # plt.show()

        
        AMPM = makeTable(pm_df['Frequency'], difference, fig, print_freqs=[10000])
        plt.close()
        
        number_str = pm_file.split()[0]  # split the filename into words and take the first word
        if 'V' in number_str: number_str=number_str[:-1]

        bias = float(number_str)  # convert to float
        am_to_pm = float(AMPM)
        data.append((bias, am_to_pm))
        
        

        am_to_pm = float(AMPM)
        data2.append((opt_power, am_to_pm))
        
        
    if 'HHI' in folder: plt.figure(2)
    df = pd.DataFrame(data2, columns=['Bias', 'AM_to_PM'])
    df = df.sort_values(by='Bias')
    # plt.figure()
    plt.plot(df.Bias, df.AM_to_PM,'-o',label=power_levels)
    plt.grid()
    plt.title('Bias at 10.5 V')
    plt.legend()
    plt.xlabel('Optical Power [mW]')
    plt.ylabel('AM to PM suppression [dB]')
    plt.savefig(results_folder+'\\'+'AMtoPM_suppression_fixed bias.png')
    