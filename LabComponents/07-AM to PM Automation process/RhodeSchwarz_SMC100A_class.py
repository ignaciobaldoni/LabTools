# -*- coding: utf-8 -*-
"""
Created on Wed May 31 17:08:39 2023

@author: ibaldoni
"""

import pyvisa as visa
import time

class RhodeSchwarz_SMC100A:
    '''
    A class for controlling Keysight_DC_PowerSupply
    '''
    
    
    def __init__(self, resource, label = None):
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
        self.connect(resource, label) 
    
    def connect(self, resource, label = None):
        '''
        Connect to the instrument. 
        
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
        rm = visa.ResourceManager()
        self.label = label
        
        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
          self.visaobj = rm.open_resource(resource)
        except visa.VisaIOError as e:
          print(e.args)
          raise SystemExit(1)
          
    def setAM_depth(self, AM_depth = 10):
        '''

        Sets the AM Depth
        -------

        '''
        self.visaobj.write(f':SOURce:AM {AM_depth}PCT')
        


    def setAM_frequency_kHz(self, AM_frequency = 10):
        '''

        Sets the frequency modulation for the AM internal modulation
        -------

        '''

        self.visaobj.write(f'SOURce:LFOutput:FREQuency {AM_frequency}kHz')
        
    def setLevel(self, Level = 10):
        '''

        Sets the power level
        -------

        '''
        
        self.visaobj.write(f'SOUR:POW:LEV:IMM:AMPL {Level}')
        



if __name__ == '__main__':

    resourceStr = "USB0::0x0AAD::0x006E::108450::INSTR"
    FunctionGenerator = RhodeSchwarz_SMC100A(resourceStr)
    
    FunctionGenerator.setAM_depth(17)
    FunctionGenerator.setAM_frequency_kHz(9)  
    FunctionGenerator.setLevel(17)  
        
          
