# -*- coding: utf-8 -*-
"""
Created on Wed May 31 17:08:39 2023

@author: ibaldoni
"""

import pyvisa as visa
import time

class Keysight_E36312A_DC_Power_Supply:
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
          
    def setBias(self, bias,channel):
        '''

        Sets the voltage bias for the Photodiode
        -------

        '''
        
        self.visaobj.write(f':INSTrument:NSELect {channel}')
        self.visaobj.write(':OUTPut:STATe 1')
        self.visaobj.write(f':SOURce:VOLTage:LEVel:IMMediate:AMPLitude {bias}')




if __name__ == '__main__':

    resourceStr = "USB0::0x2A8D::0x1102::MY61003592::INSTR"
    DC_PowerSupply = Keysight_E36312A_DC_Power_Supply(resourceStr)
    bias = DC_PowerSupply.setBias(3.7,channel = 2)          
          
          
