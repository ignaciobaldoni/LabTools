# -*- coding: utf-8 -*-
"""
Created on Tue May 30 21:36:20 2023

@author: ibaldoni
"""

from AM2PM_function import AM2PM
from function_Automation_for_tim_files import Automation_for_tim_files

import matplotlib.pyplot as plt


# %% Personal functions 
import sys
sys.path.append(r'\\menloserver\MFS\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\python Util functions')
from Plot_aux_functions import Plot_parameters
Plot_parameters(width=9)

#%% Run the whole analysis
               
FOLDER = (r'\\menloserver\mfs\03-Operations\03-Production\05-AU_PA'+\
          r'\AU07627_AU06630-RMA-Syncro\05_2023 - Photodiodes characterization'+\
          r'\HHI Fraunhoffer (new)\AM to PM NIST\Temperature dependence measurements')


Temps = [20.5,21.5,22.5,25.0,28.1]
# Temps = [20.5,28.1]
p=0
for temperatures in Temps:
    
    thema = '\\'+str(temperatures)+' degrees'

    folder1 = r'\3 mW'
    folder2 = r'\4 mW'
    folder3 = r'\5 mW'
    folder4 = r'\6 mW'
    folder5 = r'\7 mW'
    folder6 = r'\8 mW'
    folder7 = r'\9 mW'
        
        
    Title = FOLDER.split('\\')[-1]
    Temperature = thema.split('\\')[1]
    
    
    
    subfolders = [FOLDER + thema + folder for folder in [folder1, 
                                                    folder2, 
                                                      folder3, 
                                                      folder4,
                                                      folder5, 
                                                      folder6,
                                                      folder7,
                                                 ]]
    
    
    Automation_for_tim_files(FOLDER,subfolders)
    
    min_AM2PM_dataframe = AM2PM(FOLDER,
        subfolders, 
        AMtoPM_characterization = True,
        plot_figures = False,
        saveFigs = True, 
        Title = Title,
        Temperature=Temperature, p=p)
    p+=1




            
