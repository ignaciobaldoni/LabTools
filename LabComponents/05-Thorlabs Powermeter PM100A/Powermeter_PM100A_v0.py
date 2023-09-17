# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 14:34:36 2021

@author: ibaldoni
"""

import pyvisa as visa


class Thorlabs_PM100A:
    '''
    A class for controlling Thorlabs PM-100A Powermeter
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
          
          

    def readPower(self):
        '''

        Returns measured power in mW
        -------

        '''
        
        self.visaobj.write('SENS:CURR:RANG:AUTO ON\n')
        power = self.visaobj.query_ascii_values('Measure:Scalar:POWer?')[0]
        power_mW = power*1e3
        print(power_mW,'mW')
        return power_mW


if __name__ == '__main__':

    resourceStr = 'USB0::0x1313::0x8079::P1001184::INSTR'
    powermeter = Thorlabs_PM100A(resourceStr)
    power = powermeter.readPower()
    