# -*- coding: utf-8 -*-
"""
Created on Tue May 30 21:36:20 2023

@author: ibaldoni
"""

from AM2PM_function_v2 import AM2PM
# from function_Automation_for_tim_files import Automation_for_tim_files

import numpy as np
import matplotlib.pyplot as plt

import os
# %% Personal functions 
import sys
sys.path.append(r'\\menloserver\MFS\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\python Util functions')
from Plot_aux_functions import Plot_parameters
Plot_parameters(width=9)

#%% Run the whole analysis
               
 
FOLDER = (r'\\menloserver\mfs\03-Operations'+\
          r'\02-DCP\01-DCP_Management\01-Gruppenmanagement'+\
          r'\UMS\06_Measurements TBD\20230821 - Hensoldt Photodiodes characterization\Coherent VPDV2120 PD spectrum\AM to PM')

    
    

folders = []
for file in os.listdir(FOLDER):
    # Check if file has .csv extension
    if file.endswith(" mW"):
    #.startswith('17'): #
        folders.append(file)

print(folders)
        
        
folders = ['7.80 mW','13.00 mW','17.45 mW']
    
thema = '\\'





subfolders = [FOLDER + thema + folder for folder in folders]





_, data, lastAM2PM ,biases = AM2PM(FOLDER,
    subfolders, 
    AMtoPM_characterization = True,
    plot_figures = False,
    saveFigs = False, 
    Title = 'Test with amplifiers',
    Temperature='' , p=0)




            
