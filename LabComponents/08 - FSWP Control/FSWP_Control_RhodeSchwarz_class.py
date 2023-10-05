# -*- coding: utf-8 -*-
"""
Created on Wed May 31 17:08:39 2023

@author: ibaldoni
"""

import pyvisa as visa
import time
import numpy as np

class RhodeSchwarz_FSWP:
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
          print(self.visaobj.query('*IDN?'))
          
        except visa.VisaIOError as e:
          print(e.args)
          raise SystemExit(1)
          
          
    def PNoise_Status(self,traceNumber=1):      
        '''
        Sets the instrument mode
        
        Parameters:
        -----------
        traceNumber : int
            numberof trace to be read out
                
        Returns:
        ----------
        data : ?
            trace data
        '''
        
        self.visaobj.timeout = 6000
        queryStr = 'STATus:QUEStionable:PNOise:CONDition?'
        # print(queryStr)
        
        data = self.visaobj.query(queryStr)
        self.visaobj.timeout = 2000 # set timeout back to 2s
        if data=='0\n': print('Channel unused but found')        
        # return data
        
    
    def PhaseNoiseTrace(self, traceNumber=1):
        '''

        '''
        import pandas as pd
        
        self.visaobj.timeout = 6000
        queryStr = 'TRAC? TRACE'+str(traceNumber)
        
        data = self.visaobj.query(queryStr)
        self.visaobj.timeout = 2000 # set timeout back to 2s
        
        data_list = [float(x) for x in data.split(',')]
        
        # Separate even and odd index elements
        even_numbers = data_list[::2]
        odd_numbers = data_list[1::2]
        
        df = pd.DataFrame({'Frequency': even_numbers, 'dBc_Hz': odd_numbers})
        
        # print(df)
        
        return df
    
    
    def SpectrumTrace(self, traceNumber=1):
        '''

        '''
        import pandas as pd
        
        self.visaobj.timeout = 6000
        queryStr = 'TRAC? TRACE'+str(traceNumber)
        
        data = self.visaobj.query(queryStr)
        # print(data)
        self.visaobj.timeout = 2000 # set timeout back to 2s
                
        data_list = [float(x) for x in data.split(',')]        
        
        return data_list

        

        
        # df = pd.DataFrame({'Frequency': even_numbers, 'PSD': odd_numbers})
        
        # print(df)
        
        # return df
        
    
    def centerFrequency(self, center=500e6):
        
        self.visaobj.timeout = 6000
        command = f'FREQ:CENT {center}Hz'
        self.visaobj.write(command)

        
    def startFrequency(self, start=500e6):
        command = f'FREQ:STAR {start}Hz'
        self.visaobj.write(command)

        
    def stopFrequency(self, stop=500e6):
        command = f'FREQ:STOP {stop}Hz'
        self.visaobj.write(command)
    
    def queryStopFrequency(self):
        Stop = self.visaobj.query('FREQ:STOP?').strip()
        print('Stop frequency:\t\t', Stop,'Hz')
        return float(Stop)

    def queryCenterFrequency(self):
        Center = self.visaobj.query('FREQ:CENT?').strip()
        print('Center frequency:\t',Center,'Hz')
        return float(Center)

    def queryStartFrequency(self):
        Start = self.visaobj.query('FREQ:STAR?').strip()
        print('Start frequency:\t', Start, 'Hz')
        return float(Start)
        
        
    def setResolutionBandwidth(self, bandwidth=3):
        
        self.visaobj.timeout = 6000
        command = f'SENSE:BAND:RES {bandwidth}Hz'
        self.visaobj.write(command)

        
        self.visaobj.timeout = 2000 # set timeout back to 2s
        
        
    def queryResolutionBandwidth(self):
        
        self.visaobj.timeout = 6000
        command = f'SENSE:BAND:RES?'
        resBW = float(self.visaobj.query(command))
        print(f'Res. bandwidth:\t\t {resBW*1E-6:.2f} MHz')
        
        self.visaobj.timeout = 2000 # set timeout back to 2s
        
        return resBW
    
        
        
    
    def switchSpectrumTrace(self, mode = 'Spectrum'):
        '''

        '''
        import pandas as pd
        
        self.visaobj.timeout = 6000
        queryStr=f"INST:SEL {mode}"
        
        data = self.visaobj.write(queryStr)
        self.visaobj.timeout = 2000 # set timeout back to 2s
        
        
    def windowsAvailable(self ):
        '''

        '''
        import pandas as pd
        
        self.visaobj.timeout = 6000
        queryStr = "INST:LIST?"
        
        data = self.visaobj.query(queryStr)
        self.visaobj.timeout = 2000 # set timeout back to 2s
        
        print(data)
        
    
    def ContinuousMeasurement(self,value):
        self.visaobj.timeout = 6000
        command = f'INIT:CONT {value}'
        self.visaobj.write(command)
        
        self.visaobj.timeout = 2000 # set timeout back to 2s
        print(f'Continuous measurement is {value}')
        
    

    
    