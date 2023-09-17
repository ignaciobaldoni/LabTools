# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 17:37:49 2021

@author: ibaldoni
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 17:40:30 2021

@author: ibaldoni
"""

from labTools_utilities import saveDictToHdf5
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import os.path
import scipy
from matplotlib.image import NonUniformImage

# We select the plots and results we want to see
plots                   = True
plot_hist               = True
swipe_to_mean           = True
hist2d_v2_misaligned    = True

cross_correlation = True

freq_trace              = True
save_figs               = False 
plot_drift              = True
New_Analysis            = True

normalizing             = False
discard_resonances      = False
drift_all_to_zero       = True
hist2d_v2               = False


intervals = 30 # Number of intervals for the histogram
size_hist = 1 # Number of bins for the 2d histogram
fileType_img = '.png' 
size_fig    = (12,8)
fig_resolution = 100    # a.k.a., dpi

num_points = 50000


folder                  = ''
measurementPurposeShort = 'D63_3_C12_F4_metalic_setup_v2/'
subfolder               = ''
file                    = 'Test_of_driftings__'


######################### LOAD FILE ##########################################

year = dt.datetime.today().year
month = dt.datetime.today().month
day =  dt.datetime.today().day

month = '0'+str(month) if len(str(month)) == 1 else month
day = '0'+str(day) if len(str(day)) == 1 else day

save_path = '//menloserver/MFS/03-Operations/02-DCP/03-Entwicklungsprojekte/'
project = '9552-KECOMO/'
main_folder = '52-Messergebnisse/'
fileType = '.h5'

### Today
date = str(year)+str(month)+str(day)

in_raw_data = '1-Raw Data/' 
in_data_analysis = '2-Data Analysis/' 
in_results  = '3-Results/'

subfolder_time = 'Time trace'
subfolder_freq = 'Frequency trace'

directory3 = save_path + project + main_folder+ folder + \
    date + measurementPurposeShort + in_results + subfolder 
    
directory2 = save_path + project + main_folder+ folder + \
    date + measurementPurposeShort + in_results 
    
directory1 = save_path + project+ main_folder+ folder + date + measurementPurposeShort + \
                                        in_results +  subfolder + subfolder_time 

directory4 = save_path + project+ main_folder+ folder + date + measurementPurposeShort + \
                                        in_results +  subfolder + subfolder_freq

if not os.path.exists(directory3):
    os.makedirs(directory3)
if not os.path.exists(directory2):
    os.makedirs(directory2)
if not os.path.exists(directory1):
    os.makedirs(directory1)
if not os.path.exists(directory4):
    os.makedirs(directory4)
    
    
import os
directory_data = save_path + project + main_folder+ folder + \
    date + measurementPurposeShort + in_raw_data
path, dirs, files = next(os.walk(directory_data))
file_count = len(files)

number_of_traces = file_count
###############################################################################

# List to enumerate the drifts, respect to zero in the different traces
# Zero is defined for all the traces as the first resonance of the FLC 
drift           = []
drift_amplitude = []
All_traces      = []
drifts_to_zero  = []
hist_time       = []
trace_number    = []

if New_Analysis == True:
    for i in range(0,number_of_traces):
        iteration   = str(int(i))
    
        fileName = os.path.join(save_path, project+ \
                                            main_folder+\
                                            folder+ \
                                            date +  \
                                            measurementPurposeShort + \
                                            in_raw_data +  \
                                            subfolder + \
                                            file +  \
                                            iteration + \
                                            fileType)    
        
        ##############################################################################
            
        dict_Result = saveDictToHdf5.load_dict_from_hdf5(fileName)
        
        timeTrace = dict_Result['measurementData'] \
                                    ['fiberResonatorTransmission_traceData'] \
                                    ['time_axes']
        
        # get fiber loop cavity transmission trace
        voltageTrace = dict_Result['measurementData'] \
                                    ['fiberResonatorTransmission_traceData'] \
                                    ['voltage_axes']
                                    
    
                                    
        # get ring resonator transmission trace
        # Actually, is the generated light trace but for compatibilty purposes 
        # between the oscilloscope measurements and the analysis, we mantain the 
        # same name as the oscilloscope script
        
        ringResonatorTransmissionTrace \
            = dict_Result['measurementData'] \
                        ['ringResonatorTransmission_traceData'] \
                        ['voltage_axes']
                        
        # get function generator transmission trace
        functionGeneratorTrace \
        = dict_Result['measurementData'] \
                    ['funtionGeneratorRamp_traceData'] \
                    ['voltage_axes']
        
        min_trace = np.where(functionGeneratorTrace==np.min(functionGeneratorTrace))[0][0]
        max_trace = np.where(functionGeneratorTrace==np.max(functionGeneratorTrace))[0][0]
        
        # We redefine all the traces according to the voltage (should be stable)
        
        timeTrace                       = timeTrace[min_trace:max_trace]
        ringResonatorTransmissionTrace  = ringResonatorTransmissionTrace[min_trace:max_trace]
        voltageTrace                    = voltageTrace[min_trace:max_trace]
        functionGeneratorTrace          = functionGeneratorTrace[min_trace:max_trace]
    
        # We find the highest point from the generated light transmission.
        # Value and position although only the position is what we care about
        # It will be the point to follow when a drift in frequency exists. 
            
        max_generatedLightTrace = np.max(ringResonatorTransmissionTrace)
        min_generatedLightTrace = np.min(ringResonatorTransmissionTrace)
        peak_generatedLight = np.where(ringResonatorTransmissionTrace==max_generatedLightTrace)
        
        # In case the signal is lost and the traces are spurios we consider only 
        # the ones that are useful
        if np.abs(max_generatedLightTrace - min_generatedLightTrace) \
                    > 0.7*max_generatedLightTrace:
            
            # In case that, for lack of resolution, we have more than one...
            
            peak_generatedLight = peak_generatedLight[0][0]                    
            
        #    We find the peaks from the FLC and select two in order to make a df/dt 
        #    relation through interpolation
                  
            from scipy import interpolate as interp
            from scipy.signal import find_peaks
            fiber_resonator = -voltageTrace    # We invert the signal to get the peaks
        
            magic_number1 = 1.05*np.max(fiber_resonator)
    #        magic_number2 = 1.1*np.max(fiber_resonator)
            magic_number3 = num_points*0.015 #Distance between peaks 
    
            peaks, _ = find_peaks(fiber_resonator, 
                                  height = magic_number1, 
                                  distance = magic_number3,
                                  prominence = magic_number1)    
            
            ## I get rid of the spurios peaks. It can happen that the first peak 
            ## that it measures is too close to the lasers limited range
    #        peaks = peaks[1:]
            if discard_resonances == True:
                print('Discard')
                    
            # This might need an improvement.
            FSR = 180.3
            dt = timeTrace[peaks]
            df = []
            for h in range(0,len(peaks)):
                df.append(FSR*(h-len(peaks)+1))
                
            # We get the frequency according to the position of the calibration FLC
            freq_x = interp.interp1d(dt, df,fill_value="extrapolate")
            freq = freq_x(timeTrace)
            
#            plt.plot(timeTrace[peaks],freq_x(timeTrace[peaks]),'-o',
#                     timeTrace[-1],freq_x(timeTrace[-1]),'-o')
            
            # Time trace now becomes a frequency. 
            if freq_trace == True:
                timeTrace = freq
                label_x = 'Frequency (MHz)'
                subfolder2 = 'Frequency trace/'
            else:
                label_x = 'time (s)'
                subfolder2 = 'Time trace/'
            
            # Select the value of reference for each trace. Can be done in Freq as well
            oscilloscope_zero_point = freq[-1] if freq_trace==True else timeTrace[-1]
    #        oscilloscope_zero_point = freq[0] if freq_trace==True else timeTrace[0]
    #        oscilloscope_zero_point = freq[peaks[-1]] if freq_trace==True else timeTrace[peaks[-1]]

            # The drift will be the difference between the first value of the scope
            # trace and the point where the generated light is maximum
            Drift = timeTrace[peak_generatedLight] - oscilloscope_zero_point
            Drift_Amplitude = max_generatedLightTrace
            
            if plots == True:
                
                if normalizing == False:
                    fig, ax1 = plt.subplots(num=1, figsize=size_fig, dpi=fig_resolution)
                    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
                    ax1.plot(timeTrace,voltageTrace,'r--',linewidth = 0.1)
                    ax1.plot(timeTrace[peaks],voltageTrace[peaks],'go')
                    ax2.plot(timeTrace,ringResonatorTransmissionTrace)
                    
                    ax2.plot(timeTrace[peak_generatedLight],ringResonatorTransmissionTrace[peak_generatedLight],'o')
                    
                    ax1.tick_params(labelsize=17)
                    ax1.set_xlabel(label_x,fontsize=20)
                    ax1.set_ylabel('Fiber Loop Cavity (V)',fontsize=20)
                    ax1.set_ylim([0.4,0.7])
                    ax2.set_ylabel('Generated Light (V)',fontsize=20)
                    ax2.tick_params(labelsize=17)
                    ax2.set_ylim([0.,2.0])
                    
                elif normalizing == True:
                    plt.figure(num=1, figsize=size_fig, dpi=fig_resolution) 
                    plt.plot(timeTrace,voltageTrace/np.max(voltageTrace))
                    plt.plot(timeTrace,ringResonatorTransmissionTrace/np.max(ringResonatorTransmissionTrace))
                    plt.plot(timeTrace[peaks],voltageTrace[peaks]/np.max(voltageTrace),'o')
                    plt.plot(timeTrace[peak_generatedLight],ringResonatorTransmissionTrace[peak_generatedLight]/np.max(ringResonatorTransmissionTrace),'o')
                    plt.tick_params(labelsize=17)
                    plt.xlabel(label_x,fontsize=20)
                    plt.ylabel('Voltage (a.u)',fontsize=20)
                    
                if save_figs == True:
                                
                    saveResults = os.path.join(save_path, project+ \
                                            main_folder+ \
                                            folder+\
                                            date +  \
                                            measurementPurposeShort + \
                                            in_results +  \
                                            subfolder + \
                                            subfolder2 + \
                                            file +  \
                                            iteration + \
                                            fileType_img) 
                    plt.savefig(saveResults)
                    plt.close()
                    subfolder = ''
                    
            # We collect the drift for a later histogram analysis
            drift.append(np.round(Drift,10))
            drift_amplitude.append(np.round(Drift_Amplitude,10))
            
            trace_number.append(i)
            
            All_traces.append(ringResonatorTransmissionTrace)
            
            if drift_all_to_zero == False:
                drifts_to_zero.append(timeTrace)
            else:
                drifts_to_zero.append(timeTrace-timeTrace[peak_generatedLight])
            
#            hist_time.append(timeTrace)

# We move all the plot to the average of the results
if swipe_to_mean == True:
    
    hist, bin_edges = np.histogram(drift, bins=intervals)
    estimation = np.linspace(np.min(drift),np.max(drift),intervals-1)
    
    result = estimation[np.argmax(hist)]
    drift = [x-result for x in drift]


#%%   Results plots
if hist2d_v2 == True:
    
    nbiny = 250#np.linspace(np.min(All_traces[0]), np.max(All_traces[0]), 250)
    nbinx = 250#np.linspace(np.min(drifts_to_zero[0]), np.max(drifts_to_zero[0]), 250)
    xs = drifts_to_zero
    ys = All_traces
           
    heatmap = 0
    for x, y in zip(xs, ys):
        hist, _, _ = np.histogram2d(
            y, x, bins = [nbinx,nbiny])
        heatmap += hist
        
    fig, ax = plt.subplots(num=2, figsize=size_fig, dpi=fig_resolution) #plt.subplots()
    fig_hist2d = ax.imshow(heatmap, extent=None,
    #                       norm=mpl.colors.LogNorm(),
                           interpolation='nearest')

    plt.colorbar(fig_hist2d)
    plt.show()


    if save_figs == True:
                
        saveResults_hist2D = os.path.join(save_path, project+ \
                                main_folder+ \
                                folder +\
                                date +  \
                                measurementPurposeShort + \
                                in_results +  \
                                subfolder + \
                                str('Hist_2D')+ \
                                str(subfolder2[:-1])+\
                                fileType_img) 
        plt.savefig(saveResults_hist2D)


if plot_hist == True:    
    plt.figure(num=4, figsize=size_fig, dpi=fig_resolution) 
    plt.hist(drift,bins = intervals, alpha=0.5)
        
    plt.xlabel(label_x ,fontsize=20)
    plt.ylabel('Counts',fontsize=20)
    plt.tick_params(labelsize=17)
    if save_figs == True:
        saveResults_hist = os.path.join(save_path, project+ \
                                main_folder+ \
                                folder+ \
                                date +  \
                                measurementPurposeShort + \
                                in_results +  \
                                subfolder + \
                                str('Histogram_timeTrace')+\
#                                str(subfolder2[:-1])+ \                                
                                fileType_img) 
        plt.savefig(saveResults_hist)


if plot_drift == True:
    
    fig, ax1 = plt.subplots(num=6, figsize=size_fig, dpi=fig_resolution)
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
#    plt.figure(num=6, figsize=size_fig, dpi=fig_resolution) 
    ax1.plot(trace_number,drift)
    ax1.set_xlabel('Trace Number')
    ax1.set_ylabel('Drift in detuning')
    
#    plt.figure(num=6, figsize=size_fig, dpi=fig_resolution) 
    ax2.plot(trace_number,drift_amplitude,'g-',alpha = 0.3)
    ax2.set_xlabel('Trace Number')
    ax2.set_ylabel('Drift in amplitude')
    
    if save_figs == True:
        saveResults_hist_fit = os.path.join(save_path, project+ \
                                main_folder+ \
                                folder+ \
                                date +  \
                                measurementPurposeShort + \
                                in_results +  \
                                subfolder + \
                                str('Drift_traces')+ \
                                str(subfolder2[:-1])+\
                                fileType_img) 
        plt.savefig(saveResults_hist_fit)
        


if cross_correlation == True:
    import matplotlib.pyplot as plt
    import numpy as np
    
    Max_lag = number_of_traces-1
    
    x = drift
    y = drift_amplitude
    fig, [ax1, ax2, ax3] = plt.subplots(3, 1, sharex=True,num=7, figsize=size_fig, dpi=fig_resolution)
    ax1.xcorr(x, y, usevlines=True, maxlags=Max_lag, normed=True, lw=2)
    ax1.grid(True)
    ax1.title.set_text('Cross correlation (Detuning drift vs. Amplitude drift)')
    
    ax2.acorr(x, usevlines=True, normed=True, maxlags=Max_lag, lw=2)
    ax2.grid(True)
    ax2.title.set_text('Autocorrelation (Detuning drift)')
    
    ax3.acorr(y, usevlines=True, normed=True, maxlags=Max_lag, lw=2)
    ax3.grid(True)
    ax3.title.set_text('Autocorrelation (Amplitude drift)')
    ax3.set_xlabel('Lag')
     
    plt.show()
    
    if save_figs == True:
        saveResults_correlation = os.path.join(save_path, project+ \
                                main_folder+ \
                                folder+ \
                                date +  \
                                measurementPurposeShort + \
                                in_results +  \
                                subfolder + \
                                str('Correlation')+ \
                                fileType_img) 
        plt.savefig(saveResults_correlation)