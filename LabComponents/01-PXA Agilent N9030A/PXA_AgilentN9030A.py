# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 12:51:40 2021

@author: ibaldoni
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt

class AgilentN9030A:
    '''
    A class for controlling the Agilent N9030A PXA Signal Analyzer 
    using VISA commands. 
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
    
    def setMode(self, mode):
        '''
        Sets the instrument mode
        
        Parameters:
        -----------
        mode : string
            The instrument mode you wish to take a measurement in. 
            Possible modes include, but no limited to:
                
                SA : Signal analyzer 
                PNOISE : phase noise measurement
                
        Returns:
        ----------
        
        '''
        print('PXA setMode call with: '+ mode)
        self.visaobj.timeout = 5000
        writeStr = 'INST:SEL '+ mode
        self.visaobj.write(writeStr)
        queryStr = 'INST:SEL?'
        data = self.visaobj.query(queryStr)
        print('Current mode set to: '+ data) 
        self.visaobj.timeout = 2000 # set timeout back to 2s
        
    

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
        self.visaobj.timeout = 60000
        queryStr = 'CONF?'
        data = self.visaobj.query(queryStr)
        print('Current measurement configuration set to: '+ data) 
        self.visaobj.timeout = 2000 # set timeout back to 2s
        
        return data

    def readStartFreq(self):
        '''
        reads out start frequency
        
        Parameters:
        -----------
                
        Returns:
        ----------
        startFreq : float
            start frequency in Hz
        
        '''
        queryStr = 'SENS:FREQ:START?'
        data = self.visaobj.query(queryStr)
        data = float(data.strip())
        return data

    def readStopFreq(self):
        '''
        reads out stop frequency
        
        Parameters:
        -----------
                
        Returns:
        ----------
        stopFreq : float
            stop frequency in Hz
        
        '''
        queryStr = 'SENS:FREQ:STOP?'
        data = self.visaobj.query(queryStr)
        data = float(data.strip())
        return data
    
    def setStopFreq(self,value):
        '''
        reads out stop frequency
        
        Parameters:
        -----------
                
        Returns:
        ----------
        stopFreq : float
            stop frequency in Hz
        
        '''
        queryStr = 'SENS:FREQ:STOP {}'.format(str(value))
        data = self.visaobj.write(queryStr)
        return data
    
    def setStartFreq(self,value):
        '''
        reads out start frequency
        
        Parameters:
        -----------
                
        Returns:
        ----------
        startFreq : float
            start frequency in Hz
        
        '''
        queryStr = 'SENS:FREQ:START {}'.format(str(value))
        data = self.visaobj.write(queryStr)
        return data
    
    def setAutoTune(self):
        '''
        reads out stop frequency
        
        Parameters:
        -----------
                
        Returns:
        ----------
        stopFreq : float
            stop frequency in Hz
        
        '''
        queryStr = 'SENS:FREQ:TUNE:IMMediate'
        
        data = self.visaobj.write(queryStr)
        return data

    def readNumberOfPOints(self):
        '''
        reads the number of measured points
        
        Parameters:
        -----------
                
        Returns:
        ----------
        numPoints : int
            number of aquired points
        
        '''
        queryStr = 'SENS:SWE:POIN?'
        data = self.visaobj.query(queryStr)
        data = int(data.strip())
        return data
 
    def readResolutionBandwidth(self):
        '''
        reads the current resolution bandwidth
        
        Parameters:
        -----------
                
        Returns:
        ----------
        RBW : float
            current RBW in Hz
        
        '''
        queryStr = 'SENS:BAND:RES?'
        data = self.visaobj.query(queryStr)
        data = float(data.strip())
        return data    
    
    def setResolutionBandwidth(self,value):
        '''
        reads the current resolution bandwidth
        
        Parameters:
        -----------
                
        Returns:
        ----------
        RBW : float
            current RBW in Hz
        
        '''
        queryStr = 'SENS:BAND:RES {}'.format(str(value))
        data = self.visaobj.write(queryStr)
        return data
                     
                     
    def readFrequencies(self):
        '''
        reads an array with the current frequencies
        
        Parameters:
        -----------
                
        Returns:
        ----------
        freqs : float[]
            array with the current frequencies
        
        '''
        startFreq = self.readStartFreq()
        stopFreq = self.readStopFreq()
        numPoints = self.readNumberOfPOints()
        
        freqs = np.linspace(startFreq,stopFreq,numPoints)
        
        return freqs

    def setToSingleMeasurement(self,bool):
        '''
        Sets the instrument into single or continous measurement
        
        Parameters:
        -----------
                
        Returns:
        ----------
        
        '''
        if bool:
            queryStr = 'INIT:CONT OFF'
            data = self.visaobj.write(queryStr)
        else:
            queryStr = 'INIT:CONT ON'
            self.visaobj.write(queryStr)
            
    def restartMeasurement(self):
        '''
        restarts current measurement
        
        Parameters:
        -----------
                
        Returns:
        ----------
        
        '''
        queryStr = 'INIT:REST'
        self.visaobj.write(queryStr)
        
    def querySpectrumTrace(self,traceNumber=1):
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
        
        self.visaobj.timeout = 60000
        queryStr = 'TRACE:DATA? TRACE' + str(traceNumber)
        data = self.visaobj.query(queryStr)
        self.visaobj.timeout = 2000 # set timeout back to 2s
        data = data.strip()
        data = data.split(',')
        data = np.array(data)
        data = data.astype(np.float)
        return data
    
    def readCurrentTraceData(self,traceNumber=1):
        '''
        returns frequency, power, and rbw data in one combined directory
        
        Parameters:
        -----------
        traceNumber : int
            numberof trace to be read out
                
        Returns:
        ----------
        data : dict
            trace data
        '''
        
        data = {}
        data['resolutionBandwidth_Hz'] = self.readResolutionBandwidth()
        data['powerSpectralDensity_dBm'] = self.querySpectrumTrace()
        data['frequencies_Hz'] = self.readFrequencies()
        
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
    resourceStr = 'USB0::0x0957::0x0D0B::US51160137::INSTR'
    resourceStr = 'TCPIP0::169.254.181.231::INSTR'
    
    #'USB0::0x0957::0x0D0B::US51160137::INSTR'
    pxa = AgilentN9030A(resourceStr)
    
    pxa.restartMeasurement()
    # pxa.setStartFreq(125e6)
    # pxa.setStopFreq(180e6)
    # pxa.setResolutionBandwidth(1e3)
    data = pxa.readCurrentTraceData()
    freqs = data['frequencies_Hz']
    psd = data['powerSpectralDensity_dBm']
    rbw = data['resolutionBandwidth_Hz']
    
    fig, ax = plt.subplots()
    ax.plot(freqs*1.e-6, psd)
    
    ax.set(xlabel='frequency [MHz]', ylabel='PSD [dBm]' + '(RBW='+str(rbw*1.e-3)+'kHz)')
    ax.grid()
    
    
    
    
    plt.show()
    # pxa.setAutoTune()
#    pxa.setToSingleMeasurement(True)
#    rawData = pxa.setMode('SA')
#    pxa.setMode('PNOISE')
#    pxa.readCurrentMeasurementQuery()
#    pxa.setMode('SA')
#    pxa.readCurrentMeasurementQuery()
#    rawData = pxa.read('SAN')
    pxa.disconnect();