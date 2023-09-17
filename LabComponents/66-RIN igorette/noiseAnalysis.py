# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 13:07:50 2021

@author: akordts
"""


##### python standard libs
import numpy as np
import matplotlib.pyplot as plt

##### user defined code libs
from Utilities import saveDictToHdf5


##############################################################################
# helper functions
##############################################################################
def plotRinFigure(freqValues,powValues,dc_voltage_V,legendStr):
    rinVal = 20*np.log10(np.array(powValues)/dc_voltage_V)
    plt.plot(freqValues, rinVal,  label = legendStr,linewidth=2)
    

    
def initFigure(figNum,dc_voltage_V):
    plt.figure(figNum)
    plt.rcParams.update({'font.size': 16})
    textstr = '$\mathrm{U}_{\mathrm{dc} = }$' + str(dc_voltage_V) + ' V'

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    
    # place a text box in upper left in axes coords
    ax = plt.gca()
    ax.text(0.95, 0.75, textstr, transform=ax.transAxes, fontsize=16,
            verticalalignment='center',horizontalalignment='center', bbox=props)
    
    ax.set(xlabel='frequency [Hz]', ylabel=r'RIN [dBc/Hz]' )
    ax.grid()
    
    ax.set_xscale('log')
    ax.legend()
    
    ax.set_ylim([-180,-80])
    ax.set_xlim([1e-1,1e7])
    
##############################################################################
# tasks
##############################################################################

# analysis of noise data 

# subtrackting detector background, check for correction due to non-linearity

# does the measurement can reach the noise limitation of the ESA
# is there an inidcation for shot noise

##############################################################################
# data file locations
##############################################################################


###############################################################################
########## PSD data 

# file with rio laser specctrum 
path_PSD_rioLaser = \
    r'\\menloserver\MFS\03-Operations\02-DCP\03-Entwicklungsprojekte\9556-COSMIC\52-Messergebnisse\20210919-ARK - amplitude noise characterisation\rawData\20210925-1454-ARK- PS configuration - rio laser\1506_PS configuration - high freq.h5'
    
# file with detector background

path_PSD_detectorbackground = \
    r'\\menloserver\MFS\03-Operations\02-DCP\03-Entwicklungsprojekte\9556-COSMIC\52-Messergebnisse\20210919-ARK - amplitude noise characterisation\rawData\20210919-1340-ARK- PSD configuration - detector background\1340_rio_laser_1542nm_det2_noOptInput.h5'

###############################################################################
########## PS data 
    
# file with detector background

path_PS_detectorbackground = \
    r'\\menloserver\MFS\03-Operations\02-DCP\03-Entwicklungsprojekte\9556-COSMIC\52-Messergebnisse\20210919-ARK - amplitude noise characterisation\rawData\20210924-1033-ARK-PS configuration - detector background high res\1033_PS configuration - detector background high res.h5'

###############################################################################
########## cross correlation data 

# file with ESA background
path_ESA_background = \
        r'\\menloserver\MFS\03-Operations\02-DCP\03-Entwicklungsprojekte\9556-COSMIC\52-Messergebnisse\20210919-ARK - amplitude noise characterisation\rawData\20210920-1034-ARK - CorssCor configuration - ESA background - 4 x avg\1034_CorssCor configuration - ESA background - 4 x avg.h5'

# file with detector background
path_detectorSpectum = \
    r'\\menloserver\MFS\03-Operations\02-DCP\03-Entwicklungsprojekte\9556-COSMIC\52-Messergebnisse\20210919-ARK - amplitude noise characterisation\rawData\20210923-1806-ARK-CrossCor configuration - detector background - high res\1806_CrosCor configuration - detector background high res.h5'

# file with rio laser specctrum 
rioSpectrumPath = \
    r'\\menloserver\MFS\03-Operations\02-DCP\03-Entwicklungsprojekte\9556-COSMIC\52-Messergebnisse\20210919-ARK - amplitude noise characterisation\rawData\20210922-1750-ARK - CrossCor configuration - rio laser high res\1750_CrossCor configuration - rio laser - quite choir pos.h5'

##############################################################################
##############################################################################

################################################################################
### load data
################################################################################

###############################################################################
########## PSD data 

dict_Result = saveDictToHdf5.load_dict_from_hdf5(path_PSD_rioLaser)

PSD_rioLaser_freqValues_Hz = dict_Result['MeasurementData']['freqValues_Hz']
# PSD_rioLaser_freqValues_Hz = PSD_rioLaser_freqValues_Hz[1601:]
PSD_rioLaser_powValues_Vrms_rtHz = dict_Result['MeasurementData']['powValues_Vrms_rtHz']
# PSD_rioLaser_powValues_Vrms_rtHz = PSD_rioLaser_powValues_Vrms_rtHz[1601:]
PSD_rioLaser_dc_voltage_V = dict_Result['MeasurementData']['dc_voltage_V']

dict_Result = saveDictToHdf5.load_dict_from_hdf5(path_PS_detectorbackground)

PSD_detBackgroundSpectrum_freqValues_Hz = dict_Result['MeasurementData']['freqValues_Hz']
PSD_detBackgroundSpectrum_freqValues_Hz = PSD_detBackgroundSpectrum_freqValues_Hz[1601:]
PSD_detBackgroundSpectrum_powValues_Vrms_rtHz = dict_Result['MeasurementData']['powValues_Vrms_rtHz']
PSD_detBackgroundSpectrum_powValues_Vrms_rtHz = PSD_detBackgroundSpectrum_powValues_Vrms_rtHz[1601:]
PSD_detBackgroundSpectrum_dc_voltage_V = dict_Result['MeasurementData']['dc_voltage_V']


###############################################################################
########## cross correlation data 

# rio laser
dict_Result = saveDictToHdf5.load_dict_from_hdf5(rioSpectrumPath)

rioLaser_freqValues_Hz = dict_Result['MeasurementData']['freqValues_Hz']
rioLaser_powValues_Vrms_rtHz = dict_Result['MeasurementData']['powValues_Vrms_rtHz']
rioLaser_dc_voltage_V = dict_Result['MeasurementData']['dc_voltage_V']

# detecctor background
dict_Result = saveDictToHdf5.load_dict_from_hdf5(path_detectorSpectum)

detBackgroundSpectrum_freqValues_Hz = dict_Result['MeasurementData']['freqValues_Hz']
detBackgroundSpectrum_powValues_Vrms_rtHz = dict_Result['MeasurementData']['powValues_Vrms_rtHz']
detBackgroundSpectrum_dc_voltage_V = dict_Result['MeasurementData']['dc_voltage_V']

# esa Background
dict_Result = saveDictToHdf5.load_dict_from_hdf5(path_ESA_background)

detESA_Background_freqValues_Hz = dict_Result['MeasurementData']['freqValues_Hz']
detESA_Background_powValues_Vrms_rtHz = dict_Result['MeasurementData']['powValues_Vrms_rtHz']
detESA_Background_dc_voltage_V = dict_Result['MeasurementData']['dc_voltage_V']

###############################################################################
### plot data - rio orion crossCor 
###############################################################################

figNum = 1
dc_Voltage = rioLaser_dc_voltage_V
fig = plt.figure(figNum)
plt.clf()

plt.title('Performance comparison of RIN measurement methods')

# cross cor
plotRinFigure(
        rioLaser_freqValues_Hz,
        rioLaser_powValues_Vrms_rtHz,
        dc_Voltage,
        r"$\bf{CSD}$: RIO ORION 1542nm Laser Module"
    )

# PSD rio
plotRinFigure(
        PSD_rioLaser_freqValues_Hz,
        PSD_rioLaser_powValues_Vrms_rtHz,
        PSD_rioLaser_dc_voltage_V,
        r'$\bf{PSD}$: RIO ORION 1542nm Laser Module'
    )

# crosscor background
plotRinFigure(
        detBackgroundSpectrum_freqValues_Hz,
        detBackgroundSpectrum_powValues_Vrms_rtHz,
        dc_Voltage,
        r'$\bf{CSD}$: noise floor'
    )

# PSD background
plotRinFigure(
        PSD_detBackgroundSpectrum_freqValues_Hz,
        PSD_detBackgroundSpectrum_powValues_Vrms_rtHz,
        dc_Voltage,
        r'$\bf{PSD}$: noise floor'
    )




initFigure(figNum,dc_Voltage)

# ###############################################################################
# ### plot data - improvement  
# ###############################################################################

# figNum = 2
# dc_Voltage = 4.5
# fig = plt.figure(figNum)
# plt.clf()

# # crossCor background
# plotRinFigure(
#         detBackgroundSpectrum_freqValues_Hz,
#         detBackgroundSpectrum_powValues_Vrms_rtHz,
#         dc_Voltage,
#         'RIO ORION 1542nm Laser Module'
#     )

# # PSD background
# plotRinFigure(
#         PSD_detBackgroundSpectrum_freqValues_Hz,
#         PSD_detBackgroundSpectrum_powValues_Vrms_rtHz,
#         dc_Voltage,
#         'Measurement background'
#     )

# initFigure(figNum,rioLaser_dc_voltage_V)

# plotRinFigure(
#         detESA_Background_freqValues_Hz,
#         detESA_Background_powValues_Vrms_rtHz,
#         detESA_Background_dc_voltage_V,
#         'ESA Background'
#     )




# diffPowValues = np.sqrt(
#             np.array(rioLaser_powValues_Vrms_rtHz)**2
#             - np.array(detBackgroundSpectrum_powValues_Vrms_rtHz)**2 
#     )

# plotRinFigure(
#         rioLaser_freqValues_Hz,
#         diffPowValues,
#         rioLaser_dc_voltage_V,
#         'rio laser minus background'
#     )



# ax.set(xlabel='frequency [Hz]', ylabel=r'power $\left[\mathrm{V}_{\mathrm{rms}}/\sqrt{\mathrm{Hz}}\right]$' )



    




plt.show()