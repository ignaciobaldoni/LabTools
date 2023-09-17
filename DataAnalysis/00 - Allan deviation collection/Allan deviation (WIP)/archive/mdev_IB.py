# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 20:59:49 2023

@author: akordts edited by IB
"""

########## IMPORTS ##########
import allantools as at
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.constants import speed_of_light


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
def calcFreqData(df_Freqs,absFreqOffset,interval_ms,df_Freqs_diff = None,sign = 1):
    time_index = df_Freqs.index
    timeTags = np.arange(len(time_index))*(interval_ms/1000) # time in miliseconds
    absFreqs = np.array(df_Freqs.iloc[:,0])
    
    if df_Freqs_diff is not None:
        absFreqs_diff = np.array(df_Freqs_diff.iloc[:,0])
        absFreqs = np.abs(absFreqs- sign * absFreqs_diff)
    
    avgAbsFreq = absFreqs.mean()
    print('average measured frequency:\t{:.2e}'.format(avgAbsFreq)) 
    deltaFreqs = (absFreqs-avgAbsFreq)
        
    normFracFreqData = deltaFreqs/avgAbsFreq
    
    return timeTags,absFreqs,normFracFreqData, avgAbsFreq

# %% load and prepare freq data
def loadAndCorrectFreqData(
        dataFilePath,
        column_number,
        interval_ms,
        wavelength = 0,
        column_number_diff = None,
        sign = 1
        ):    
    
    # %% calulate offset
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

    if column_number_diff is not None:
        df_Freqs_diff = pd.read_csv(
                        dataFilePath,
                        delimiter = r"\s+",
                        header=None, 
                        skiprows=11, 
                        usecols=[column_number_diff], 
                        float_precision='high') 
        # prepare frequency data
        timeTags, absFreqs, normFracFreqData, avgAbsFreq = calcFreqData(df_Freqs,absFreqOffset,interval_ms,df_Freqs_diff,sign)
    else:
        # prepare frequency data
        timeTags, absFreqs, normFracFreqData, avgAbsFreq = calcFreqData(df_Freqs,absFreqOffset,interval_ms,df_Freqs_diff = None,sign = sign)
    
    avgAbsFreqOffset = avgAbsFreq + absFreqOffset
    
    return timeTags, absFreqs, normFracFreqData, avgAbsFreq, avgAbsFreqOffset

# %% calculate allan deviation
def  calculateAllanDeviation(
        normFracFreqData,
        interval_ms,
        avgAbsFreq,
        avgAbsFreqOffset
        ):   
    (t2, ad, ade, adn) = at.mdev(normFracFreqData, rate=1/(interval_ms*1e-3), data_type="freq", taus="decade") #for automatic generated timescales
    
    ad = ad * (avgAbsFreq)/(avgAbsFreqOffset)
    ade = ade * (avgAbsFreq)/(avgAbsFreqOffset)
      
    return t2,ad,ade

def plotFreqDevVsTime(
        normFracFreqData,
        avgAbsFreq,
        avgAbsFreqOffset,
        timeTags,
        plotPath_FreqDevVsTime
        ):
    yData = normFracFreqData * (avgAbsFreq)/(avgAbsFreqOffset)
    
    fig, ax1 = plt.subplots()
    ax1.plot(
            timeTags,
            yData
        )
    
    plt.grid(True, axis='both', which='both', linestyle='-')
    
    ax1.set_xlabel('time [s]')
    marginFactor = 1.05
    minVal = np.min(yData) * marginFactor
    maxVal = np.max(yData) * marginFactor 
    ax1.set_ylim(minVal, maxVal)
    ax1.set_ylabel('Fractional frequency deviation')
    
    ax2 = ax1.twinx()
    ax2.set_ylim(minVal * avgAbsFreqOffset , maxVal * avgAbsFreqOffset)
    ax2.set_ylabel('absolute frequency deviation [Hz]')
    
    plt.tight_layout()
    plt.savefig(plotPath_FreqDevVsTime, dpi = 150)
    

# %% plot allan dev
def plotAllanDev(
        t2, 
        ad,
        ade,
        avgAbsFreqOffset,
        plotPath_MADEV
        ):
    fig, ax1 = plt.subplots()
    ax1.errorbar(t2, ad, yerr=ade, marker='o')
    
    plt.loglog()
    
    plt.ylabel('MADEV')  # label of y axis    
    plt.grid(True, which='major', color='k',linestyle='-')  # style of major grid lines
    plt.grid(True, which='minor', color='grey', linestyle='--')  # style of minor grid lines
    
    plt.xlabel('Integration Time [s]') 
    
    marginFactor = 1.05
    minVal = np.min(ad) * marginFactor
    maxVal = np.max(ad) * marginFactor 
    
    ax2 = ax1.twinx()
    ax2.set_ylim(minVal * avgAbsFreqOffset , maxVal * avgAbsFreqOffset)
    ax2.set_ylabel('absolute frequency deviation [Hz]')
    
    plt.loglog()
    
    plt.tight_layout()
    plt.savefig(plotPath_MADEV, dpi = 300)


def createCombinedPlot(
        resultFolderPath,
        dataFilePath1,
        dataFilePath2,
        dataName,
        interval_ms,
        wavelength = 0,
        column_number = 3,
        column_number_diff = None):
    
    # %% define file information
    
    os.makedirs(resultFolderPath, exist_ok=True) 
    plotPath_MADEV = resultFolderPath + '\\'+dataName+'_MADEV.png'


    # %% load and prepare data file 1
    
    (timeTags, 
      absFreqs, 
      normFracFreqData, 
      avgAbsFreq, 
      avgAbsFreqOffset) = loadAndCorrectFreqData(dataFilePath1,
                                column_number,
                                interval_ms,
                                wavelength,column_number_diff)
    
    # %% calculate allan deviation file 1
    
    t2,ad,ade = calculateAllanDeviation(normFracFreqData,
                                        interval_ms,
                                        avgAbsFreq,
                                        avgAbsFreqOffset)
        
    # %% plot data file 1

    fig, ax1 = plt.subplots()
    ax1.errorbar(t2, ad, yerr=ade, marker='o')
        
    plt.loglog()
    
    plt.ylabel('MADEV')  # label of y axis
    
    plt.grid(b=True, which='major', color='k', linestyle='-')  # style of major grid lines
    plt.grid(b=True, which='minor', color='grey', linestyle='--')  # style of minor grid lines
    
    plt.xlabel('Integration Time [s]') 


    # %% load and prepare data file 2
    
    (timeTags, 
      absFreqs, 
      normFracFreqData, 
      avgAbsFreq, 
      avgAbsFreqOffset) = loadAndCorrectFreqData(dataFilePath2,
                                                column_number,
                                                interval_ms,
                                                wavelength,
                                                column_number_diff,
                                                sign = - 1)
    
    # %% calculate allan deviation file 2
    
    t2,ad,ade = calculateAllanDeviation(normFracFreqData,
                                        interval_ms,
                                        avgAbsFreq,
                                        avgAbsFreqOffset)        
    
    ax1.errorbar(t2, ad, yerr=ade, marker='o')   
    ax1.set_xlim([1e-3,1e2])
    ax1.legend(["Legend 1","Legend 2"])
    
    yLim = [3e-13,2e-12]
    ax1.set_ylim(yLim )
    
    ax2 = ax1.twinx()
    ax2.set_ylim( [yLim[0] * avgAbsFreqOffset,yLim[1] * avgAbsFreqOffset])
    
    ax2.set_ylabel('absolute frequency deviation [Hz]')
    
    plt.loglog()
    
    plt.tight_layout()
    plt.savefig(plotPath_MADEV, dpi = 300)
    
    plt.show()


    
def createPlot(resultFolderPath, dataFilePath, dataName, interval_ms,
               wavelength = 0, column_number = 3,column_number_diff = None):
    
    # %% define file information
    
    os.makedirs(resultFolderPath, exist_ok=True) 
    plotPath_FreqDevVsTime = resultFolderPath + '\\'+dataName+'_freqDevVsTime.png'
    plotPath_MADEV = resultFolderPath + '\\'+dataName+'_MADEV.png'
    
    # %% load and prepare data
    
    (
     timeTags, 
     absFreqs, 
     normFracFreqData, 
     avgAbsFreq, 
     avgAbsFreqOffset
    ) = loadAndCorrectFreqData(
            dataFilePath,
            column_number,
            interval_ms,
            wavelength,
            column_number_diff = None
            )

    save_madev_data_to_file(absFreqs, dataName)

    
    # %% plot fractional and abs frequency deviation 
    plotFreqDevVsTime(
            normFracFreqData,
            avgAbsFreq,
            avgAbsFreqOffset,
            timeTags,
            plotPath_FreqDevVsTime
            )
    
    
    # %% calculate allan deviation
    
    t2,ad,ade = calculateAllanDeviation(normFracFreqData, interval_ms,
                                        avgAbsFreq, avgAbsFreqOffset)
    
    # %% plot allan fractional deviation
    
    plotAllanDev(t2, ad, ade, avgAbsFreqOffset, plotPath_MADEV)



if __name__ == '__main__':
    
    dataFolderpath=r"\\menloserver\MFS\99-Data_Warehouse\01-User_Folders-Private\i.baldoni\2023 - Ultrastable Microwaves\01 - UMS Labtools (WIP)\Allan deviation (WIP)\Old\correctedData"
    
    filenames=['211105_11_Frequ.txt']  # just to debug
    
    filepath = dataFolderpath + '\\' + filenames[0]
            
    dataFilePath = dataFolderpath + '\\' + filenames[0]
    
    resultsFolderpath = r"C:\Users\ibaldoni\Desktop\Allan deviation\PRUEBA"
    
    dataName = 'beat_ORS-FLC'
    wavelength = 1542e-9
    createPlot(resultsFolderpath,dataFilePath,dataName,1,wavelength,column_number = 3)
    
    dataName = 'beat_RIO-FLC'
    wavelength = 1542e-9
    createPlot(resultsFolderpath,dataFilePath,dataName,1,wavelength,column_number = 4)
