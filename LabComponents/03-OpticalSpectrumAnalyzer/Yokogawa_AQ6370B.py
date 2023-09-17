# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 15:10:48 2021

@author: Administrator
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt

class Yokogawa_AQ6370B:
    '''
    A class for controlling the Yokogawa_AQ6370B OSA
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

    def read(self, mode):
        '''
        Takes a measurement using current instrument measurement settings.
        
        Parameters:
        -----------
        mode : string
            The instrument mode you wish to take a measurement in. 
            Possible modes include, but no limited to:
                
                SAN : Signal analyzer 
        
        Returns:
        ----------
        data : str
            The measured data.
        '''
        self.visaobj.timeout = 60000 # set timeout to 60s for measurement
        data = self.visaobj.query(':READ:{}?'.format(mode))
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
        
    def readCurrentMeasurementQuery(self):
        '''
        Reads out current measurement configuration
        
        Parameters:
        -----------
                
        Returns:
        ----------
        data : string
            information on current measurement configuration
        
        '''
        self.visaobj.timeout = 4000
        # queryStr = 'open'
        Message = "open anonymous\r\n"
        # Frame=chr(0x80)+chr(0x00)+chr(len(Message)>>8 & 0xFF)+ chr(len(Message) & 0xFF)+ Message.encode()
        Frame = bytes([0x80,0x00,14,len(Message)>>8 & 0xFF,len(Message) & 0xFF])+ Message.encode()
        data = self.visaobj.write_raw(Frame)
        print('open answer: '+ str(data)) 
        
        data = self.visaobj.read()
        print('read answer: '+ str(data)) 
        
        queryStr = ''
        data = self.visaobj.write(queryStr)
        print('open answer: '+ str(data)) 
        
        data = self.visaobj.read()
        print('read answer: '+ str(data)) 
        data = self.visaobj.write('')
        print('open answer: '+ str(data)) 
        
        queryStr = 'open "bla"'
        data = self.visaobj.query(queryStr)
        print('Current measurement configuration set to: '+ data) 
        data = self.visaobj.query(queryStr)
        print('Current measurement configuration set to: '+ data) 
        self.visaobj.timeout = 4000 # set timeout back to 2s
        
        return data
        
if __name__ == '__main__':
    resourceStr = 'TCPIP0::169.254.202.228::10001::SOCKET'
    #'USB0::0x0957::0x0D0B::US51160137::INSTR'
    osa = Yokogawa_AQ6370B(resourceStr)
    print('test')
    osa.readCurrentMeasurementQuery()
    print('test2')
    # pxa.restartMeasurement()
    # data = pxa.readCurrentTraceData()
    # freqs = data['frequencies_Hz']
    # psd = data['powerSpectralDensity_dBm']
    # rbw = data['resolutionBandwidth_Hz']
    
    # fig, ax = plt.subplots()
    # ax.plot(freqs*1.e-6, psd)
    
    # ax.set(xlabel='frequency [MHz]', ylabel='PSD [dBm]' + '(RBW='+str(rbw*1.e-3)+'kHz)')
    # ax.grid()
    
    # plt.show()
#    pxa.setToSingleMeasurement(True)
#    rawData = pxa.setMode('SA')
#    pxa.setMode('PNOISE')
#    pxa.readCurrentMeasurementQuery()
#    pxa.setMode('SA')
#    pxa.readCurrentMeasurementQuery()
#    rawData = pxa.read('SAN')
    # osa.disconnect();