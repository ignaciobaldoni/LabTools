# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 12:01:37 2021

@author: ibaldoni
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time

class RigolDG4162:
    '''
    A class for controlling the Rigol DG4162 Function generator
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
    
          
    def is_enable(self):
        """ Query the state of the output of the signal. """
        data = self.visaobj.query(":OUTP:STAT?")
        print(data)

    def enable(self):
        """ Enables the output of the signal. """
        self.visaobj.write(':OUTP ON')
        

    def disable(self):
        """ Disables the output of the signal. """
        self.visaobj.write(":OUTP OFF")
    
    
    def read_frequency(self):
        """ Current frequency"""
        self.visaobj.timeout = 60000 # set timeout to 60s for measurement
        data = self.visaobj.query(':FREQ?')
        self.visaobj.timeout = 2000 # set timeout back to 2s

        return data  
    
    def read_amplitude(self):
        """ Current amplitude """
        
        self.visaobj.timeout = 60000 # set timeout to 60s for measurement
        data = self.visaobj.query(':POW?')
        self.visaobj.timeout = 2000 # set timeout back to 2s

        return data  
    
    def set_frequency(self,value):
        """Set frequency in Hz (according to manual)"""
        
        self.visaobj.timeout = 6000 # set timeout to 60s 
        
        word = "FREQ {}".format(str(value))
        data = self.visaobj.write(word)
        # data = self.visaobj.query(word)
        print('Frequency set at %s Hz'%value)
        # self.visaobj.timeout = 2000 # set timeout back to 2s


    def set_amplitude(self,channel,value):
        """Set Amplitude in V for selected channel output"""
        
        self.visaobj.timeout = 10000 # set timeout to 60s for measurement
        word = "SOUR{}:VOLT {}".format(str(channel),str(value))
        
        data = self.visaobj.write(word)
        
        self.visaobj.timeout = 2000 # set timeout back to 2s
        print('Amplitude of channel %s set to %s Vpp'%(channel,value))
        return data  
    
    
    def set_offset(self,channel, value):
        """ Set Offset in V for selected channel output"""
        
        self.visaobj.timeout = 10000 # set timeout to 60s for measurement
        word = "SOUR{}:VOLT:OFFS {}".format(str(channel),str(value))
        data = self.visaobj.write(word)
        self.visaobj.timeout = 2000 # set timeout back to 2s
        print('Offset of channel %s set to %s Vpp'%(channel,value))
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

    resourceStr = 'TCPIP0::169.254.187.139::inst0::INSTR'
    
    fg = RigolDG4162(resourceStr)
    # fg.is_enable()    
    # fg.enable()    
    # fg.is_enable()    
    # fg.set_frequency(50)
    
    channel = 2
    
    for i in range(-2, 0):
        
        fg.set_offset(channel,i)
        # fg.set_amplitude(channel,abs(i))
        time.sleep(2)  
    
    # fg.disable()