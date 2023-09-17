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
               
 
FOLDER = (r'\\menloserver\mfs\99-Data_Warehouse'+\
          r'\02-User_Folders-Public\i.baldoni'+\
          r'\HHI AM to PM before RS August\AM to PM')
    
FOLDER = r'\\menloserver\mfs\03-Operations\03-Production\05-AU_PA\AU07751-FC1500-250-NOVA-NPL-Scotland\03-Endabnahme\08-Mikrowelle\04-AMPM Suppression\AM to PM'
    

folders = []
for file in os.listdir(FOLDER):
    # Check if file has .csv extension
    if file.endswith(" mW"):
        folders.append(file)

print(folders)
        
        
# folders = ['10.00 mW','unlocked 10.00 mW','9.97 mW',]
    
thema = '\\'


    
    
# Title = FOLDER.split('\\')[-1]
# Temperature = thema.split('\\')[1]



subfolders = [FOLDER + thema + folder for folder in folders]



# Automation_for_tim_files(FOLDER,subfolders)

_, data, lastAM2PM ,biases = AM2PM(FOLDER,
    subfolders, 
    AMtoPM_characterization = True,
    plot_figures = False,
    saveFigs = True, 
    Title = 'Test for automations',
    Temperature=22.5, p=0)

min_data = min(data)
min_index = data.iloc[np.where(data==min(data))].index[0]
min_bias = biases[min_index]

print()
text = f'Max. suppression:{min(data)} dB\nat {min_bias} V'
plt.text(2.5,-45,text)
plt.ylim(-50,50)
plt.savefig('AM_to_PM_Suppression.png',dpi = 300)

            
