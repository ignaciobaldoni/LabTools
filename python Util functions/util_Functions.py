# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 14:31:49 2023

@author: ibaldoni
"""


import pandas as pd
import numpy as np
from scipy import integrate, fft
import os



#%% Readout from CSV files taken with a USB stick

def readCXA_usb(folder, fileName,Names= ['Frequency','Variable']):
    print('reading cxa output from USB stick...')
    
    
    joined_path = os.path.join(folder, fileName)
    
    CXA_output = pd.read_csv(joined_path,
                             skiprows=61,
                             sep=',', 
                             names = Names)
    
    return CXA_output




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

# def PhaseStation_PhaseNoise_csv(folder,fileName):
    
#     if '.csv' not in fileName: 
#         raise ValueError
#         print('Wrong file type')
#     else:
#         phase_Station_output = pd.read_csv(folder+fileName, sep=',', names= ['Frequency','PSD'])
        

#     return phase_Station_output.Frequency, phase_Station_output.PSD
        

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

def Watt_to_dBm(value_in_Watt):
    return 10*np.log10(1e3*value_in_Watt)


#%% Noises contribution
def dbm_to_mw(dbm):
    """
    Converts dBm (decibel-milliwatts) to mW (milliwatts).
    
    Args:
        dbm (float): The power value in dBm.
    
    Returns:
        float: The power value in mW.
    """
    return 10 ** (dbm / 10)


def thermal_noise(MW_Power = 0, unit = 'dBm'):
    '''To be fully understood... (from Merits of PM Noise Measurement Over Noise
    Figure: A Study at Microwave Frequencies (2006)
    
    Microwave power is in dBm
    '''
    
    if unit == 'dBm':
        Power = dbm_to_mw(MW_Power)
    if unit == 'mW':
        Power = MW_Power
    
    boltzmann_constant = 1.38064852e-23

    RoomTemperature = 300

    L_f = boltzmann_constant * RoomTemperature/2/Power

    Lf_dBc_Hz = 10*np.log10(L_f)
    print('Thermal noise:', Lf_dBc_Hz,'dBc/Hz')
    
    return Lf_dBc_Hz



def shot_noise_cw(nu  = 194.4e12, Optical_Power = 1e-3, Responsitivity = 0.9):
    
    # Natural constants
    electric_charge = 1.602e-19
    planck_constant = 6.62607015e-34
    Load_resistance = 50
    
    photocurrent = Responsitivity * Optical_Power 
    print(f'Photocurrent \t= {photocurrent*1E3} mA')
    
    shot_noise_current = 2*electric_charge*Responsitivity*Optical_Power
   
    shot_noise_power = shot_noise_current*Load_resistance
    # print(f'shot noise power at cw = {shot_noise_power} W')

    shot_noise_power_dBc_Hz = 10*np.log10(shot_noise_power*1e3)
    print(f'Shot noise (cw) = {shot_noise_power_dBc_Hz:.2f} dBc/Hz')
    
    return shot_noise_power_dBc_Hz, shot_noise_power
    

def shot_noise_pulsed(nu  = 194.4e12, Optical_Power = 1e-3, Responsitivity = 0.9, MW_signal=10e9, 
                      tau = 100e-15, Harmonic_number = 10e9,
                      AM_to_PM_suppression = 0, Load_resistance = 50):
    
    '''Following the paper from Quinlan et al. (2013)
    Analysis of shot noise in the detection
        of ultrashort optical pulse trains
    '''
    
    if AM_to_PM_suppression == 0: print('AM to PM conversion unknown')
    if AM_to_PM_suppression != 0: print(f'AM to PM conversion: {AM_to_PM_suppression} dB')
    
    # carrier_power_in_dBm = 10*np.log10(Optical_Power*1e3)
    # print(f'Power in dBm = {carrier_power_in_dBm}')
    
    tau_g = tau/(2*(np.sqrt(np.log(2))))
    # print(f'tau_g = {tau_g*1e15} fs')
    
    # Natural constants
    electric_charge = 1.602e-19
    # planck_constant = 6.62607015e-34
    
    
    photocurrent = Responsitivity * Optical_Power 
    print(f'Photocurrent \t= {photocurrent*1E3} mA')
    
    
    L_pm = (electric_charge*(2*np.pi*Harmonic_number*tau_g)**2)/(2*photocurrent)
   
    # print(f'shot noise power = {shot_noise_power} W')

    L_pm_dBc_Hz = 10*np.log10(L_pm)#*1e3)-carrier_power_in_dBm
    print(f'Shot noise (PN) = {L_pm_dBc_Hz:.2f} dBc/Hz')
    
    L_am = electric_charge/photocurrent
    L_am_dBc_Hz = 10*np.log10(L_am)
    print(f'Shot noise (AM) = {L_am_dBc_Hz:.2f} dBc/Hz')
    
    
    
    SN_AM_to_PM_suppression = L_am_dBc_Hz - AM_to_PM_suppression
    
    print(f'Shot noise (AM to PM sup.) = {SN_AM_to_PM_suppression:.2f} dBc/Hz')
    
    return L_am_dBc_Hz, L_pm_dBc_Hz, SN_AM_to_PM_suppression

def jitter_calc(psd, freqs,carrier):
       

    rms_phase_jitter = np.sqrt(2*10**(psd/10)) #[rad]
    
    rms_jitter_sec = rms_phase_jitter/(2*np.pi*carrier)
    
    int_pn_rad = np.abs(integrate.cumtrapz(rms_phase_jitter[::-1],np.log10(freqs[::-1])))
    int_pn_sec = np.abs(integrate.cumtrapz(rms_jitter_sec[::-1],np.log10(freqs[::-1])))
    
    return int_pn_rad, int_pn_sec




    




# shot_noise_level_dBcHz, _ , _= shot_noise_pulsed(Optical_Power = 8e-3, 
#                                               Responsitivity=0.3,
#                                               Harmonic_number= 10e9,
#                                               tau=75e-15,
#                                               AM_to_PM_suppression=30)

# shot_noise_level_dBcHz, _ = shot_noise_cw(Optical_Power = 8e-3, 
#                                               Responsitivity=0.3)