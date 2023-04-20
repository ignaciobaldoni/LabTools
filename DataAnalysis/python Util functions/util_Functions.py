# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 14:31:49 2023

@author: ibaldoni
"""


import pandas as pd


#%% Readout from CSV files taken with a USB stick

def readCXA_usb(folder, fileName):
    print('reading cxa output from USB stick...')
    
    CXA_output = pd.read_csv(folder+fileName,
                             skiprows=54,
                             sep=',', 
                             names = ['Frequency','Variable'])
    
    return CXA_output.Frequency, CXA_output.Variable




def readOSA_usb(folder, fileName):
    print('reading OSA output from USB stick...')
    
    OSA_output = pd.read_csv(folder+fileName,
                             skiprows=29,
                             sep=',', 
                             names = ['Wavelength','Variable'])
    
    Wavelength = OSA_output.Wavelength.astype(float)
    Variable = OSA_output.Variable.astype(float)
    
    return Wavelength, Variable


#%% Phase stations 53100a readout from csv exported files. Note that it is not for
### .tim files.

def PhaseStation_PhaseNoise_csv(folder,fileName):
    
    if '.csv' not in fileName: 
        raise ValueError
        print('Wrong file type')
    else:
        phase_Station_output = pd.read_csv(folder+fileName, sep=',', names= ['Frequency','PSD'])

    return phase_Station_output.Frequency, phase_Station_output.PSD
        

def PhaseStation_adev_csv(folder,fileName):
    
    if '.csv' not in fileName: 
        raise ValueError
        print('Wrong file type')
    else:
        phase_Station_output = pd.read_csv(folder+fileName,
                            delimiter = ",",
                            names=['taus', 'adev'], 
                            float_precision='high')

    return phase_Station_output.taus, phase_Station_output.adev


#%% Some simple functions for fun

def units(x):
    
    if x<1e-3: unit = 'm'; factor = 1e-3
    if x<1e-6: unit = 'μ'; factor = 1e-6
    if x<1e-9: unit = 'n'; factor = 1e-9
    if x<1e-12: unit = 'p'; factor = 1e-12
    if x<1e-15: unit = 'f'; factor = 1e-15
        
    if x<1: unit = 'm'; factor = 1e-3
    if x>=1 and x<1e3: unit = ''; factor = 1
    if x>=1e3: unit = 'k'; factor = 1e3
    if x>=1e6: unit = 'M'; factor = 1e6
    if x>=1e9: unit = 'G'; factor = 1e9
    if x>=1e12: unit = 'T'; factor = 1e12
    
    
    return unit, factor