# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 13:27:18 2020

@author: ibaldoni
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import os.path

#%% 
save_path   =  '//menloserver/MFS/03-Operations/02-DCP/03-Entwicklungsprojekte/'
project = '9552-KECOMO/'
main_folder = '52-Messergebnisse/'
fileType = '.csv'

in_raw_data = '1-Raw Data/' 
in_results  = '3-Results/'

measurementPurposeShort = '_Soliton_spectrums_in_polished_chips/'

fileType_img = '.png' 

year = dt.datetime.today().year
month = dt.datetime.today().month
day =  dt.datetime.today().day

month = '0'+str(month) if len(str(month)) == 1 else month
day = '0'+str(day) if len(str(day)) == 1 else day

### Today
date = str(year)+str(month)+str(day)

size_fig    = (12,8)
fig_resolution = 100    # a.k.a., dpi
skipRow = 41

p=0
Figsize = (12,8)
Roll = 2
for jj in range(0,7):
    
    subfolder = 'D63_2_12GHz/' if jj >= 4 else 'D63_03_12GHz_F4_C12/'
    file = 'W000'
    
    fileName = os.path.join(save_path, project+ \
                                    main_folder+\
                                    date +  \
                                    measurementPurposeShort + \
                                    in_raw_data +  \
                                    subfolder + \
                                    file +  \
                                    str(jj) + \
                                    fileType)   
    print(fileName)
    header_list = ["Wavelength", "Power"]
    med=pd.read_csv(fileName,skiprows = skipRow, names=header_list)
    plt.figure(num=jj, figsize=size_fig, dpi=fig_resolution) 
    plt.plot(med.Wavelength,med.Power)
    plt.title(subfolder[:-1],fontsize=20)
    plt.xlabel('Wavelength (nm)',fontsize=20)
    plt.ylabel('Power (dBm/nm)',fontsize=20)    
    plt.ylim(-70,0)
    plt.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.5)
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)


    saveResults_OSA = os.path.join(save_path, project+ \
                                main_folder+ \
                                date +  \
                                measurementPurposeShort + \
                                in_results +  \
                                subfolder[:-1]+'_'+\
                                str(jj) + \
                                fileType_img) 
    
    plt.savefig(saveResults_OSA)