# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 15:08:20 2022

@author: ibaldoni
"""

# OSA Read outs
import pandas as pd
import matplotlib.pyplot as plt

def OSA_MPQ(fileName,OSA_Calibration,SkipRow = 3):
    
    OSA_data = pd.read_csv(fileName+'.TXT', sep=",", header=None, skiprows = SkipRow)
    OSA_data.columns = ["wavelength", "PSD"]
    OSA_data = OSA_data[:1001]

    OSA_data.wavelength = OSA_data.wavelength.astype(float)
    OSA_data.PSD = OSA_data.PSD.astype(float)
    OSA_data.PSD = OSA_data.PSD+OSA_Calibration
    
    return OSA_data
    
    
def OSA_Severus(fileName,OSA_Calibration,SkipRow = 0):
    
    
    OSA_data = pd.read_csv(fileName+'.CSV', sep=",", header=None, skiprows = SkipRow)
    OSA_data.columns = ["wavelength", "PSD"]

    OSA_data.wavelength = OSA_data.wavelength.astype(float)
    OSA_data.PSD = OSA_data.PSD.astype(float)
    OSA_data.PSD = OSA_data.PSD+OSA_Calibration
    
    return OSA_data



