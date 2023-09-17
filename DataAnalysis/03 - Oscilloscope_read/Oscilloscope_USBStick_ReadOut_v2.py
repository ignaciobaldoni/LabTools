# -*- coding: utf-8 -*-
"""
Created on Wed May 13 10:44:38 2020

@author: ibaldoni
"""

import matplotlib.pyplot as plt

plt.rc('xtick', labelsize=17) 
plt.rc('ytick', labelsize=17) 
plt.rcParams.update({'font.size': 17})
plt.rcParams['figure.figsize'] = (14, 10)

import pandas as pd
import warnings
warnings.filterwarnings("ignore")

plot_oscilloscope   = True
Containing_folder = '\\1 - raw_data'

import os
directory_data = os.getcwd()+Containing_folder  
path, dirs, files = next(os.walk(directory_data))

exceptions_in = ['.csv']

for i in files:
    if all((ele_in in i) for ele_in in exceptions_in):

        print(i)
        med=pd.read_csv(directory_data +'/' + i)        
        med=med.drop(med.index[0])  
        
        
        if len(list(med))>=2:
            string_column1 = str(list(med)[1])
            Columns = {"x-axis":"time", 
                        string_column1:"Channel1"}    
            
        if len(list(med))>=3:
            string_column2 = str(list(med)[2])
            Columns = {"x-axis":"time", 
                        string_column1:"Channel1", 
                        string_column2:"Channel2"}
            
        if len(list(med))>=4:
            string_column3 = str(list(med)[3])
            Columns = {"x-axis":"time", 
                        string_column1:"Channel1",
                        string_column2:"Channel2" ,
                        string_column3:"Channel3"}
        
        if len(list(med))>=5:
            string_column4 = str(list(med)[4])
            Columns = {"x-axis":"time", 
                        string_column1:"Channel1",
                        string_column2:"Channel2" ,
                        string_column3:"Channel3" ,
                        string_column4:"Channel4"}
            
            
        med = med.rename(columns=Columns)
        
        t = med.time
        t = t.astype(float)
        t = t*1e3
        
        Channel1 = med.Channel1.astype(float)
        if len(list(med))==3: Channel2 = med.Channel2.astype(float)
        if len(list(med))==4: Channel3 = med.Channel3.astype(float)
        if len(list(med))==5: Channel4 = med.Channel4.astype(float)
        

        # Plot the file
        if plot_oscilloscope == True:
            plt.figure()
            plt.plot(t,Channel1,label = 'Channel 1')
            if len(list(med))==3: plt.plot(t,Channel2,'-',label = 'Channel 2')
            if len(list(med))==4: plt.plot(t,Channel3,'-',label = 'Channel 3')
            if len(list(med))==5: plt.plot(t,Channel4,'-',label = 'Channel 4')
            plt.xlabel('Time [ms]')
            plt.ylabel('Voltage [V]')
            plt.grid()
            plt.legend()
            plt.title(str(i)[:-4])
            plt.savefig(str(i)+'.png')