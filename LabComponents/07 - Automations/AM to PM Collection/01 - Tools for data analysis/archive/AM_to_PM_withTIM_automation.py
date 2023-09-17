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

               


def AM_to_PM_characterization(FOLDER, FOLDERFolders, 
                              bias_sweep_characterization = True,
                              plot_figures = False,
                              saveFigs = False):
    

    sep = ','
    headers = ['Frequency', 'PSD']
    
    
    for folder in Folders:
        
        Photodiode      = folder.split(sep='\\')[-4]
        print(Photodiode)
        power_levels    = folder.split(sep='\\')[-1]
        print(power_levels)
        
        
        results_folder = os.path.join(FOLDER, 'Results')
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
            # print(AMPM)
            plt.close()
            
            number_str = pm_file.split()[0]  # split the filename into words and take the first word
            if 'V' in number_str: number_str=number_str[:-1]
            
            if bias_sweep_characterization:  
                bias = float(number_str)  # convert to float
                am_to_pm = float(AMPM)
                data.append((bias, am_to_pm))
            
        if bias_sweep_characterization:    
            plt.figure(2)
            df = pd.DataFrame(data, columns=['Bias', 'AM_to_PM'])
            df = df.sort_values(by='Bias')
            plt.plot(df.Bias, df.AM_to_PM,'-o',label=power_levels)
            plt.grid()
            plt.title(Photodiode)
            plt.legend()
            plt.xlabel('Bias [V]')
            plt.ylabel('AM to PM suppression [dB]')
            plt.grid(visible=True, which='major', color='lightgrey', linestyle='-')  # style of major grid lines
            plt.grid(visible=True, which='minor', color='lightgrey', linestyle='--')
            
            if saveFigs: plt.savefig(results_folder+'\\'+'AM to PM suppression.png')
        
        

if __name__ == '__main__':
    

    FOLDER = (r'\\menloserver\mfs\03-Operations\03-Production\05-AU_PA'+\
              r'\AU07627_AU06630-RMA-Syncro\05_2023 - Photodiodes characterization'+\
              r'\HHI Fraunhoffer (new)\AM to PM NIST\Optically locked')
    
    folder1 = r'\2.0 mW'
    folder2 = r'\3.5 mW'
    folder3 = r'\5.0 mW'
    folder4 = r'\6.5 mW'
    
    
    

    
    Folders = [FOLDER + folder for folder in [folder1, 
                                              folder2, 
                                              folder3, 
                                              folder4, 
                                              # folder5, 
                                              # folder6
                                              ]]
    
    
    
    AM_to_PM_characterization(FOLDER, 
                              Folders, 
                              bias_sweep_characterization = True,
                              plot_figures = False,
                              saveFigs = True)

    