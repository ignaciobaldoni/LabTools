'''
Created on 11.08.2016

@author: Arne
'''
import visa
import matplotlib.pyplot as plt
import numpy as np

####################################################################################
# List all connected devices
####################################################################################

resourceManager = visa.ResourceManager()
deviceList = resourceManager.list_resources()
    
    ################################################################################
    # Log information
print(deviceList)
    ################################################################################

####################################################################################
# Connect to device and get device Information
####################################################################################
    
    # connect to first devices in the deviceList
instrumentManager = resourceManager.open_resource(deviceList[0])

    # collect device informations
deviceIdentifyInfo = instrumentManager.query('*IDN?')
deviceOptionList = instrumentManager.query('*OPT?')    
    ################################################################################
    # Log information
print(deviceIdentifyInfo)
    ################################################################################


####################################################################################
# initialize instrument & setup device
#
# commands:
#    *rst ... restor default settings
#    *TST? ... device self test run -> 0 is good, anything else bad
#    :AUToscale
#    
####################################################################################


## instrumentManager.write("*rst; status:preset; *cls")

####################################################################################
# take measurement 
# 
#
#     :ACQuire:TYPE NORMal | AVERage | HRESolution | PEAK
#     :ACQuire:COUNt 2 to 65536 (number of averages)
#     :ACQuire:POINts?
#     :ACQuire?
#
#     :CHANnel<n>:COUPling[?] {AC | DC} 
#     :CHANnel<n>:DISPlay[?] ON or OFF
#     :CHANnel<n>:IMPedance[?] {ONEMeg | FIFTy}
#     :CHANnel<n>:OFFSet[?] value {V | mV}
#     :CHANnel<n>:RANGe[?] <range>{V | mV} (from 8 mV to 40 V, with probe 1)
#     :CHANnel<n>:SCALe[?] <scale>{V | mV}
#
#     :TIMebase:POSition[?] <pos> ::= time in seconds from the trigger to the display reference in NR3 format
#     :TIMebase:RANGe[?] <range_value> time for 10 div in seconds in NR3 format
#     :TIMebase:SCALe[?] <scale_value> time/div in seconds in NR3 format
#
#     :DIGitize CHANnel<n>
#            The :DIGitize command is a specialized RUN command. It causes the instrument
#            to acquire waveforms according to the settings of the :ACQuire commands
#            subsystem. When the acquisition is complete, the instrument is stopped.
#            Example: instrumentManager.write("DIGitize CHANnel1")
#     *TRG (Trigger) ... same as :DIGitize without parameter
#     :RUN
#     :SINGLe
#     :STOP
#     :STATus? CHANnel<n>
####################################################################################


     
     
####################################################################################
# read out data
#
#     :WAVeform 
#     :WAVeform:POINts[?] <# points>
####################################################################################
    # set read out channel 
instrumentManager.write(":WAVeform:SOURce CHANnel1")
    # set read out format
instrumentManager.write(":WAVeform:FORMat BYTE")
    # read channel
yAxesData = instrumentManager.query_binary_values(":WAVeform:DATA?",datatype='B')     

XINCrement = instrumentManager.query_ascii_values(':WAVeform:XINCrement?')
XORigin = instrumentManager.query_ascii_values(':WAVeform:XORigin?')
XREFerence = instrumentManager.query_ascii_values(':WAVeform:XREFerence?') # should always be zero 

numOfPoints = len(yAxesData)

xAxes = np.array(range(numOfPoints))*XINCrement+XORigin

YINCrement = instrumentManager.query_ascii_values(':WAVeform:YINCrement?')
YORigin = instrumentManager.query_ascii_values(':WAVeform:YORigin?')
YREFerence = instrumentManager.query_ascii_values(':WAVeform:YREFerence?')

calyAxesData = (np.array(yAxesData)-yAxesData[int(YREFerence[0])])*YINCrement[0]

####################################################################################
# save data
####################################################################################   


####################################################################################
# plot data
####################################################################################   
plt.plot(xAxes,calyAxesData)
plt.ylabel('some numbers')
plt.show()

