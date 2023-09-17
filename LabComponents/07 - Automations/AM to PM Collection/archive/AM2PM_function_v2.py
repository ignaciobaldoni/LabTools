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



    

def AM2PM(FOLDER,Folders, AMtoPM_characterization = True, 
          plot_figures = True,
          saveFigs = True, Title = None,Temperature=20, p=-1):

    
    sep = ','
    headers = ['Frequency', 'PSD']
    
    
    min_AM2PM = []
    # min_AM2PM_bias = []
    temper = 0
    for folder in Folders:
        
        
        power_levels    = folder.split(sep='\\')[-1]
        print(power_levels)
        
        Power = float(power_levels.split(' ')[0])
        
        for_results = FOLDER+'\\'
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
            # print(AMPM)
            plt.close()
            
            number_str = pm_file.split()[0]  # split the filename into words and take the first word
            if 'V' in number_str: number_str=number_str[:-1]
            
            if AMtoPM_characterization:  
                bias = float(number_str)  # convert to float
                am_to_pm = float(AMPM)
                data.append((bias, am_to_pm))
            
            
            

            
            
            
        if AMtoPM_characterization:   

            plt.figure(int(2+p))
            df = pd.DataFrame(data, columns=['Bias', 'AM_to_PM'])
            df = df.sort_values(by='Bias')
            plt.plot(df.Bias, df.AM_to_PM,'-o',label=power_levels)
            plt.grid()
            plt.title(f'{Title} : {Temperature}')
            plt.legend()
            plt.xlabel('Bias [V]')
            plt.ylabel('AM to PM suppression [dB]')
            plt.grid(visible=True, which='major', color='lightgrey', linestyle='-')  # style of major grid lines
            plt.grid(visible=True, which='minor', color='lightgrey', linestyle='--')
            plt.ylim([-60,15])
            plt.xlim([2,20])
            
            # Find the minimum value of am_to_pm
            min_am_to_pm = min(data, key=lambda x: x[1])
            
            # Extract the am_to_pm value and the corresponding bias
            min_am_to_pm_value, min_am_to_pm_bias = min_am_to_pm
            
            min_AM2PM.append((Power, min_am_to_pm_value, min_am_to_pm_bias))
            

            
            
            if saveFigs: plt.savefig(results_folder+'\\'+'AMtoPM_sup_'+str(Temperature)+'.png')
    
    min_AM2PM_dataframe = pd.DataFrame(min_AM2PM,columns=['OpticalPower','min_AM2PM_value','bias'])
    
    # plt.figure(30)
    # plt.plot(min_AM2PM_dataframe.min_AM2PM_value,min_AM2PM_dataframe.bias,'o-',label=f'{Temperature}')
    # plt.legend()
    
    return min_AM2PM_dataframe,df.AM_to_PM, df.AM_to_PM.iloc[-1]
            
            
    