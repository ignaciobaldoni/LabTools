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


#%% Import necessary modules
print('Stablish concept for error bars')
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
from Plot_aux_functions import Plot_parameters, makeTable,add_grids
Plot_parameters()

#%% Load files from FXE Counter
def load_FXEdata(folder,file,channels):
    print('Loading FXE data')
       
    df_Freqs = pd.read_csv(folder+file,
                        delimiter = r"\s+",
                        header=None, 
                        skiprows=11, 
                        usecols=channels, 
                        float_precision='high')
    
    # df_Freqs = df_Freqs #df_Freqs * 10*np.random.random() * np.sin(len(df_Freqs))
    


    return df_Freqs



#%% Plot frequency (dedrift or raw)
def plot_Frequency(df_Freqs,channels,channel_names, wavelength = 1542.14e-9, 
                   freq_rate = 10, Dedrift = False):
    
    num_plots = len(channels)
    t0 = 1/freq_rate
    if num_plots>1:
        fig, axes = plt.subplots(num=7, nrows=num_plots, 
                                 ncols=1, gridspec_kw={'hspace': 0.10},
                                 sharex=True)
    
    p=0
    for i in channels:
        
        FXE_freqs = np.array(df_Freqs[i])
        
        lc = len(FXE_freqs)
        Time = np.linspace(0,t0*lc, lc)
        if num_plots>1:
            axes[p].plot(Time,FXE_freqs, label = f'{channel_names[p]}')
            # axes[p].grid(visible=True, which='both')
            # axes[p].legend()
            add_grids()
        else:
            fig = plt.figure(num=7)
            plt.plot(Time,FXE_freqs, label = f'{channel_names[p]}',color='#053061')
            # plt.grid(visible=True, which='both')
            plt.legend()
            plt.xlabel('Time [s]')
            add_grids()
        
        p+=1
    
    if num_plots>1: axes[p-1].set_xlabel('Time [s]')
    fig.supylabel('Frequency [Hz]')
    if Dedrift: 
        plt.suptitle('FXE frequency with dedrift')
    else:
        plt.suptitle('Raw FXE frequency')
    fig.subplots_adjust(top=0.93, left = 0.1)
    if saveFigs: plt.savefig('Frequency_plot.png')
        
        
        
        

# %% Allan deviation from FXE counter

def calcAllanDev(df_Freqs, channels, channel_names, freq_rate = 1/0.1, 
             TCH = False, Dedrift = True, 
             wavelength = 1542.14e-9, Type = 'm', saveFigs = False):
    print('Calculating Allan Deviation')
    print('Data to be provided to the allantools is the Fractional Frequency (adimensional)')
    
    # df_Freqs is the readout frequency from the FXE
    # We normalized them to the fractional frequency dividing by f0 
    f0 = (speed_of_light/wavelength)

   
    for i in channels:        
        color = '#00'+str(i)+'41b'
        if Dedrift == False: 

            FXE_Freqs = np.array(df_Freqs)/f0#np.array(df_Freqs[i])/f0
            
            phase_data=at.frequency2phase(FXE_Freqs, freq_rate)
        
        if Dedrift:  
            FXE_Freqs = np.array(df_Freqs[i])/f0
            
            phase_data=at.frequency2phase(FXE_Freqs, freq_rate)
            
        
        if Type == 'm' : 
            (t2, ad, ade, adn) = at.mdev(phase_data, rate=freq_rate, data_type="phase", taus="decade")
            allan_type = 'Modified '
        if Type == 'a' : 
            (t2, ad, ade, adn) = at.adev(FXE_Freqs, rate=freq_rate, data_type="freq", taus="decade")
            allan_type = ''
        if Type == 'oa' : 
            (t2, ad, ade, adn) = at.oadev(FXE_Freqs, rate=freq_rate, data_type="freq", taus="decade")
            allan_type = 'Overlapping '
        if Type == 'h' : 
            (t2, ad, ade, adn) = at.hdev(FXE_Freqs, rate=freq_rate, data_type="freq", taus="decade")
            allan_type = 'Hadamard '
        
               
        fig = plt.figure(1)
        
        plt.errorbar(t2,ad, yerr=ade, marker='o', color = color, linewidth=1.5)
        plt.loglog()
        plt.title('overall stability')
        plt.grid(visible=True, which='major', color='lightgrey', linestyle='-')  # style of major grid lines
        plt.grid(visible=True, which='minor', color='lightgrey', linestyle='--')# style of minor grid lines
        plt.xlabel('Integration Time (s)') # label of x axis
        plt.ylabel(allan_type+'ADEV')   # label of y axis
        plt.legend(channel_names)
        plt.ylim([1e-16,1e-12])
        
        # Preparation of the data to getting into the table

        t_tau = [0.1, 1.0, 10.0, 100.0]  # tau values to be shown in table (a .1 has been added because for some reason the ADEV functions lower the taus a bit...)
        
        makeTable(t2, ad, fig, print_freqs = t_tau,plot_type='allan')
        
        
        if saveFigs: plt.savefig('Allan_deviation_plot.png')
    
    
#%% TCH 
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
                           freq_rate = 1/0.1, Requirements = False, Dedrift = False):
    
    '''Edited function from Ben Rauf's script (2023) 
        and Michele/Sarah script (2015)'''
    
    print('Frequency noise PSD from FXE counter, still work in progress')   
    
    if Dedrift == False:
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
                
                
        axes[0].set_title('Work in progress. Check the algorithm')       
        axes[2].set_xlabel('Frequency [Hz]')
        if saveFigs: plt.savefig('PSDs_plot.png')
    else:
        print('No plot for phase noise - frequency noise because of Dedrift is on')
    
    

    
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


def plot_PhaseData(df_Freqs,channels,wavelength = 1542.14e-9,freq_rate = 1/0.1, Dedrift = False):
    
    '''
    Edited from Ben Rauf's script
    '''
    if Dedrift == False:
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
    else:
        print('No plot for phase data because of Dedrift is on')

#%% Apply dedrift
def apply_dedrift(dfFreqs, freq_rate = 10,wavelength_nm = 1542):
        
    for channel in channels:
        lc = len(dfFreqs[channel])
        t0 = 1/freq_rate
        
        x = np.linspace(0,t0*lc, lc)
        y1 = np.array(dfFreqs[channel])
        # f_scale=float(wavelength_nm/3)/10**17 #multiplier
        
        coefs1=np.polyfit(x,y1,1)
        linear_drift_1=coefs1[0]
        print(linear_drift_1*1E3,'mHz/s')
        freq_data_Hz=(y1-(x*coefs1[0]+coefs1[1]))
    
        dfFreqs.loc[:,channel] = freq_data_Hz#*f_scale
    
    return dfFreqs 

#%% Set the parameters for running the script:
    
if  __name__ == "__main__":
    
    # Choose folder and file location
    folder = r'C:\Users\ibaldoni\Desktop\Ignacio\Allan deviation'
    fileName = r'\230418_1_Frequ.txt'
    saveFigs   = False      
    wavelength = 1542.14e-9    
    
    

    
    # Define the acquisition frequency in Hz (frequency rate)
    freq_rate = 10 
    
    # Select FXE channels to be analyzed. 
    channels = [4]

    # Select the name for every channel    
    channel_names = ['ORS Mini Menlo Inc']
     
    #### m = Modified || h = Hadamard || a = Allan deviation || oa = Overlapping
    AllanType = 'm'
    
    Calculate_allan_deviation   = True
    Plot_Frequency              = True
    Plot_PSD_Noise_from_Counter = False
    Plot_PhaseData              = False
    
    Dedrift                     = True
    
    
#%% Runnning the script with the selected parameters 
### ----------------------------------------------------------------------- ###
### ----------------------------------------------------------------------- ###
### ----------------------------------------------------------------------- ###

    print('Running the script...')
    folder = folder[:2] + folder[2:].replace('\\', '\\\\')
    fileName = str('\\') + fileName 
    
    # All channels need to be moved two places to the right:
    channels = [i+2 for i in channels]
    # Load the data
    Raw_df_Freqs = load_FXEdata(folder,fileName, channels)
    

    
    # Dummy_freqs = True
    # if Dummy_freqs == True:
        
    #     Raw_df_Freqs2 = Raw_df_Freqs
    #     time = np.linspace(0,370,len(Raw_df_Freqs2))
    #     Raw_df_Freqs = pd.DataFrame(10*np.random.random()*np.sin(0.05*np.pi*time))
    #     plt.figure(7)
    #     plt.plot(time, Raw_df_Freqs)

    
    if Dedrift:
        df_Freqs = apply_dedrift(Raw_df_Freqs, freq_rate = 10, wavelength_nm = 1542)
    else:
        df_Freqs = Raw_df_Freqs
    
    #### Comment and uncomment the functions you want to implement 
    if Calculate_allan_deviation:
        calcAllanDev(df_Freqs, channels, channel_names, 
                     Type = AllanType, freq_rate = freq_rate, 
                     TCH = False, Dedrift = Dedrift)
        
    if Plot_Frequency:
        plot_Frequency(df_Freqs, channels,channel_names,
                       Dedrift=Dedrift)
        
    if Plot_PSD_Noise_from_Counter:
        PSD_Noise_from_Counter(df_Freqs,channels, channel_names, 
                               Dedrift = Dedrift)
    if Plot_PhaseData:   
        plot_PhaseData(df_Freqs,channels, freq_rate = freq_rate, 
                       Dedrift = Dedrift)
    
