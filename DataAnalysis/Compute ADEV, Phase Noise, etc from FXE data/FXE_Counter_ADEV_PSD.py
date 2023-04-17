# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 14:44:23 2023

@author: ignacio

This Python script is designed to process frequency data from a FXE counter
and calculate different parameters of interest such as 
Allan deviation, frequency noise power spectral density, phase and phase noise. 

For using, simply select the FXE file and the parameters to be analyzed at the 
end of this script
"""


#%% Import necessary modules

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import allantools as at
from scipy.constants import speed_of_light
import matplotlib.mlab as mplm
import scipy.signal

#%% Load files from FXE Counter
def load_FXEdata(folder,file,channels):
    print('Loading FXE data')
        
    df_Freqs = pd.read_csv(folder+file,
                        delimiter = r"\s+",
                        header=None, 
                        skiprows=1, 
                        usecols=channels, 
                        float_precision='high')
    return df_Freqs

#%% Load files from Phase Station (WIP!!)
def load_53100aStation(folder,file):
    
    df_Freqs = pd.read_csv(folder+file,
                        delimiter = ",",
                        header=None, 
                        skiprows=1, 
                        float_precision='high')
    return df_Freqs

def plot_Frequency(df_Freqs,channels,channel_names, wavelength = 1542.14e-9, 
                   freq_rate = 10):
    
    num_plots = len(channels)
    t0 = 1/freq_rate
    
    fig, axes = plt.subplots(num=7, nrows=num_plots, 
                             ncols=1, #gridspec_kw={'hspace': 0.10},
                             sharex=True)
    
    p=0
    for i in channels:
        
        normFracFreq = np.array(df_Freqs[i])/(speed_of_light/wavelength)
        
        lc = len(normFracFreq)
        Time = np.linspace(0,t0*lc, lc)
        
        axes[p].plot(Time,normFracFreq, label = f'{channel_names[p]}')
        axes[p].grid(visible=True, which='both')
        axes[p].legend()
        
        p+=1
    
    axes[p-1].set_xlabel('Time [s]')
    fig.supylabel('Frequency [Hz]')
    if saveFigs: plt.savefig('Frequency_plot.png')
        
        
        
        

# %% Allan deviation from FXE counter

def calcAllanDev(df_Freqs, channels, channel_names, freq_rate = 1/0.1, 
             TCH = False, 
             wavelength = 1542.14e-9, Type = 'm'):
    print('Calculating Allan Deviation')
        
    for i in channels:        
        
        normFracFreq = np.array(df_Freqs[i])/(speed_of_light/wavelength)
        
        if Type == 'm' : 
            (t2, ad, ade, adn) = at.mdev(normFracFreq, rate=freq_rate, data_type="freq", taus="decade")
            allan_type = 'Modified '
        if Type == 'a' : 
            (t2, ad, ade, adn) = at.adev(normFracFreq, rate=freq_rate, data_type="freq", taus="decade")
            allan_type = ''
        if Type == 'oa' : 
            (t2, ad, ade, adn) = at.oadev(normFracFreq, rate=freq_rate, data_type="freq", taus="decade")
            allan_type = 'Overlapping '
        if Type == 'h' : 
            (t2, ad, ade, adn) = at.hdev(normFracFreq, rate=freq_rate, data_type="freq", taus="decade")
            allan_type = 'Hadamard '
        
        plt.figure(1)
        
        plt.errorbar(t2,ad, yerr=ade, marker='o')
        plt.loglog()
        plt.title('overall stability')
        plt.grid(visible=True, which='major', color='lightgrey', linestyle='-')  # style of major grid lines
        plt.grid(visible=True, which='minor', color='lightgrey', linestyle='--')# style of minor grid lines
        plt.xlabel('Integration Time (s)') # label of x axis
        plt.ylabel(allan_type+'ADEV')   # label of y axis
        plt.legend(channel_names)
        if saveFigs: plt.savefig('Allan_deviation_plot.png')
    
    
    
    if TCH:
        print('Calculating Three Cornered Hat')
        stability = pd.DataFrame()
        
        if len(channels) != 3:
            print('Must be 3 channels for a TCH')
            exit()
        
        for i in channels:
            
            normFracFreq = np.array(df_Freqs[i])/(speed_of_light/wavelength)
            
            (t2, stability[channels.index(i)], ade, adn) = at.mdev(normFracFreq, rate=freq_rate, data_type="freq", taus="decade")
        
        stability_unit = np.empty([len(channels),len(t2)])
        stability_unit[0] = np.sqrt(0.5*(stability[0]**2 + stability[1]**2 -stability[2]**2))
        stability_unit[1] = np.sqrt(0.5*(stability[0]**2 + stability[2]**2 -stability[1]**2))
        stability_unit[2] = np.sqrt(0.5*(stability[1]**2 + stability[2]**2 -stability[0]**2))
        
         
        plt.figure(2)
        plt.title('overall TCH stability')
        plt.grid(visible=True, which='major', color='lightgrey', linestyle='-')  # style of major grid lines
        plt.grid(visible=True, which='minor', color='lightgrey', linestyle='--')# style of minor grid lines
        plt.xlabel('Integration Time (s)') # label of x axis
        plt.ylabel('Modified ADEV')   # label of y axis
        
        for i in channels:
            plt.loglog(t2, stability_unit[channels.index(i)])
        plt.legend(channel_names)    
        if saveFigs: plt.savefig('TCH_plot.png')
        
        
# %% Frequency noise power spectral density from FXE Counter (WIP!!)

def PSD_Noise_from_Counter(df_Freqs,channels,channel_names,
                           wavelength = 1542.14e-9, 
                           freq_rate = 1/0.1, Requirements = False):
       
    print('Frequency noise PSD from FXE counter')   
    
    fig, axes = plt.subplots(num=3, nrows=3, 
                             ncols=1, gridspec_kw={'hspace': 0.10},
                             sharex=True)
    
    
    for channel in channels:
        
        
        f0 =  speed_of_light/wavelength    
        normFracFreq = np.array(df_Freqs[channel])/f0       
                      

    
        fffluctu    = mplm.csd(normFracFreq, normFracFreq, 
                                Fs=freq_rate,detrend='mean',
                                scale_by_freq='True',NFFT=2**18) # result in 1/Hz
        
        sqrtfflu    = np.sqrt(fffluctu[0].real*f0**2) # conversion to Hz²/Hz then Hz/√Hz 
        
        ffreq       = fffluctu[1] # Fourier frequencies
        
        
        Phi, Time = calculate_PhaseData(normFracFreq, freq_rate)       
        
        ##calulate Phasenoise PSD of Counter Data
        (fpsd, Spsd) = scipy.signal.periodogram(np.pi*2*Phi, fs=freq_rate, 
                                                window='boxcar', nfft=None, 
                                                detrend='constant', 
                                                return_onesided=True, 
                                                scaling='density', axis= -1)
        #discard first value number
        fpsd = np.flip(fpsd)
        Spsd = np.flip(Spsd)
        
        Spsdlog=10*np.log10(Spsd/1)
        
        
        
        axes[0].loglog(fpsd, 2*Spsd)
        axes[0].set_ylabel('S$_{\phi}$ [rad²/Hz]')
        axes[0].set_ylim([1e-15,10])
            
        axes[1].semilogx(fpsd,Spsdlog)
        axes[1].set_ylabel('ℒ(f) [dBc/Hz]')
        axes[1].set_ylim([-160,0])
        
        axes[2].loglog(ffreq,sqrtfflu)
        axes[2].set_ylabel('S$_{\Delta f}$ [Hz/√Hz]')
        
    
        for i in range(0,3):
            axes[i].legend(channel_names)
            axes[i].grid(visible=True, which='both')
            
            
    axes[0].set_title('Title')       
    axes[2].set_xlabel('Frequency [Hz]')
    if saveFigs: plt.savefig('PSDs_plot.png')
    
    

    
# %% Phase data from FXE Counter
def calculate_PhaseData(normFracFreq, freq_rate=10):
    
    """
    Calculate the phase difference between two signals from their frequency deviation.
    
    Parameters
    ----------
    normFracFreq : array-like
        Normalized frequency deviation between two laser signals.
    freq_rate : float, optional
        Sampling rate of the frequency data, in Hz (default is 10).
    
    Returns
    -------
    Phi : array
        Total phase difference over time, in cycles.
    Time : array
        Time values corresponding to each phase measurement, in hours.
    """
    
    # Calculate the time interval between samples
    t0 = 1 / freq_rate
    
    lc = len(normFracFreq)
    
    # Create an array of time values corresponding to each sample
    Time = np.linspace(0, t0*lc, lc) / 3600  # Convert to hours
    
    # Calculate the instantaneous phase difference at each sample
    PhaseDiff = normFracFreq * t0
    
    # Initialize the total phase difference
    Phi = np.zeros_like(PhaseDiff)
    
    # Accumulate the phase differences over time
    for i in range(1, lc):
        Phi[i] = Phi[i-1] + PhaseDiff[i]
        
    # Create a DataFrame with the time and phase data
    data = {'Time': Time, 'Phase': Phi}
    df = pd.DataFrame(data)
    
    return df['Phase'].values, df['Time'].values
    

def plot_PhaseData(df_Freqs,channels,wavelength = 1542.14e-9,freq_rate = 1/0.1):
    
    print('Calculating Phase from counter data')
    f0 =  (speed_of_light/wavelength)   
    
    p = 0
    for channel in channels:
        
        normFracFreq = np.array(df_Freqs[channel])/f0       
        
        Phi, Time = calculate_PhaseData(normFracFreq, freq_rate)
           
        #plot phase
        plt.figure(5)
        plt.plot(Time, Phi, '.-', linewidth=1, markersize=0.1, alpha=0.75,label=f'Phase for {channel_names[p]}')
        p +=1
        
    
        magic_number = 1e-19 #1e-19 ????????
        
        
    plt.plot(Time, f0*freq_rate*magic_number*Time, '.-', color='r', linewidth=0.75, markersize=0.0, alpha=0.9, label = f"{magic_number}")
    plt.plot(Time, -f0*freq_rate*magic_number*Time, '.-', color='r', linewidth=0.75, markersize=0.0, alpha=0.9)
    plt.xlim(left=Time[0])
    
    plt.xlabel('Time [h]')
    plt.ylabel('Phase [cycles]')
    plt.grid()
    plt.legend()
    plt.tight_layout()
    if saveFigs: plt.savefig('Phase_plot.png')



#%% Set the parameters for running the script:
    
if  __name__ == "__main__":
    
    # Choose folder and file location
    
    folder = r'\\FXE mdev\\'
    fileName = '22_2_Frequ.txt'
    
    saveFigs = False
    
    # Define the interval in seconds. Consider that Freq_rate = 1/interval
    interval_sec = 0.1
    
    # Select FXE channels to be analyzed    
    channels = [1,3,9]
    
    # Select the name for every channel    
    channel_names = ['Prot','AU','Pan']
     
    #### m = Modified || h = Hadamard || a = Allan deviation || oa = Overlapping
    AllanType = 'm'
    
### ----------------------------------------------------------------------- ###
    print('Running the script...')
    
    # Load the data
    df_Freqs = load_FXEdata(folder,fileName, channels)
    
    #### Comment and uncomment the functions you want to implement 
    
    calcAllanDev(df_Freqs, channels, channel_names, Type = AllanType,
                  freq_rate = 1/interval_sec, TCH = False)
    
    PSD_Noise_from_Counter(df_Freqs,channels, channel_names)
    
    plot_PhaseData(df_Freqs,channels, freq_rate = 1/interval_sec)
    
    plot_Frequency(df_Freqs, channels,channel_names)
