# coding=utf-8
'''
Coded by IZ
08.11.2021
as a template TCH_v3.5.py of ORS was used
!!!: before operating allantools module should be installed
'''

########## IMPORTS ##########
import allantools as at
import numpy as np
#from scipy import signal
import pandas as pd
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join
#import math

#format = '%H%M%S.%f' # didn't use it, because we had only fast measurements

###### DEFINE THE PATH ######
path=r"D:\Working Materials\Articles\Projects\Frequency Stabilization\From MENLO\Data\20211105-ARK-IZ-FXE Stability characterization\correctedData"

path=r"C:\Users\akordts\Desktop\FXE test"

#path=r"D:\Working Materials\Articles\Projects\Frequency Stabilization\From MENLO\Data\20211103-IZ-Test experiment\Data"


path_corr = path+'\\corr_time\\'
path_pics = path+'\\ResPics\\'

colorlist=['#00441b','#762a83','#5aae61','#d395dd','darkblue','darkblue','darkblue','darkblue']
markerlist=['-o','-v','-s','p','v','s','o','v']


filenames = [f for f in listdir(path) if isfile(join(path, f))] # Extract only filenames from the folder
file_num = [] #specific number of file corresponds to the measurement
print(filenames)
for f in filenames:
    file_num.append(f.split('_')[1])
print(file_num)

#filenames=['211105_11_Frequ.txt']  # just to debug
### code for process the signle file for one channel

### Constants and parameters###
rep_rate_measured = 37e6 #1.2126587e10 # repetition rate in Hzs: 12.126587 GHz  measured by ESA
optical_frequency = 194.417936e12
chosen_parameter = 'pump_beat' # can be 'rep_rate' or 'pump_beat' in order to change the parameter we want to analyze
t_tau=np.array([0.001, 0.01, 0.1, 1, 10, 100])

comparison_set = ['10', '11', '12'] # three sets [8,10] and [9,11]
comparison_labels=['PDH','Pump res lck', 'Rep rate lck']


# font sizes in ADEV plot
label_font_size=18
tick_font_size=14
title_font_size=20 #24

ax = plt.axes()
ax.set_title("ADEV {}".format(chosen_parameter), fontsize=title_font_size) #ADEV_plot_title
ax.set_xscale('log')
ax.set_yscale('log')
ax.grid(b=True, which='major', color='k', linestyle='-')  # style of major grid lines
ax.grid(b=True, which='minor', color='grey', linestyle='--')  # style of minor grid lines
ax.set_xlabel(r'Integration Time, $\tau$ (s)', fontsize=label_font_size)  # label of x axis
ax.set_ylabel(r'ADEV, $\sigma_\tau$', fontsize=label_font_size)  # label of y axis
#ax.ticks(fontsize=tick_font_size)
#ax.yticks(fontsize=tick_font_size)


if (chosen_parameter == 'pump_beat'):
    column_number = int('3')
elif (chosen_parameter == 'rep_rate'):
    column_number = int('4')
else:
    print('Choose the correct parameter')
    exit()

######## FUNCTION DEFINITIONS ############ (I don't use them, can be found in main_0.py in 'scripts' folder)

###### MAIN SCRIPT ######
#Read data from file
for filename in filenames:
    df_tmp=pd.read_csv(path+"/"+filename,delimiter=r"\s+",header=None, skiprows=11, usecols=[column_number], float_precision='high')    # reads the csv file
    #print(filename)
#Data and correct timetags for the
    time_index = df_tmp.index
    time_data = np.arange(len(time_index))/1000 # time in miliseconds
    freq_data = np.array(df_tmp.iloc[:,0])
    freq_data_avg = freq_data.mean()
    #freq_data_norm = freq_data/freq_data_avg # just normalisation case
    freq_data_norm = (freq_data-freq_data_avg)/freq_data_avg
    freq_data_optical = (freq_data-freq_data_avg)/optical_frequency
    #print(time_data, freq_data_norm)

### Create a corrected timetag file
    df_load = pd.DataFrame({"timetag" : time_data, "normalized frequency" : freq_data_norm})
    df_load.to_csv(path_corr+file_num[filenames.index(filename)]+chosen_parameter+".txt", index=False, sep=' ')

    
### PLOT RAW DATA ###
    plt.figure()  # Plot
    plt.plot(time_data,freq_data_norm)
    plt.grid(True, axis='both', which='both', ls='-')
    plt.xlabel("Time (s)")
    plt.ylabel("Fractional frequency (rel. u.) ")
    # plt.ylim([-1,1])
    plt.title("Chosen parameter  {}, file {}".format(chosen_parameter, file_num[filenames.index(filename)]))
    plt.tight_layout()
    plt.savefig(path_pics+'Data_'+chosen_parameter+'_'+file_num[filenames.index(filename)]+'.png', dpi = 150)
    plt.clf()
    #plt.show()

    ### Allan deviation calculation
    (t2, ad, ade, adn) = at.adev(freq_data_norm, rate=1e3, data_type="freq", taus="decade") #for automatic generated timescales
    #(t2, ad, ade, adn) = at.adev(freq_data_optical, rate=1e3, data_type="freq",taus="decade")  # for automatic generated timescales and optical carrier correction
    (t2_tau, ad_tau, ade_tau, adn_tau) = at.adev(freq_data_norm, rate=1e3, data_type="freq", taus=t_tau) # for chosen timescales
    ad_1s = ad_tau[3] # checking Allan deviation for 1s averaged time

    
    ### Create files with Allan Deciation
    Allan_load = pd.DataFrame({"Int_Time": t2, "ADEV": ad, "ADErr":ade})
    Allan_load.to_csv(path +'\ADfiles\ADEV-'+ file_num[filenames.index(filename)] + chosen_parameter + ".txt", index=False, sep=' ')
   
    if (chosen_parameter == 'rep_rate'):
        print("Allan deviation @ 1s: {} ".format(ad_1s))
        freq_delta = ad_1s*rep_rate_measured
        freq_shift = ad * rep_rate_measured
        print("Frequency deviation @ 1s: {} Hz for measured {} GHz".format(freq_delta,rep_rate_measured*1e-9))
    elif(chosen_parameter == 'pump_beat'):
        print("Allan deviation @ 1s: {} ".format(ad_1s))
        freq_delta = ad_1s * freq_data_avg
        freq_shift = ad * freq_data_avg
        print("Frequency deviation @ 1s: {} Hz".format(freq_delta))
 
    ### Draw Allan dev plot ###
    # fig_allan = plt.loglog(t2, ad, '-o')
    fig_allan = plt.loglog(t2, freq_shift, '-o')
    plt.title("ADEV @ 1s: {:e} ".format(ad_1s), fontsize=title_font_size) #ADEV_plot_title
    #plt.title("Freq_sh @ 1s: {:e} Hz".format(freq_delta), fontsize=title_font_size)  # ADEV_plot_title
    plt.grid(b=True, which='major', color='k', linestyle='-')  # style of major grid lines
    plt.grid(b=True, which='minor', color='grey', linestyle='--')  # style of minor grid lines
    plt.xlabel('Integration Time (s)', fontsize=label_font_size)  # label of x axis
    #plt.ylabel('ADEV', fontsize=label_font_size)  # label of y axis
    plt.ylabel('Freq, Hz', fontsize=label_font_size)  # label of y axis
    plt.xticks(fontsize=tick_font_size)
    plt.yticks(fontsize=tick_font_size)
    plt.tight_layout()
    plt.savefig(path_pics+'Allan Deviation\\ADEV_'+chosen_parameter+'_'+file_num[filenames.index(filename)]+'.png', dpi = 150)
    #plt.savefig(path_pics+'FreqShift/FSh_'+chosen_parameter+'_'+file_num[filenames.index(filename)]+'.png', dpi = 150)
    plt.clf()
    #plt.show()
    
    #### PLOT GRAPHS FOR COMPARISON #####
    if file_num[filenames.index(filename)] in comparison_set:
        #print(file_num[filenames.index(filename)])
        print(comparison_labels[comparison_set.index(file_num[filenames.index(filename)])])
        ax.errorbar(t2,ad, yerr=ade, fmt = markerlist[comparison_set.index(file_num[filenames.index(filename)])], label =comparison_labels[comparison_set.index(file_num[filenames.index(filename)])])
plt.legend()
plt.tight_layout()
plt.savefig(path_pics+'Comparison/ADEV_'+chosen_parameter+'.png', dpi = 150)
plt.clf()
#plt.show()