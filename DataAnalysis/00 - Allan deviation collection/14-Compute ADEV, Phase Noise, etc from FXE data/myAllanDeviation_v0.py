# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 14:44:23 2023

@author: ibaldoni

This Python script is designed to process frequency data from a FXE counter
and calculate different parameters of interest such as 
Allan deviation, frequency noise power spectral density, phase and phase noise. 

For using, simply select the FXE file and the parameters to be analyzed at the 
end of this script
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import allantools as at
from scipy.constants import speed_of_light
import matplotlib.mlab as mplm
import scipy.signal


#%% Personal functions for plotting and units
import sys
sys.path.append(r'\\menloserver\MFS\99-Data_Warehouse\02-User_Folders-Public\i.baldoni\python Util functions')
from Plot_aux_functions import Plot_parameters
Plot_parameters()

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
        plt.loglog(t2, ad)
        plt.title('overall stability')
        plt.grid(visible=True, which='major', color='lightgrey', linestyle='-')  # style of major grid lines
        plt.grid(visible=True, which='minor', color='lightgrey', linestyle='--')# style of minor grid lines
        plt.xlabel('Integration Time (s)') # label of x axis
        plt.ylabel(allan_type+'ADEV')   # label of y axis
        plt.legend(channel_names)
    
    
    
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
        
        
# %% Frequency noise power spectral density from FXE Counter (WIP!!)

def PSD_Noise_from_Counter(df_Freqs,channels,channel_names,
                           wavelength = 1542.14e-9, 
                           freq_rate = 1/0.1, Requirements = False):
    
    
    fig, axes = plt.subplots(num=3, nrows=3, 
                             ncols=1, gridspec_kw={'hspace': 0.10},
                             sharex=True)
    
    
    for channel in channels:
        
        
        print(channel)    
        f0 =  speed_of_light/wavelength    
        normFracFreq = np.array(df_Freqs[channel])/f0       
                      
        print('Frequency noise PSD from FXE counter')
    
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
            
        axes[1].semilogx(fpsd,Spsdlog)
        
        axes[2].loglog(ffreq,sqrtfflu)
        
    
        for i in range(0,3):
            axes[i].legend(channel_names)
            
            
    axes[0].set_title('Title')       
    axes[0].set_ylabel('S$_{\phi}$ [rad²/Hz]')
    axes[0].grid(visible=True, which='both')
    axes[0].set_ylim([1e-15,10])
    axes[1].set_xlabel('Frequency [Hz]')
    axes[1].set_ylabel('ℒ(f) [dBc/Hz]')
    axes[1].set_ylim([-160,0])
    axes[1].grid(visible=True, which='both')
    axes[2].set_xlabel('Frequency [Hz]')
    axes[2].set_ylabel('S$_{\Delta f}$ [Hz/√Hz]')
    axes[2].grid(visible=True, which='both')
        
        
        
    
    
    

    


    
# %% Phase data from FXE Counter
def calculate_PhaseData(normFracFreq, freq_rate=10):
    
    #calculate Phase data    
    t0 = 1/freq_rate
    lc = len(normFracFreq)
    Time = np.linspace(0,t0*lc, lc)

    
    result_phi = []
    erstwert = np.multiply(normFracFreq[0], t0)
    result_phi.append(erstwert)
    
    for i in range(1, lc):
        k = i-1
        phig = np.multiply(normFracFreq[i], t0)

        addendum = result_phi[k]
        phires = np.add(addendum, phig)
        result_phi.append(phires)
        
    #create Time and Phase array
    lrp = np.arange(len(result_phi))
    d = pd.DataFrame(result_phi)
    d.insert(loc=0, column='Time', value=np.divide(lrp, freq_rate))
    d2 = d.to_numpy()

    
    Time = np.divide(Time, 3600) # Turn seconds into hours
    Phi = d2.T[1]
    
    return Phi, Time

def plot_PhaseData(df_Freqs,channels,wavelength = 1542.14e-9,freq_rate = 1/0.1):
    
    '''
    Edited from Ben Rauf's script
    '''
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



#%% Set the parameters for running the script:
    
if  __name__ == "__main__":
    
    # Choose folder and file location
    
    folder = r'C:\\Users\\ibaldoni\\Desktop\\TimeLab files\\FXE mdev\\'
    fileName = '211007_2_Frequ.txt'
    
    # Define the interval in seconds. Consider that Freq_rate = 1/interval
    interval_sec = 0.1
    
    # Select FXE channels to be analyzed    
    channels = [1,3,9]
    
    # Select the name for every channel    
    channel_names = ['Prototype','AU','PuCC']
     
    #### m = Modified || h = Hadamard || a = Allan deviation || oa = Overlapping
    AllanType = 'm'
    
### ----------------------------------------------------------------------- ###
    print('Running the script...')
    
    # Load the data
    df_Freqs = load_FXEdata(folder,fileName, channels)
    
    # Comment and uncomment the functions you want to implement 
    
    # calcAllanDev(df_Freqs, channels, channel_names, Type = AllanType,
    #              freq_rate = 1/interval_sec, TCH=False)
    
    
    PSD_Noise_from_Counter(df_Freqs,channels, channel_names)
    
    # plot_PhaseData(df_Freqs,channels, freq_rate = 1/interval_sec)






# Deleted files

    # '''
    # Edited from Michele and Sarah's script
    # '''
    
    # print('Frequency noise PSD from FXE counter')
    
    # beat = np.genfromtxt(folder+fileName) # Frequency trace from FXE counter
    
    # f0 = (speed_of_light/wavelength)
    
    # for i in channels: 

    #     beat_a0 = beat[:,i]  
    
    #     beat_norm   = beat_a0/f0
    #     fffluctu    = mplm.csd(beat_norm, beat_norm, 
    #                             Fs=freq_rate,detrend='mean',
    #                             scale_by_freq='True',NFFT=2**18) # result in 1/Hz
        
    #     sqrtfflu    = np.sqrt(fffluctu[0].real*f0**2) # conversion to Hz²/Hz then Hz/√Hz 
        
    #     ffreq       = fffluctu[1] # Fourier frequencies
        
        
                
        
    #     #### Frequency fluctuation plot
    #     plt.figure(3)
    #     plt.loglog(ffreq,sqrtfflu)
    #     plt.xlabel('Fourier frequency [Hz]')
    #     plt.ylabel(r'Frequency fluctuation [Hz/√Hz] ')
        
        
        
    #     PN   = (fffluctu[0].real*f0**2)/(ffreq**2)
        
        
        
    #     dBc_Hz_PN = 10*np.log10(0.5*PN)
        
    #     #### Phase Noise plot
    #     plt.figure(4)
    #     plt.plot(ffreq,dBc_Hz_PN)
    #     plt.xscale('log')
    #     plt.xlabel('Fourier frequency [Hz]')
    #     plt.ylabel('Phase Noise [dBc/Hz]')
    
    
    # Req_legend = []
    # # Requirements
    # if Requirements:
    #     ax = plt.gca()
    #     freqreq1=[1e-4,1e-3,1e-2,1e-1,1]
    #     req1=[1e4,1e2,30,30,30]
    #     freqreq2=[1,10,100,1000,1e4,1e5,1e6]
    #     req2=[3e4,3e3,3e2,3e1,5,4,4]
        
    #     ax.loglog(freqreq1,req1, 'black', label="Requirement")
    #     ax.loglog(freqreq2,req2, 'red', label = 'Requirement in red')
    #     Req_legend = ["Requirement","Requirement in red"]
    
    # plt.legend(channel_names + Req_legend)
    # plt.grid(True, which='major', color='k',linestyle='-')  # style of major grid lines
    # plt.grid(True, which='minor', color='grey', linestyle='--')  # style of minor grid lines
    

