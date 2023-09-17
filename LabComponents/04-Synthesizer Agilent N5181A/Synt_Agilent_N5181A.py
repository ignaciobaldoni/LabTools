# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 12:01:37 2021

@author: Administrator
"""

import logging
logger = logging.getLogger(__name__)

import pyvisa as visa
import time

class Synt_Agilent_N5181A:
    '''
    A class for controlling the Agilent N-5181A Synthesizer
    '''
    
    
    def __init__(self, resource = None):
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
        self.connect(resource) 

    def findDeviceResourceStr(self):
        
        deviceIDNstrArray = [
                'Agilent Technologies, N5181A, MY50142764, A.01.80'
            ]

        rm = visa.ResourceManager()

        deviceList = rm.list_resources_info()  
        # 10.0.2.191
        # TCPIP[board]::host address::port::SOCKET
        
        for deviceStr in deviceList:
            logger.debug(deviceStr)
            
            if deviceStr.startswith('TCPIP'):
                try:
                    instrumentManager = rm.open_resource(deviceStr)
                    query = '*IDN?'
                    data = instrumentManager.query(query)
                    data = data.strip()
                    logger.debug(data)
                    if data in deviceIDNstrArray:
                        instrumentManager.close()
                        logger.debug('selected resource string: ' + deviceStr)
                        return deviceStr
                except visa.VisaIOError as e:
                    logger.error(e)
        return None
    
    def connect(self, resource = None):
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
        
        if resource == None:
            resource = self.findDeviceResourceStr()
        
        rm = visa.ResourceManager()
        
        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
          self.visaobj = rm.open_resource(resource)
          self.visaobj.timeout = 2000
          queryStr = '*IDN?'
          data = self.visaobj.query(queryStr)
          logger.debug('selected device string: '+ data.strip())
        except visa.VisaIOError as e:
          logger.error(e)
          
    def enable(self):
        """ Enables the output of the signal. """
        self.visaobj.write(":OUTPUT ON;")
        logger.debug('switch synth output on')

    def disable(self):
        """ Disables the output of the signal. """
        self.visaobj.write(":OUTPUT OFF;")
        logger.debug('switch synth output off')

    def read_frequency(self):
        '''
        Current frequency
        '''
        self.visaobj.timeout = 60000 # set timeout to 60s for measurement
        data = self.visaobj.query(':FREQ?')
        self.visaobj.timeout = 2000 # set timeout back to 2s
        logger.debug('synth frequency is: ' + data)
        data = float(data.strip())*1e-6
        return data  
    
    def read_amplitude(self):
        '''
        Current frequency
        '''
        self.visaobj.timeout = 60000 # set timeout to 60s for measurement
        data = self.visaobj.query(':POW?')
        self.visaobj.timeout = 2000 # set timeout back to 2s
        logger.debug('synth amplitude is: ' + data)
        return data  
    
    def set_frequency(self,value_MHz):
        '''
        Set frequency in MHz
        '''
        self.visaobj.timeout = 6000 # set timeout to 60s for measurement
        word = "FREQuency:FIXed {} MHz".format(str(value_MHz))
        data = self.visaobj.write(word)
        logger.debug('synth frequency set to: ' + str(value_MHz) + 'MHz')
        return data  
    
    def set_amplitude(self,value_dBm):
        '''
        Set Amplitude in dBm 
        '''
        self.visaobj.timeout = 10000 # set timeout to 60s for measurement
        word = "POWer:LEVel {} dBM".format(str(value_dBm))
        data = self.visaobj.write(word)
        
        self.visaobj.timeout = 2000 # set timeout back to 2s

        logger.debug('synth amplitude set to: ' + str(value_dBm) + 'dBm')

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
        logger.debug('synth disconnected')
        
    
        
if __name__ == '__main__':
    resourceStr = 'TCPIP0::A-N5181A-42764::inst0::INSTR'
    
    resourceStr = None
    synt = Synt_Agilent_N5181A(resourceStr)
    # print('test')
    time.sleep(1)
    
    # Test of sweeping
    for i in range(0,3):
        # In MHz
        synt.set_frequency(170+i)
    
        # # In dBm
        # synt.set_amplitude(1-i)
        time.sleep(2)
        
    synt.disconnect()

