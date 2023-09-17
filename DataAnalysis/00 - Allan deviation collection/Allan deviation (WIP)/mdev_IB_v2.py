
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 20:59:49 2023

@author: ibaldoni
"""
#%% Personal functions 
import sys
sys.path.append(r'\\menloserver\MFS\99-Data_Warehouse\01-User_Folders-Private\i.baldoni\python Util functions')
from Plot_aux_functions import Plot,Plot_parameters, Plot_yy # Import all functions from the script
Plot_parameters()
from util_Functions import units


#%% ######### IMPORTS ##########
import allantools as at
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import os
from scipy.constants import speed_of_light




# %% Save file function

def save_madev_data_to_file(freq_data, file_name):

    mean_freq_avg = np.abs(freq_data.mean())
    delta_freqs = (freq_data - mean_freq_avg)

    wavelength = 1542 * 1e-9
    abs_freq = speed_of_light / wavelength
    norm_frac_freq_data = delta_freqs / abs_freq

    c = [np.arange(len(norm_frac_freq_data))*0.001, norm_frac_freq_data]

    filepath = file_name
    with open(filepath, "w") as file:
        for x in zip(*c):
            file.write("{0}\t{1}\n".format(*x))



# %% support functions
def calcFreqData(df_Freqs,absFreqOffset,interval_sec,df_Freqs_diff = None,sign = 1):
    time_index = df_Freqs.index
       
    timeTags = np.arange(len(time_index))*interval_sec #*(interval_sec/1000) # time in miliseconds
    
    print(f'Intervals of {interval_sec}s')
    
    # absFreqs = np.array(df_Freqs.iloc[:,0])
    
    # if df_Freqs_diff is not None:
    #     absFreqs_diff = np.array(df_Freqs_diff.iloc[:,0])
    #     absFreqs = np.abs(absFreqs- sign * absFreqs_diff)
    

    # avgAbsFreq = absFreqs.mean()
    
    # avgAbsFreq_MHz = avgAbsFreq/1e6
    # print(f'average measured frequency:\t{avgAbsFreq_MHz:.2f} MHz') 
    
    # deltaFreqs = (absFreqs-avgAbsFreq)
        
    # normFracFreqData = deltaFreqs/avgAbsFreq
    avgAbsFreq = 1
    absFreqs = 1

    normFracFreqData = df_Freqs
    
    return timeTags,absFreqs,normFracFreqData, avgAbsFreq

# %% load and prepare freq data
def loadAndCorrectFreqData(
        dataFilePath,
        column_number,
        interval_sec,
        wavelength = 0,
        column_number_diff = None,
        sign = 1
        ):    
    
    # calulate offset
    if wavelength > 0:
        absFreqOffset = speed_of_light / wavelength
    else:
        absFreqOffset = 0
    
    # reads the csv file
    df_Freqs = pd.read_csv(
                    dataFilePath,
                    delimiter = r"\s+",
                    header=None, 
                    skiprows=11, 
                    usecols=[column_number], 
                    float_precision='high')
    
    # print(df_Freqs.head())

    if column_number_diff is not None:
        df_Freqs_diff = pd.read_csv(
                        dataFilePath,
                        delimiter = r"\s+",
                        header=None, 
                        skiprows=11, 
                        usecols=[column_number_diff], 
                        float_precision='high') 
        # prepare frequency data
        timeTags, absFreqs, normFracFreqData, avgAbsFreq = calcFreqData(df_Freqs,absFreqOffset,interval_sec,df_Freqs_diff,sign)
        
        print(normFracFreqData)

    else:
        # prepare frequency data
        timeTags, absFreqs, normFracFreqData, avgAbsFreq = calcFreqData(df_Freqs,absFreqOffset,interval_sec,df_Freqs_diff = None,sign = sign)
    
    avgAbsFreqOffset = avgAbsFreq + absFreqOffset
    
    freq_thz = avgAbsFreqOffset / 1e12  # convert Hz to THz

    print(f'Average absolute frequency offset = {freq_thz:.3f} THz')
    
    return timeTags, absFreqs, normFracFreqData, avgAbsFreq, avgAbsFreqOffset

# %% calculate allan deviation
def  calculateAllanDeviation(
        normFracFreqData,
        interval_sec,
        avgAbsFreq,
        avgAbsFreqOffset
        ):   

    
    Rate = 1/interval_sec
    
    (t2, ad, ade, adn) = at.mdev(normFracFreqData, rate=Rate, data_type="freq", taus="decade") #for automatic generated timescales
    
    ad = ad #* (avgAbsFreq)/(avgAbsFreqOffset)
    ade = ade #* (avgAbsFreq)/(avgAbsFreqOffset)
      
    return t2,ad,ade


# %% Plot Frequency vs time
def plotFreqDevVsTime(
        normFracFreqData,
        avgAbsFreq,
        avgAbsFreqOffset,
        timeTags,
        plotPath_FreqDevVsTime
        ):
    yData = normFracFreqData * (avgAbsFreq)/(avgAbsFreqOffset)
    
    marginFactor = 1.05
    minVal = np.min(yData) * marginFactor
    maxVal = np.max(yData) * marginFactor 
    abs_freq_dev = np.linspace(minVal * avgAbsFreqOffset , maxVal * avgAbsFreqOffset,len(yData))
    
    
    Plot_yy(timeTags,yData,abs_freq_dev,num = 5,alpha_1 = 0.35, alpha_2=0.,
            xLabel = 'time [s]',yLabel_1='Fractional frequency deviation',
            yLabel_2 = 'Absolute frequency deviation [Hz]')


# %% plot allan dev
def plotAllanDev(
        t2, 
        ad,
        ade,
        avgAbsFreqOffset,
        plotPath_MADEV
        ):
    
    marginFactor = 1.05
    minVal = np.min(ad) * marginFactor
    maxVal = np.max(ad) * marginFactor 
    abs_freq_dev = np.linspace(minVal * avgAbsFreqOffset , maxVal * avgAbsFreqOffset,len(ad))
    
    Plot_yy(t2, ad, abs_freq_dev, 
            num = 5, alpha_2= 0., loglog = True, filename = 'plotPath_MADEV', marker = 'o',
            xLabel = 'Integration time [s]', yLabel_1='Mod $\sigma( \\tau )$',
            yLabel_2 = 'Absolute frequency deviation [Hz]') 
    print('For errorbar, use plt.errorbar(t2, ad, yerr=ade, marker="o")')



# %% Run the script for creating the plots of interest
def createPlot(resultFolderPath, dataFilePath, dataName, interval_sec,
               wavelength = 0, column_number = 3,column_number_diff = None):
    
    # define file information
    
    os.makedirs(resultFolderPath, exist_ok=True) 
    plotPath_FreqDevVsTime = resultFolderPath + '\\'+dataName+'_freqDevVsTime.png'
    plotPath_MADEV = resultFolderPath + '\\'+dataName+'_MADEV.png'
    
    # load and prepare data
    
    (timeTags,absFreqs, normFracFreqData,avgAbsFreq, 
      avgAbsFreqOffset) = loadAndCorrectFreqData(dataFilePath,
                                column_number,
                                interval_sec,
                                wavelength,
                                column_number_diff = None
                                )

    # save_madev_data_to_file(absFreqs, dataName)

    
    # plot fractional and abs frequency deviation 
    plotFreqDevVsTime(
            normFracFreqData,
            avgAbsFreq,
            avgAbsFreqOffset,
            timeTags,
            plotPath_FreqDevVsTime
            )
    
    
    # calculate allan deviation
    t2,ad,ade = calculateAllanDeviation(normFracFreqData, interval_sec,
                                        avgAbsFreq, avgAbsFreqOffset)
    
    # plot allan fractional deviation
    plotAllanDev(t2, ad, ade, avgAbsFreqOffset, plotPath_MADEV)


# %% Run the script
# if __name__ == '__main__':
       
dataFolderpath = r"\\menloserver\MFS\03-Operations\03-Production\05-AU_PA\AU07434-SmartComb-PMWG_Hensoldt\03-Endabnahme\06-OL-Kammvergleich\calculate PSD Optical limit\\"

dataFolderpath = r'C:\Users\ibaldoni\Desktop\TimeLab files\FXE mdev'

interval_sec = 0.1
  



filenames = ['211008_1_Frequ.txt']#,'230401_1_Frequ.txt','230402_1_Frequ.txt','230403_1_Frequ.txt']


for i in filenames:
    filepath = dataFolderpath + '\\' + i
            
    dataFilePath = dataFolderpath + '\\' + i
    
    
    
    resultsFolderpath = r"\\menloserver\MFS\99-Data_Warehouse\01-User_Folders-Private\i.baldoni\2023 - Ultrastable Microwaves\01 - UMS Labtools (WIP)\Allan deviation (WIP)\Results"
    
    dataName = f'beat_ORS-FLC_{i}'
    wavelength = 1542e-9
    
    interval_sec = 0.1
    
    createPlot(resultsFolderpath,dataFilePath,dataName,interval_sec,wavelength,column_number = 3)
    

print('OBJETIVO: RECUPERAR EL RESULTADO DE BR')
    

