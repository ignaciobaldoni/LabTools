# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 17:47:45 2021

@author: ibaldoni
"""
from labTools_utilities import dataStructureConvention as nameConv
from labTools_utilities import saveDictToHdf5
from oscilloscope.MSOX3000 import MSOX3000
from os import environ
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class Osc_DSOX2004A:
    '''
    A class for controlling Keysight DSOX2004A Oscilloscope'
    '''
    
    def __init__(self, ResourceStr, label = None):
        '''
        Creates a new instrument instance and attempts connection. 
        
        Parameters:
        -----------
        resource : str
            A string containing the VISA address of the device.
        label : str
            The name of the device that will be used to label data uniquely.
        
        Returns:
        ----------
        N/A
        '''
        
        ################################################################################
        # interface to connect to oscilloscope
        resource = environ.get('MSOX3000_IP',ResourceStr)
        # create your visa instrument
        self.instr = MSOX3000(resource)
        self.instr.open()
    
    def disconnect(self):
        self.instr.close()
        
    def get_trace(self,fileName, plots = True, data_to_csv = False):
        
        # information about setup (Only available on hdf5 files)
        
        dict_SetupConfiguration = {}
        
        # function generator used
        dict_SetupConfiguration['functionGenerator/name'] \
            = 'Rigol DG4162'
        dict_SetupConfiguration['functionGenerator/functionType'] \
            = 'ramp'
        dict_SetupConfiguration['functionGenerator/frequency_Hz'] \
            = 60
        dict_SetupConfiguration['functionGenerator/amplitude_VPP'] \
            = 6   
            
        # laser used 
        dict_SetupConfiguration['laser/name'] = 'RIO Orion Laser Module'
        dict_SetupConfiguration['laser/wavelength_nm'] = 1542
        dict_SetupConfiguration['laser/powerSetting_mW'] = 20
           

        channel1 = '1'
        channel2 = '2'
        channel3 = '3'
        
        
        dict_SetupConfiguration['oscilloscope/name'] \
            = 'Keysight DSOX2004A'
        dict_SetupConfiguration[('oscilloscope/'
                                 'channel1')] \
            = channel1
            
        dict_SetupConfiguration[('oscilloscope/'
                                 'channel2')] \
            = channel2
            
        dict_SetupConfiguration[('oscilloscope/'
                                 'channel3')] \
            = channel3
        

        ################################################################################
        # Measurement inputs
        ################################################################################
        dict_measurementData = {}
         
        # read channel 1 
        self.instr.channel = channel1
        channel1_trace = self.instr.waveform()
        dict_measurementData['channel1_trace'] \
            = channel1_trace
            
        # read channel 2
        self.instr.channel = channel2
        channel2_trace = self.instr.waveform()
        dict_measurementData['channel2_trace'] \
            = channel2_trace
         
        # read channel 3
        self.instr.channel = channel3
        channel3_trace = self.instr.waveform()
        dict_measurementData['channel3_trace'] \
            = channel3_trace
         
        
        
        ################################################################################
        # save data
        ################################################################################\
        dict_measurementResult = {
            'measurementSetupInformation' : dict_SetupConfiguration,
            'measurementData' : dict_measurementData
            }
        
        saveDictToHdf5.save_dict_to_hdf5(
            dict_measurementResult, 
            fileName)
        
        if plots == True:  
            time = channel1_trace['time_axes']
            volt = channel1_trace['voltage_axes']
            plt.plot(time,volt)
            volt = channel2_trace['voltage_axes']
            plt.plot(time,volt)
            volt = channel3_trace['voltage_axes']
            plt.plot(time,volt)
            
            plt.title(str(fileName),fontsize=20)
            plt.ylabel('Channel data (V)',fontsize=20)
            plt.xlabel('Time (s)',fontsize=20)
            plt.tick_params(labelsize=17)
            plt.grid()
            plt.show()
        
        if data_to_csv == True:
            
            dict_Result = saveDictToHdf5.load_dict_from_hdf5(fileName)
        
            timeTrace = dict_Result['measurementData'] \
                                        ['channel1_trace'] \
                                        ['time_axes']
            # timeTrace = timeTrace*1000  # Time in ms
    
            channel1_trace = dict_Result['measurementData'] \
                                        ['channel1_trace'] \
                                        ['voltage_axes']
            
            channel2_trace \
                = dict_Result['measurementData'] \
                            ['channel2_trace'] \
                            ['voltage_axes']
            
            channel3_trace \
                = dict_Result['measurementData'] \
                            ['channel3_trace'] \
                            ['voltage_axes']

            df = pd.DataFrame(data=[timeTrace,
                                    channel1_trace, 
                                    channel2_trace,
                                    channel3_trace],
                                      ).T
            df.columns =['time','Channel 1','Channel 2','Channel 3']
            df.to_csv(fileName+'.csv',index= False)
        
    


if __name__ == '__main__':
    
    resourceStr =  'USB0::0x2A8D::0x1766::MY60104389::INSTR'
    osci = Osc_DSOX2004A(resourceStr)
    
    fileName = 'Example' # Set folder and filename to save
    
    osci.get_trace(fileName, plots = False, data_to_csv=False)