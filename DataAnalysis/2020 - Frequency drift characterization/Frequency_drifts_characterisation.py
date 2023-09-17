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
fit_hist                = False
hist2d_v2               = True
hist2d_v2_misaligned    = True
drift_all_to_zero       = False
freq_trace              = True
save_figs               = False 

number_of_traces = 309
intervals = 30
size_hist = 1 # Number of bins for the 2d histogram
fileType_img = '.png' 
size_fig    = (12,8)
fig_resolution = 100    # a.k.a., dpi

######################### LOAD FILE ##########################################

year = dt.datetime.today().year
month = dt.datetime.today().month
day =  dt.datetime.today().day -3#'20210203'

month = '0'+str(month) if len(str(month)) == 1 else month
day = '0'+str(day) if len(str(day)) == 1 else day

save_path = '//menloserver/MFS/03-Operations/02-DCP/03-Entwicklungsprojekte/'
project = '9552-KECOMO/'
folder = '52-Messergebnisse/'
fileType = '.h5'

### Today
date = str(year)+str(month)+str(day)

in_raw_data = '1-Raw Data/' 
in_data_analysis = '2-Data Analysis/' 
in_results  = '3-Results/'

measurementPurposeShort = '_12_GHz_chip/'#'_Ortwin_20_GHz_chip_v2/'
subfolder               = ''
file                    = 'Test_of_driftings__'

directory3 = save_path + project + folder + \
    date + measurementPurposeShort + in_results + subfolder 

if not os.path.exists(directory3):
    os.makedirs(directory3)
###############################################################################

# List to enumerate the drifts, respect to zero in the different traces
# Zero is defined for all the traces as the first resonance of the FLC 
drift           = []
All_traces      = []
drifts_to_zero  = []
hist_time       = []

for i in range(0,number_of_traces+1):
    iteration   = str(int(i))

    fileName = os.path.join(save_path, project+ \
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
        num_resonances = 7 
        magic_number2 = len(fiber_resonator)/num_resonances
        
        peaks, _ = find_peaks(fiber_resonator, 
                              height = magic_number1, 
                              distance = magic_number2)    
        
        # I get rid of the spurios peaks. It can happen that the first peak that it 
        # measures is too close to the lasers limited range
    #    peaks = peaks[1:]
        if len(peaks) > 5:
            peaks = peaks[:-1]
        
        # This might need an improvement.
        FSR = 180.3
        dt = timeTrace[peaks]
        df = []
        for h in range(0,len(peaks)):
            df.append(FSR*h)
            
        # We get the frequency according to the position of the calibration FLC
        freq_x = interp.interp1d(dt, df,fill_value="extrapolate")
        freq = freq_x(timeTrace)
        
        # Time trace now becomes a frequency. 
        if freq_trace == True:
            timeTrace = freq
            label_x = 'Frequency (MHz)'
        else:
            label_x = 'time (s)'
        
        # Select the value of reference for each trace. Can be done in Freq as well
        oscilloscope_zero_point = freq[0] if freq_trace==True else timeTrace[0]
        
        # The drift will be the difference between the first value of the scope
        # trace and the point where the generated light is maximum
        Drift = timeTrace[peak_generatedLight] - oscilloscope_zero_point
        
        if plots == True:
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
                                        folder+ \
                                        date +  \
                                        measurementPurposeShort + \
                                        in_results +  \
                                        subfolder + \
                                        file +  \
                                        iteration + \
                                        fileType_img) 
                # plt.savefig(saveResults)
                plt.close()
                
        # We collect the drift for a later histogram measurement
        drift.append(np.round(Drift,10))
        
        All_traces.append(ringResonatorTransmissionTrace)
        
        if drift_all_to_zero == True:
            drifts_to_zero.append(timeTrace)
        else:
            drifts_to_zero.append(timeTrace-timeTrace[peak_generatedLight])
        
        hist_time.append(timeTrace)


#%%   Results plots

# We move all the plot to the average of the results
#mu, sigma = scipy.stats.norm.fit(drift)


if swipe_to_mean == True:
    
    hist, bin_edges = np.histogram(drift, bins=intervals)
    estimation = np.linspace(np.min(drift),np.max(drift),intervals-1)
    
    result = estimation[np.argmax(hist)]
    drift = [x-result for x in drift]


subfolder = ''
if hist2d_v2 == True:
    nbiny = 20
    nbinx = 20
    xs = drifts_to_zero
    ys = All_traces
    
#    min_trace = np.min(All_traces[0])
#    max_trace = np.max(All_traces[0])    
#    min_time  = np.min(drifts_to_zero[0])
#    max_time  = np.max(drifts_to_zero[0])
#
#    positions_x = (0, nbinx*0.25, nbinx*0.5,nbinx*0.75, nbinx)
#    labels_x = np.round(np.linspace(min_time, max_time, 5),4)
#    
#    positions_y = (0, nbiny*0.25, nbiny*0.5,nbiny*0.75, nbiny)
#    labels_y = np.round(np.linspace(min_trace, max_trace, 5),4)
           
    heatmap = 0
    
    for x, y in zip(xs, ys):
        hist, _, _ = np.histogram2d(
            y, x, bins = [nbinx,nbiny])
        heatmap += hist
        
#    extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]
    
#    heatmap = np.flipud(np.rot90(heatmap, k=4))

    fig, ax = plt.subplots(num=2, figsize=size_fig, dpi=fig_resolution) #plt.subplots()
    fig_hist2d = ax.imshow(heatmap, extent=None,
    #                       norm=mpl.colors.LogNorm(),
                           interpolation='nearest')
    plt.gca().invert_yaxis()
    
#    plt.xticks(positions_x, labels_x)
#    plt.yticks(positions_y, labels_y)
    plt.colorbar(fig_hist2d)
    plt.show()

    
#    for i in range(0,number_of_traces+1):
#        plt.figure(num=2, figsize=size_fig, dpi=fig_resolution) 
#        plt.hexbin(drifts_to_zero,All_traces,\
#                   bins=(size_hist,size_hist),\
##                   cmap=plt.cm.cubehelix,
#                   yscale = 'linear')
#        
#        plt.xlabel(label_x)
#        plt.ylabel('Generated light')
#    cbar = plt.colorbar()
#    cbar.ax.set_ylabel('Counts')
    if save_figs == True:
                
        saveResults_hist2D = os.path.join(save_path, project+ \
                                folder+ \
                                date +  \
                                measurementPurposeShort + \
                                in_results +  \
                                subfolder + \
                                file +  \
                                iteration + \
                                str('Hist_2D')+ \
                                fileType_img) 
        # plt.savefig(saveResults_hist2D)

import matplotlib as mpl
if hist2d_v2_misaligned == True:
    nbiny = 50#np.linspace(hist_time[0][0], hist_time[0][-1], 5)
    nbinx = 50#np.linspace(All_traces[0][0], All_traces[0][-1], 5)
    xs = hist_time
    ys = All_traces
    
    heatmap = 0
    
    for x, y in zip(xs, ys):
        hist, xedges, yedges = np.histogram2d(
            y, x, bins = [nbinx,nbiny])
        heatmap += hist
        
#    extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]
    
    heatmap = np.flipud(heatmap)
    fig, ax = plt.subplots(num=3, figsize=size_fig, dpi=fig_resolution) #plt.subplots()
    fig_hist2d = ax.imshow(heatmap, extent=None,
    #                       norm=mpl.colors.LogNorm(),
                           interpolation='nearest')
    plt.colorbar(fig_hist2d)
    plt.show()
#    for i in range(0,number_of_traces+1):
#        plt.figure(num=3, figsize=size_fig, dpi=fig_resolution) 
##        im = NonUniformImage(ax, interpolation='bilinear')
#        plt.hexbin(hist_time,All_traces,\
#                   bins=(size_hist,size_hist),\
##                   cmap=plt.cm.cubehelix,
#                   norm=mpl.colors.LogNorm(),
#                   yscale = 'linear')
#        
#        plt.xlabel(label_x)
#        plt.ylabel('Generated light')
#    cbar = plt.colorbar()
#    cbar.ax.set_ylabel('Counts')
    if save_figs == True:
                
        saveResults_hist2D = os.path.join(save_path, project+ \
                                folder+ \
                                date +  \
                                measurementPurposeShort + \
                                in_results +  \
                                subfolder + \
                                file +  \
                                iteration + \
                                str('Hist_2D_misaligned')+ \
                                fileType_img) 
        # plt.savefig(saveResults_hist2D)


# Number of intervals for the histogram
if plot_hist == True:    
    plt.figure(num=4, figsize=size_fig, dpi=fig_resolution) 
    plt.hist(drift,bins = intervals, alpha=0.5)
        
    plt.xlabel(label_x ,fontsize=20)
    plt.ylabel('Counts',fontsize=20)
    plt.tick_params(labelsize=17)
    if save_figs == True:
        saveResults_hist = os.path.join(save_path, project+ \
                                folder+ \
                                date +  \
                                measurementPurposeShort + \
                                in_results +  \
                                subfolder + \
                                file +  \
                                iteration + \
                                str('Histogram')+ \
                                fileType_img) 
        # plt.savefig(saveResults_hist)

# In case we want a normalize gaussian fit, we can do it here...
if plot_hist == True and fit_hist == True:
    
    data = np.random.normal(0, 1, 1000)
    plt.figure(num=5, figsize=size_fig, dpi=fig_resolution) 
    _, bins, _ = plt.hist(drift, intervals, density=1, alpha=0.5)
    mu, sigma = scipy.stats.norm.fit(drift)
    best_fit_line = scipy.stats.norm.pdf(bins, mu, sigma)
    plt.plot(bins, best_fit_line)
    plt.xlabel(label_x ,fontsize=20)
    if save_figs == True:
        saveResults_hist_fit = os.path.join(save_path, project+ \
                                folder+ \
                                date +  \
                                measurementPurposeShort + \
                                in_results +  \
                                subfolder +\
                                file +  \
                                iteration + \
                                str('Fitted_Histogram')+ \
                                fileType_img) 
        # plt.savefig(saveResults_hist_fit)