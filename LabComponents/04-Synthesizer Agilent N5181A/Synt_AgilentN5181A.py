# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 12:01:37 2021

@author: ibaldoni
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time

class AN5181A:
    '''
    A class for controlling the Agilent N-5181A Synthesizer
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
          self.visaobj.timeout = 2000
          queryStr = '*IDN?'
          data = self.visaobj.query(queryStr)
          print('idns answer: '+ str(data)) 
        except visa.VisaIOError as e:
          print(e.args)
          raise SystemExit(1)
          
    def enable(self):
        """ Enables the output of the signal. """
        self.visaobj.write(":OUTPUT ON;")

    def disable(self):
        """ Disables the output of the signal. """
        self.visaobj.write(":OUTPUT OFF;")
        
    def read_frequency(self):
        '''
        Current frequency
        '''
        self.visaobj.timeout = 60000 # set timeout to 60s for measurement
        data = self.visaobj.query(':FREQ?')
        self.visaobj.timeout = 2000 # set timeout back to 2s

        return data  
    
    def read_amplitude(self):
        '''
        Current frequency
        '''
        self.visaobj.timeout = 60000 # set timeout to 60s for measurement
        data = self.visaobj.query(':POW?')
        self.visaobj.timeout = 2000 # set timeout back to 2s

        return data  
    
    def set_frequency(self,value):
        '''
        Set frequency in MHz
        '''
        self.visaobj.timeout = 6000 # set timeout to 60s for measurement
        word = "FREQuency:FIXed {} MHz".format(str(value))
        data = self.visaobj.write(word)
        
        return data  
    
    def set_amplitude(self,value):
        '''
        Set Amplitude in dBm 
        '''
        self.visaobj.timeout = 10000 # set timeout to 60s for measurement
        word = "POWer:LEVel {} dBM".format(str(value))
        data = self.visaobj.write(word)
        
        self.visaobj.timeout = 2000 # set timeout back to 2s
        return data  
    
    
    def disconnect(self):
        '''
        Turns off output and disconnects from the SMU. 
        
        Parameters:
        -----------
        N/A
        
        Returns:
        ----------
        N/A
        '''
        self.visaobj.control_ren(6) # sends GTL (Go To Local) command
        self.visaobj.close()  
        
    
        
if __name__ == '__main__':
    # resourceStr = 'TCPIP0::169.254.9.16::10001::SOCKET'
    resourceStr = 'TCPIP0::A-N5181A-42764::inst0::INSTR'
    
    synt = AN5181A(resourceStr)
    # print('test')
    time.sleep(1)
    
    # Test of sweeping
    for i in range(0,3):
        # In MHz
        synt.set_frequency(170+i)
    
        # In dBm
        synt.set_amplitude(1-i)
        time.sleep(2)
        
    synt.disconnect()

