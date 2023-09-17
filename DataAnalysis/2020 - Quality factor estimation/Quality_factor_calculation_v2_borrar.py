# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 17:37:49 2021

@author: ibaldoni
"""


from labTools_utilities import saveDictToHdf5
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import os.path
from matplotlib.image import NonUniformImage

from scipy import interpolate as interp
from scipy import optimize

# We select the plots and results we want to see
plots                   = True
plot_hist               = False
swipe_to_mean           = False
hist2d_v2_misaligned    = False

cross_correlation       = False

freq_trace              = False
save_figs               = True 
plot_drift              = False
New_Analysis            = True

Q_calculation           = True
#normalizing             = False

Q_total     = []
wavelength  = []


fileType_img = '.png' 
size_fig    = (12,8)
fig_resolution = 100    # a.k.a., dpi

num_points = 50000

fsr_flc = 180.3

begin_scan  = 1520.05
finish_scan = 1570.0


step_size   = 0.1

folder                  = ''
measurementPurposeShort = 'Quality_factor_F3_1550_v2/'
subfolder               = ''
file                    = 'linewidth_'


######################### LOAD FILE ##########################################

year = dt.datetime.today().year
month = dt.datetime.today().month
day =  dt.datetime.today().day

month = '0'+str(month) if len(str(month)) == 1 else month
day = '0'+str(day) if len(str(day)) == 1 else day

save_path = '//menloserver/MFS/03-Operations/02-DCP/03-Entwicklungsprojekte/'
project = '9556-COSMIC/'
main_folder = '52-Messergebnisse/'
fileType = '.h5'

### Today
date = str(year)+str(month)+str(day)

in_raw_data = '1-Raw Data/' 
in_data_analysis = '2-Data Analysis/' 
in_results  = '3-Results/'

subfolder_time = 'Time trace/'
subfolder_freq = 'Frequency trace/'

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
print(number_of_traces)
###############################################################################

# List to enumerate the drifts, respect to zero in the different traces
# Zero is defined for all the traces as the first resonance of the FLC 
drift           = []
drift_amplitude = []
All_traces      = []
drifts_to_zero  = []
hist_time       = []
trace_number    = []


n_points    = int((finish_scan - begin_scan)/step_size) 

scan_ = np.arange(begin_scan,finish_scan,step_size) 
count_ = 0
Q_before = 0
if New_Analysis == True:
    for i in scan_[200:250]:
        
        
            
        iteration   = str(np.round(i,2))
    
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
        
        
    
        # We find the lowest point from the transmission.
        # Value and position although only the position is what we care about
        # It will be the point to follow when a drift in frequency exists. 
            
        max_generatedLightTrace = np.max(ringResonatorTransmissionTrace)
        min_generatedLightTrace = np.min(ringResonatorTransmissionTrace)
        peak_generatedLight = np.where(ringResonatorTransmissionTrace==min_generatedLightTrace)
        



        
#         In case the signal is lost and the traces are spurios we consider only 
#         the ones that are useful
        
        if np.abs(max_generatedLightTrace - min_generatedLightTrace) \
                    > 0.5*max_generatedLightTrace:
                    
            
            count_ +=1
            
            if Q_calculation == True:
                peak_generatedLight = np.where(ringResonatorTransmissionTrace
                                               ==min_generatedLightTrace)
                
                ### We select the one from the middle, in case there are many
                if len(peak_generatedLight[0]) > 2:
                    
                    peak_generatedLight = int(0.5*(peak_generatedLight[0][-1]+\
                                                   peak_generatedLight[0][0]))

                    
                else:
                    peak_generatedLight = peak_generatedLight[0][0]
                
###     We reduce the window only on the resonance which we are interested in                
                magic_number0 = 1000
                
                min_trace = peak_generatedLight - magic_number0
                max_trace = peak_generatedLight + magic_number0
                
                # We redefine all the traces accordingly
                
                timeTrace                       = timeTrace[min_trace:max_trace]
                ringResonatorTransmissionTrace  = ringResonatorTransmissionTrace[min_trace:max_trace]
                voltageTrace                    = voltageTrace[min_trace:max_trace]
                functionGeneratorTrace          = functionGeneratorTrace[min_trace:max_trace]
                
                plt.figure()
                plt.plot(timeTrace,ringResonatorTransmissionTrace)
                plt.plot(timeTrace,voltageTrace)
                print(i)

                

#                from scipy import interpolate as interp
                from scipy.signal import find_peaks
                fiber_resonator = -voltageTrace    # We invert the signal to get the peaks
            
                magic_number1 = 1.01*np.max(fiber_resonator)
                magic_number3 = num_points*0.001 #Distance between peaks 
        
                peaks, _ = find_peaks(fiber_resonator, 
                                      height = magic_number1, 
                                      distance = magic_number3,
                                      prominence = magic_number1)   
                
                 # This might need an improvement.
                FSR = fsr_flc
                dt = timeTrace[peaks]
                df = []
                for h in range(0,len(peaks)):
                    df.append(FSR*(h-len(peaks)+1))
                    
                # We get the frequency according to the position of the calibration FLC
                freq_x = interp.interp1d(dt, df,fill_value="extrapolate")
                freq = freq_x(timeTrace)
                
                
                # Time trace now becomes a frequency. 
                if freq_trace == True:
                    timeTrace = freq
                    label_x = 'Frequency (MHz)'
                    subfolder2 = 'Frequency trace/'
                else:
                    label_x = 'time (s)'
                    subfolder2 = 'Time trace/'
                    
                    
                res     = ringResonatorTransmissionTrace
                
                wl_nm   = i
                
                res_max = np.max(res)
                minimo_ind = peak_generatedLight
                
                
                def _1lorentz(t, amp,cen,wid):
                   return (amp*wid**2/((t-cen)**2+wid**2))*(-1) +res_max
               
                initial_values = [0.1,freq_x(timeTrace[magic_number0]),180]
                
                popt_lorentz, pcov_lorentz = optimize.curve_fit(_1lorentz, freq, res, p0=initial_values,maxfev=1000)
                
                FHWM = np.abs(2*popt_lorentz[2])
                print(FHWM,'MHz')
                c = 299792458   # Speed of light
                vo = c/(wl_nm*1e-9)
                
                Q = vo/(FHWM*1e6)   
                print(Q*1e-6,'mill.')
                texto = 'Linewidth ='+str(np.round(FHWM,2))+' MHz\nQ factor = '+str(np.round(Q*1e-6,3))+' mill.' 
                
                if plots == True:
                    fig = plt.figure(figsize=size_fig)
                    plt.plot(freq,res,'-', label='Resonator')
    #                plt.plot(freq,voltageTrace,label = 'Fiber resonator')
    #                plt.plot(freq[peaks],voltageTrace[peaks],'go')
                    plt.plot(freq,_1lorentz(freq,*popt_lorentz),label='fit')
                    plt.text(-20,0.1,texto,fontsize = 17)
                    plt.tick_params(labelsize=17)
                    plt.legend()
                    plt.xlabel(label_x ,fontsize=20)
                    if save_figs == True:
                        saveResults = os.path.join(save_path, project+ \
                                            main_folder+ \
                                            folder+\
                                            date +  \
                                            measurementPurposeShort + \
                                            in_results +  \
                                            subfolder + \
                                            subfolder_freq +\
                                            file +  \
                                            iteration + \
                                            fileType_img) 
                        # plt.savefig(saveResults)
                        plt.close()  
                
                Q_total.append(Q*1e-6)
                Q_before = Q
                wavelength.append(np.round(i,2))

                    
                
                
print (number_of_traces, count_)

for i in range(0, len(Q_total)):
    print(i)
    if Q_total[i]>4*np.mean(Q_total):
        Q_total[i]      = 0
        wavelength[i]   = 0
wl_plot = [i for i in wavelength if i != 0]
Q_plot  = [i for i in Q_total if i != 0]

fig = plt.figure(figsize=size_fig)
plt.plot(wl_plot,Q_plot,'o-')
plt.tick_params(labelsize=17)
plt.xlabel('Wavelength (nm)' ,fontsize=20)
plt.ylabel('Quality Factor (mill.)' ,fontsize=20)
if save_figs == True:
    saveResults = os.path.join(save_path, project+ \
                        main_folder+ \
                        folder+\
                        date +  \
                        measurementPurposeShort + \
                        in_results +  \
                        str('Q_total') +  \
                        fileType_img) 
    # plt.savefig(saveResults)