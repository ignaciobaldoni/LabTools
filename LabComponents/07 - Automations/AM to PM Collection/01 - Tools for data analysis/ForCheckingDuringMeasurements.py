# -*- coding: utf-8 -*-
"""
Created on Tue May 30 21:36:20 2023

@author: ibaldoni
"""

from AM2PM_function_v2 import AM2PM
# from function_Automation_for_tim_files import Automation_for_tim_files


import os
# %% Personal functions 
import sys
sys.path.append(r'\\menloserver\MFS\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\python Util functions')
from Plot_aux_functions import Plot_parameters
Plot_parameters(width=9)

#%% Run the whole analysis
               
FOLDER = (r'\\menloserver\mfs\03-Operations\03-Production\05-AU_PA'+\
          r'\AU07627_AU06630-RMA-Syncro\05_2023 - Photodiodes characterization'+\
          r'\HHI Fraunhoffer (new)\AM to PM NIST\TEST FOR AUTOMATION AU7434')

folders = []
for file in os.listdir(FOLDER):
    # Check if file has .csv extension
    if file.endswith("mW"):
        folders.append(file)

print(folders)
        
        
# folders = ['5.77 mW','5.63 mW']
    
thema = '\\'


    
    
# Title = FOLDER.split('\\')[-1]
# Temperature = thema.split('\\')[1]



subfolders = [FOLDER + thema + folder for folder in folders]



# Automation_for_tim_files(FOLDER,subfolders)

_, data, amtopm = AM2PM(FOLDER,
    subfolders, 
    AMtoPM_characterization = True,
    plot_figures = False,
    saveFigs = True, 
    Title = 'Test for automations',
    Temperature=23, p=0)

# print(amtopm)
# import numpy as np
# import matplotlib.pyplot as plt
# plt.figure()
# diferencia = np.diff(data)
# plt.plot(data.bias, diferencia,'o')


            
