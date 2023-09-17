# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 12:51:40 2021

@author: ibaldoni
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt

from cycler import cycler


class KeysightN9000B:
    '''
    A class for controlling the Keysight N9000BA CXA Signal Analyzer 
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
        print('CXA setMode call with: '+ mode)
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
    
    def setSpan(self,value):
        '''
        reads the current resolution bandwidth
        
        Parameters:
        -----------
                
        Returns:
        ----------
        RBW : float
            current RBW in Hz
        
        '''
        queryStr = 'SENS:FREQ:SPAN {}'.format(str(value))
        data = self.visaobj.write(queryStr)
        return data
    
    def setCenterFrequency(self,value):
        '''
        reads the current resolution bandwidth
        
        Parameters:
        -----------
                
        Returns:
        ----------
        RBW : float
            current RBW in Hz
        
        '''
        queryStr = 'SENS:FREQ:RF:CENT {}'.format(str(value))
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
    
    def setLogPlot(self):
        
        queryStr = 'MEAS:'
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
        data = data.astype(float)
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
        try:
            data['CarrierPower_dBm'] = self.readCarrierFrequency()
        except:
            print('No single carrier found')
        
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
        

# %% phase noise mode functions (Written by ARK, edited by IB)

    def setToPNoiseLogPlotMode(self):
        '''
        set to log plot measurement in phase noise mode
        Returns
        -------
        None.
        '''
        cmdString = ':INITiate:LPLot'
        self.writeCmd(cmdString)        

# %%% analyzer setup console
    
    def readPnoiseRBW(self):
        '''
        reads out the resolution bandwidth in pnoise mode
        Returns
        -------
        carrierFreq : float
            rbw.
        '''
        queryStr = ':SENSe:MONitor:BANDwidth:RESolution?'
        carrierFreq = self.queryCmd(queryStr)  
        carrierFreq = float(carrierFreq.strip())  
        
        return carrierFreq
        
    def setPnoiseRBW(self,rbw_Hz:float):
        '''
        set the resolution bandwidth in pnoise mode
        Parameters
        ----------
        rbw_Hz : float
            rbw.
        Returns
        -------
        None.
        '''
        cmdStr = ':SENSe:MONitor:BANDwidth:RESolution {}'.format(str(rbw_Hz))
        self.writeCmd(cmdStr)
        
    def readCarrierFrequency(self):
        '''
        reads out current carrier frequency
        Returns
        -------
        carrierFreq : float
            carrier frequency in Hz
        '''
        queryStr = ':SENSe:FREQuency:CARRier?'
        carrierFreq = self.queryCmd(queryStr)  
        carrierFreq = float(carrierFreq.strip())  
        
        return carrierFreq
    
    def readCarrierPower(self):
        '''
        reads out current carrier frequency
        Returns
        -------
        carrierFreq : float
            carrier frequency in Hz
        '''
        queryStr = ':SENSe:FREQuency:CARRier?'
        carrierFreq = self.queryCmd(queryStr)  
        carrierFreq = float(carrierFreq.strip())  
        
        return carrierFreq

    def setCarrierFrequency(self,carrierFreq):
        '''
        set carrier frequency in phase noise mode
        Parameters
        ----------
        freq : float 
            Carrier frequency in Hz
        Returns
        -------
        None.
        '''
        cmdStr = ':SENSe:FREQuency:CARRier {}'.format(str(carrierFreq))
        self.writeCmd(cmdStr)

    def readStartOffsetFrequency(self):
        '''
        reads the start offset frequency for phase noise measurements
        Returns
        -------
        startOffsetFreq : float
            start offset frequency in Hz
        '''
        queryStr = ':SENSe:LPLot:FREQuency:OFFSet:STARt?'
        startOffsetFreq = self.queryCmd(queryStr)  
        startOffsetFreq = float(startOffsetFreq.strip())  
        
        return startOffsetFreq
        
    def setStartOffsetFrequency(self,startOffsetFreq_Hz):
        '''
        set start offset frequency of the phase noise measurement
        Parameters
        ----------
        startOffsetFreq_Hz : float
            start offset frequency
        Returns
        -------
        None.
        '''
        cmdStr = ':SENSe:LPLot:FREQuency:OFFSet:STARt {}'.format(str(startOffsetFreq_Hz))
        self.writeCmd(cmdStr)

    def readStopOffsetFrequency(self):
        '''
        reads the stop offset frequency for phase noise measurements
        Returns
        -------
        stopOffsetFreq : float
            stop offset frequency in Hz
        '''
        queryStr = ':SENSe:LPLot:FREQuency:OFFSet:STOP?'
        stopOffsetFreq = self.queryCmd(queryStr)  
        stopOffsetFreq = float(stopOffsetFreq.strip())  
        
        return stopOffsetFreq
        
    def setStopOffsetFrequency(self,stopOffsetFreq_Hz):
        '''
        set stop offset frequency of the phase noise measurement
        Parameters
        ----------
        stopOffsetFreq_Hz : float
            stop offset frequency
        Returns
        -------
        None.
        '''
        cmdStr = ':SENSe:LPLot:FREQuency:OFFSet:STOP {}'.format(str(stopOffsetFreq_Hz))
        self.writeCmd(cmdStr)

    def autoTuneCarrier(self):
        '''
        tunes to strongest carrier in the current window
        Returns
        -------
        None.
        '''
        
        cmdStr = ':SENSe:FREQuency:CARRier:SEARch'
        self.writeCmd(cmdStr)     

        
    
        
    def readPhaseNoiseTrace(self,traceNumber = [1]):
        # :READ:LPLot[n]?
        
        # data dictionary
        phaseNoiseData = {}
        
        # read base information
        queryStr = ':FETCh:LPLot1?'
        data = self.queryCmd(queryStr)
        
        # print(data)
        
        data = data.strip()
        data = data.split(',')
        data = np.array(data)
        data = data.astype(float)
        
        # print(data)
        
        if len(data)>2:
            
            phaseNoiseData['carrierPower_dBm'] = data[0]
            phaseNoiseData['carrierFrequency_Hz'] = data[1]
            phaseNoiseData['totalPhaseNoiseRMS_Deg'] = data[2]
            phaseNoiseData['totalPhaseNoiseRMS_Rad'] = data[3]
            phaseNoiseData['residualFrequencyModulation_Hz'] = data[4]
            phaseNoiseData['spotNoiseAtStartOffsetFreq_dBcPerHz'] = data[5]
            phaseNoiseData['spotNoiseAtStopOffsetFreq_dBcPerHz'] = data[6]
            
            
        # read frequency information
        
        # numberof points per trace
        queryStr = ':FETCh:LPLot2?'
        numberOfPoints = self.queryCmd(queryStr)
        
        numberOfPoints = numberOfPoints.strip()
        numberOfPoints = numberOfPoints.split(',')
        numberOfPoints = np.array(numberOfPoints)
        numberOfPoints = numberOfPoints.astype(float)
        

                
        # read trace data information
        for traceNum in traceNumber:
            # construct frequency axis
                        
            queryStr = ':FETCh:LPLot{}?'.format(traceNum+2)
            data = self.queryCmd(queryStr)
            
            data = data.strip()
            data = data.split(',')
            data = np.array(data)
            data = data.astype(float)
            
            traceDataIndex = np.arange(1,2*numberOfPoints[traceNum-1],2,dtype=int)
            traceLabel = 'traceData_{}_dBcPerHz'.format(traceNum)
            phaseNoiseData[traceLabel] = data[traceDataIndex]
            
            freqDataIndex = np.arange(0,2*numberOfPoints[traceNum-1],2,dtype=int)
            traceLabel = 'traceFreqAxes_{}_Hz'.format(traceNum)
            phaseNoiseData[traceLabel] = data[freqDataIndex]
        # print(list(phaseNoiseData))
        # print(len(phaseNoiseData))
        return phaseNoiseData
    
    

# %%% comfort function

    def plotPhaseNoiseTrace(self,traceNumber=[1],commentText = None,
                            default_colors=None):
        

        carrierFreq = self.readCarrierFrequency()
        rbw = self.readPnoiseRBW()
        
        if default_colors != None:
            plt.rcParams["axes.prop_cycle"] = plt.cycler("color",default_colors)

        
        fig, ax = plt.subplots(1,1)
        
        for i in traceNumber:
            data = self.readPhaseNoiseTrace([i])
        
            spectrum = data['traceData_{}_dBcPerHz'.format(i)] 
            freqs = data['traceFreqAxes_{}_Hz'.format(i)] 
            
            ax.plot(freqs, spectrum)
            
        ax.grid()
        ax.set_xlabel('Frequency [Hz]')
        ax.set_ylabel('Phasenoise [dBc/Hz]')
        ax.set_xscale('log')
        ax.set_ylim([-150,-50])
        
        
        plt.tight_layout()
        
        if len(traceNumber)>1:
            print('The table is showing the results from the average and not the raw phase noise')

        return freqs, spectrum, fig
    
    def queryCmd(self,cmd):
        '''
        wrapper function for sending queries to the pxa
        Parameters
        ----------
        cmd : string
            SCPI query string
        Returns
        -------
        data : string/diverse
            PXA answer
        '''
        cmd = cmd + ';*WAI'
        data = self.visaobj.query(cmd)
        return data   
    
    def savePNGimage(self,fileName_path):
        # queryStr = f':MMEMory:STORe:SCReen{fileName_path}?'
        queryStr = ':MMEMory:STORe:SCReen:BLOCked {}'.format(fileName_path)
        print(queryStr)
        # data = self.queryCmd(queryStr)
        data = self.queryCmd(queryStr)
        return data


        
if __name__ == '__main__':
    
    resourceStr = 'USB0::0x2A8D::0x1A0B::MY60250816::INSTR'
    # resourceStr = 'TCPIP0::10.0.2.225::5025::SOCKET'

    

    cxa = KeysightN9000B(resourceStr)
    
    cxa.connect(resourceStr)
    
    # cxa.savePNGimage('Prueba.jpg')
    
    
    Res_BW      = 1000
    # start_freq  = 9.00e6
    # stop_freq   = 11e6
    # span        = 1e6
    center_freq = 80e6
    
    PhaseNoise = False
    Spectrum_Analyzer = True
 
    if Spectrum_Analyzer:
        cxa.setMode('SA')
        cxa.restartMeasurement()
        # cxa.setStartFreq(start_freq)
        # cxa.setStopFreq(stop_freq)
        cxa.setResolutionBandwidth(Res_BW)
        # cxa.setSpan(span)
        cxa.setCenterFrequency(center_freq)
        data = cxa.readCurrentTraceData()
        freqs = data['frequencies_Hz']
        psd = data['powerSpectralDensity_dBm']
        rbw = data['resolutionBandwidth_Hz']
    
        fig, ax = plt.subplots()
        ax.plot(freqs*1.e-6, psd)
        
        ax.set(xlabel='frequency [MHz]', ylabel='PSD [dBm]' + '(RBW = '+str(rbw*1.e-3)+'kHz)')
        ax.grid()
        plt.show()
    
    if PhaseNoise:
        
        
        cxa.setAutoTune()
        cxa.setToSingleMeasurement(True)
        cxa.setMode('PNOISE')
        cxa.setCenterFrequency(center_freq)
    
    
    # cxa.savePNGimage('Prueba.png')
    

    
    cxa.disconnect();