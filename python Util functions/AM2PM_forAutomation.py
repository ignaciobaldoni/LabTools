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



    

def AM2PM(folder):

    
    sep = ','
    headers = ['Frequency', 'PSD']
    
        
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
        AMPM = makeTable(pm_df['Frequency'], difference, fig, print_freqs=[10000])
        plt.close()
        
        number_str = pm_file.split()[0]  # split the filename into words and take the first word
        if 'V' in number_str: number_str=number_str[:-1]
        
        bias = float(number_str)  # convert to float
        am_to_pm = float(AMPM)
        data.append((bias, am_to_pm))

        
    df = pd.DataFrame(data, columns=['Bias', 'AM_to_PM'])
    df = df.sort_values(by='Bias')
            

    
    return df.AM_to_PM.iloc[-1]

if __name__ == '__main__':
    folder = (r'\\menloserver\mfs\03-Operations\03-Production\05-AU_PA'+\
              r'\AU07627_AU06630-RMA-Syncro\05_2023 - Photodiodes characterization'+\
              r'\HHI Fraunhoffer (new)\AM to PM NIST\TEST FOR AUTOMATION\5.33 mW')
    last_am2pm = AM2PM(folder)
    print(last_am2pm)
            