# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 12:51:40 2021

@author: Administrator
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt

class AgilentN9030A:
    '''
    A class for controlling the Agilent N9030A PXA Signal Analyzer 
    using VISA commands. 
    '''
    
# %% class initialization and device connection functions    
    def __init__(self):
        '''
        Creates a new instrument instance and attempts connection. 

        Parameters
        ----------
        resource : str
            A string containing the VISA address of the device..
        label : str, optional
            The name of the device that will be used to label data uniquely.

        Returns
        -------
        None.

        '''
        self.connect() 

    def findDeviceResourceStr(self):
        
        deviceIDNstrArray = [
                'Agilent Technologies,N9030A,US51160137,A.14.04',
                'Keysight Technologies,N9010B,MY55460791,A.18.12',
                'Keysight Technologies,N9000B,MY56210328,A.19.05',
                'Agilent Technologies,N9000A,MY54230646,A.25.05'
            ]
        
        rm = visa.ResourceManager()

        deviceList = rm.list_resources_info()  
        # 10.0.2.191
        # TCPIP[board]::host address::port::SOCKET
        
        for deviceStr in deviceList:
            print(deviceStr)
            
            if deviceStr.startswith('TCPIP') or deviceStr.startswith('USB'):
                try:
                    instrumentManager = rm.open_resource(deviceStr)
                    query = '*IDN?'
                    data = instrumentManager.query(query)
                    data = data.strip()
                    print(data)
                    if data in deviceIDNstrArray:
                        instrumentManager.close()
                        print('\nselected resource string: ' + deviceStr)
                        return deviceStr
                except visa.VisaIOError as e:
                    print(e.args)
        return None
    
    def connect(self):
        '''
        Connect to the instrument. 

        Parameters
        ----------
        resource : str
            A string containing the VISA address of the device.
        label : str, optional
            The name of the device that will be used to label data uniquely. 
            The default is None.

        Raises
        ------
        SystemExit
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        
        conStr = self.findDeviceResourceStr()
        
        # conStr = 'TCPIP0::A-N9030A-60137.local::inst0::INSTR'
        # conStr =  'USB0::0x2A8D::0x1A0B::MY60250816::INSTR'
        # conStr =  'TCPIP0::A-N9000A-30646.local::hislip0::INSTR'
        # conStr =  'TCPIP0::K-N9000B-50816.local::hislip0::INSTR'
        # conStr =  'TCPIP0::A-N9030A-60137.local::inst0::INSTR'
        rm = visa.ResourceManager()
        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
          self.visaobj = rm.open_resource(conStr)
          self.visaobj.timeout = 60000
        except visa.VisaIOError as e:
          print(e.args)
          raise SystemExit(1)

    def disconnect(self):
        '''
        Device goes to local control and resource manager is disconnected

        Returns
        -------
        None.

        '''
        self.visaobj.control_ren(6) # sends GTL (Go To Local) command
        self.visaobj.close()


# %% pyVISA SCPI wrapper functions
    def writeCmd(self,cmd):
        '''
        wrapper function for sending commands to the PXA

        Parameters
        ----------
        cmd : string
            SCPI command string

        Returns
        -------
        None.

        '''
        cmd = cmd + ';*WAI'
        self.visaobj.write(cmd)

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
    
    

# %% general purpose device functions
    
        
    def readMode(self):
        '''
        reads out the current device mode

        Returns
        -------
        data : string
            abbreviation of current device mode.

        '''
        queryStr = 'INST:SEL?'
        data = self.queryCmd(queryStr)
        data = data.strip()
        print('Current mode set to: ' + data)
        return data

    def setMode(self, mode):
        '''
        set the current device mode
        
        cmd: :INSTrument[:SELect] mode


        Parameters
        ----------
        mode : string
                 SA | RTSA | SEQAN | EMI | BASIC | WCDMA |
                 EDGEGSM | WIMAXOFDMA | VSA | PNOISE | NFIGure | ADEMOD | BTooth |
                 TDSCDMA | CDMA2K | CDMA1XEV | LTE | LTETDD | LTEAFDD | LTEATDD | MSR
                 | DVB | DTMB | DCTV | ISDBT | CMMB | WLAN | CWLAN | CWIMAXOFDM |
                 WIMAXFIXED | IDEN | RLC | SCPILC | VSA89601

        Returns
        -------
        None.

        '''
        
        cmdStr = ':INSTrument:SELect '+mode
        self.writeCmd(cmdStr)
          

    
    def readConfiguration(self):
        '''
        Reads out current measurement configuration

        Returns
        -------
        data : string
            information on current measurement configuration.

        '''
        
        queryStr = 'CONF?'
        data = self.queryCmd(queryStr)
        print('Current measurement configuration set to: '+ data) 
        
        return data

        
# %% Spectrum analyzer mode

# %%% Analyzer setup console

# %%%% Freq channel functions
    
    def readCenterFreq(self):
        '''
        reads out center frequency 
        
        Parameters:
        -----------
                
        Returns:
        ----------
        centerFreq : float
            center frequency in Hz
        
        '''
        queryStr = 'SENS:FREQ:CENTER?'
        data = self.queryCmd(queryStr)
        data = float(data.strip())
        return data   
    
    def setCenterFreq(self,value):
        '''
        sets center frequency 
        
        Parameters:
        -----------
        value : float
            center frequency
                
        Returns:
        ----------
        None
        
        '''
        cmdStr = 'SENS:FREQ:CENTER {}'.format(str(value))
        self.writeCmd(cmdStr)
        

    def readStartFreq(self):
        '''
        reads out start frequency

        Returns
        -------
        data : float
            start frequency in Hz.

        '''
        
        queryStr = 'SENS:FREQ:START?'
        data = self.queryCmd(queryStr)
        data = float(data.strip())
        return data

    def setStartFreq(self,startFreq):
        '''
        sets start frequency

        Parameters
        ----------
        startFreq : float
            start frequency in Hz

        Returns
        -------
        None.

        '''
        
        cmdStr = 'SENS:FREQ:START {}'.format(str(startFreq))
        self.writeCmd(cmdStr)
        
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
        data = self.queryCmd(queryStr)
        data = float(data.strip())
        return data


    def setStopFreq(self,stopFreq):
        '''
        reads out stop frequency
        
        Parameters:
        -----------
        stopFreq : float
            stop frequency in Hz
                
        Returns:
        ----------
        None
        
        '''
        cmdStr = 'SENS:FREQ:STOP {}'.format(str(stopFreq))
        self.writeCmd(cmdStr)
        
    def autoTuneFreq(self):
        '''
        centers analyzer window to the strongest peak

        Returns
        -------
        None.

        '''
        
        cmdStr = 'SENS:FREQ:TUNE:IMMediate'
        self.writeCmd(cmdStr)
        


# %%%% Span x scale functions

    def readSpanFreq(self):
        '''
        reads out frequency span
        
        Parameters:
        -----------
                
        Returns:
        ----------
        span : float
            span frequency in Hz
        
        '''
        queryStr = 'SENS:FREQ:SPAN?'
        data = self.queryCmd(queryStr)
        data = float(data.strip())
        return data    

    def setSpanFreq(self,span):
        '''
        sets frequency span

        Parameters
        ----------
        span : float
            new span frequency in Hz

        Returns
        -------
        None.

        '''
        
        cmdStr = 'SENS:FREQ:SPAN {}'.format(str(span))
        self.writeCmd(cmdStr)   


# %%%% BW resolutions bandwidth functions 
    
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
        data = self.queryCmd(queryStr)
        data = float(data.strip())
        return data    
    
    def setResolutionBandwidth(self,rbw):
        '''
        sets the current resolution bandwidth

        Parameters
        ----------
        rbw : float
            rbw in Hz.

        '''
        
        cmdStr = 'SENS:BAND:RES {}'.format(str(rbw))
        self.writeCmd(cmdStr)
                     




# %%% Measurement Console 
    def setSingleMeasurementIsON(self,singleMeasurementIsON):
        '''
        Sets the instrument into single or continous measurement

        Parameters
        ----------
        singleMeasurementIsON : bool
            True - device in single measurement mode
            False - device in continous measurement mode 

        Returns
        -------
        None.

        '''
 
        if singleMeasurementIsON:
            cmdStr = 'INIT:CONT OFF'
            self.writeCmd(cmdStr)
        else:
            cmdStr = 'INIT:CONT ON'
            self.writeCmd(cmdStr)
            
    def restartMeasurement(self):
        '''
        restarts current measurement
        
        Parameters:
        -----------
                
        Returns:
        ----------
        None
        
        '''
        cmdStr = 'INIT:REST'
        self.writeCmd(cmdStr)
        queryStr = '*OPC?'
        self.queryCmd(queryStr)


# %%% readout functions

    def read(self, mode = 'SAN'):
        '''
        Takes a measurement using current instrument measurement settings.

        Parameters
        ----------
        mode : string, optional
            The instrument mode you wish to take a measurement in. 
            Possible modes include, but no limited to:
                
                SAN : Signal analyzer 
                
            The default is 'SAN'.

        Returns
        -------
        data : str
            The measured data.

        '''
        
        queryStr = ':READ:{}?'.format(mode)
        data = self.queryCmd(queryStr)
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


    def readSpectrumTrace(self,traceNumber=1):
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
        
        queryStr = 'TRACE:DATA? TRACE' + str(traceNumber)
        data = self.visaobj.query(queryStr)
        data = data.strip()
        data = data.split(',')
        data = np.array(data)
        data = data.astype(float)
        return data
    
    
    def readSpectrumTraceData(self,traceNumber=1):
        '''
        returns data for spectrum mode
        returns frequency, power, and rbw data in one combined directory

        Parameters
        ----------
        traceNumber : int, optional
            trace number to be read out 
            The default is 1.

        Returns
        -------
        data : dict
            trace data
                resolutionBandwidth_Hz
                powerSpectralDensity_dBm
                frequencies_Hz

        '''
               
        data = {}
        data['resolutionBandwidth_Hz'] = self.readResolutionBandwidth()
        data['powerSpectralDensity_dBm'] = self.readSpectrumTrace(traceNumber)
        data['frequencies_Hz'] = self.readFrequencies()
        
        return data
    
# %%% comfort function

    def plotSpectrumTraceData(self,traceNumber=1):
            
        data = self.readSpectrumTraceData(traceNumber)
    
        rbw = data['resolutionBandwidth_Hz'] 
        spectrum = data['powerSpectralDensity_dBm'] 
        freqs = data['frequencies_Hz'] 
        
        fig, ax = plt.subplots()
        ax.plot(freqs, spectrum)
        ax.grid()
        ax.set_xlabel('Frequency [Hz]')
        ax.set_ylabel('Power [dBm, rbw {}Hz]'.format(str(rbw)))
        # ax.set_xscale('log')
        plt.show()

    def plotSpectrumTraceDataComment(self,traceNumber=1,commentText = None):
            
        data = self.readSpectrumTraceData(traceNumber)
    
        rbw = data['resolutionBandwidth_Hz'] 
        spectrum = data['powerSpectralDensity_dBm'] 
        freqs = data['frequencies_Hz'] 
        
        fig, axes = plt.subplots(1,2,figsize=(16,8))
        ax = axes[0]
        ax.plot(freqs, spectrum)
        ax.grid()
        
        ax.set_xlabel('Frequency [Hz]')
        ax.set_ylabel('Power [dBm, rbw {}Hz]'.format(str(rbw)))
        # ax.set_xscale('log')
        
        ax = axes[1]
        ax.axis('off')
        textstr = 'RBW: '  + str(rbw) + ' Hz'
        if commentText != None:
            textstr = textstr + '\n\nComment:\n' + commentText
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        plt.show()
    
###############################################################################
### phase noise 

# %% phase noise mode functions

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
      
    def readCarrierTrackIsOn(self):
        '''
        returns a bool determining whether carrierTrack is on 

        Returns
        -------
        carrierTrackOn : bool
            carrier track is on when return value is True

        '''
        queryStr = ':SENSe:FREQuency:CARRier:TRACk:STATe?'
        carrierTrackIsOn = self.queryCmd(queryStr)  
        carrierTrackIsOn = bool(int(carrierTrackIsOn.strip()))  
        
        return carrierTrackIsOn
    
    def setCarrierTrackStatus(self,carrierTrackIsOn = True):
        '''
        switches the carrier track function

        Parameters
        ----------
        carrierTrackIsOn : bool, optional
            set to True to turn on carrier tracking
            set to False to turn off carrier tracking
            The default is True.

        Returns
        -------
        None.

        '''
        if carrierTrackIsOn:
            cmdStr = ':SENSe:FREQuency:CARRier:Track 1'
        else:
            cmdStr = ':SENSe:FREQuency:CARRier:Track 0'
            
        self.writeCmd(cmdStr)
        
    
# %%% Measurement console functions

    def readPNoiseAverageCount(self):
        '''
        reads out the the total count of averages taken in  phase noise m
        measurement mode

        Returns
        -------
        pNoiseAverageNumber : int
            total count of averages

        '''
        queryStr = ':SENSe:LPLot:AVERage:COUNt?'
        pNoiseAverageNumber = self.queryCmd(queryStr)  
        pNoiseAverageNumber = int(pNoiseAverageNumber)  
        
        return pNoiseAverageNumber
    
    def setPNoiseAverageCount(self,pNoiseAverageCount:int):
        '''
        set measurement average count in phasenoise mode

        Parameters
        ----------
        pNoiseAverageCount : int
            measurement average count in phasenoise mode

        Returns
        -------
        None.

        '''
        cmdStr = ':SENSe:LPLot:AVERage:COUNt {}'.format(pNoiseAverageCount)
        self.writeCmd(cmdStr)

    def readIsPNoiseAverageIsOn(self):
        '''
        returns True (False) if averaging in PNOISE mode is on (off) 

        Returns
        -------
        pNoiseAverageIsOn : bool
            status of averaging in phase noise mode 
            True if on
            False if off

        '''
        queryStr = ':SENSe:LPLot:AVERage:STATe?'
        pNoiseAverageIsOn = self.queryCmd(queryStr)  
        pNoiseAverageIsOn = bool(int(pNoiseAverageIsOn.strip()))   
        
        return pNoiseAverageIsOn
    
    def setIsPNoiseAverageIsOn(self,pNoiseAverageIsOn:bool = True):
        '''
        switches averaging in PNOISE mode on (off) if True (False) 

        Parameters
        ----------
        pNoiseAverageIsOn : bool, optional
            switch on averaging in PNOISE mode
            averaging is on if True
            averaging is off if False
            default is Ture

        Returns
        -------
        None.

        '''
        if pNoiseAverageIsOn:
            cmdStr = ':SENSe:LPLot:AVERage:STATe 1'
        else:
            cmdStr = ':SENSe:LPLot:AVERage:STATe 0'
        
        self.writeCmd(cmdStr)

    
# %%% readOut functions
    
    # def calcLogScaleFrequencyPoints(self,startFreq,stopFreq,numberOfPoints):
    #     '''
    #     calculate the disttribution of frequenies on a log scale

    #     Parameters
    #     ----------
    #     startFreq : float
    #         start offset frequency
    #     stopFreq : float
    #         stop offset frequency
    #     numberOfPoints : int
    #         number of measurement points

    #     Returns
    #     -------
    #     freqs : [float]
    #         list of logarithmic duistribuited frequencys

    #     '''
    #     points = np.arange(numberOfPoints)
        
    #     freqs = 10**(
    #             (
    #                 np.log10(startFreq)-np.log10(stopFreq)
    #             )/(
    #                 numberOfPoints-1
    #                 )*points 
    #             + np.log10(startFreq)
    #         )
                    
    #     return freqs
     
    def readPhaseNoiseTrace(self,traceNumber = [1]):
        # :READ:LPLot[n]?
        
        # data dictionary
        phaseNoiseData = {}
        
        # read base information
        queryStr = ':FETCh:LPLot1?'
        data = self.queryCmd(queryStr)
        
        print(data)
        
        data = data.strip()
        data = data.split(',')
        data = np.array(data)
        data = data.astype(float)
        
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
        
        # startOffsetFreq = self.readStartOffsetFrequency()
        # stopOffsetFreq = self.readStopOffsetFrequency()
                
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
        
        return phaseNoiseData

# %%% comfort function

    def plotPhaseNoiseTrace(self,traceNumber=1,commentText = None):
            
        data = self.readPhaseNoiseTrace([traceNumber])
    
        carrierFreq = self.readCarrierFrequency()
        rbw = self.readPnoiseRBW()
        
        spectrum = data['traceData_{}_dBcPerHz'.format(traceNumber)] 
        freqs = data['traceFreqAxes_{}_Hz'.format(traceNumber)] 
        
        fig, axes = plt.subplots(1,2,figsize=(16,8))
        ax = axes[0]
        
        ax.plot(freqs, spectrum)
        ax.grid()
        ax.set_xlabel('Frequency [Hz]')
        ax.set_ylabel('Phasenoise [dBc]')
        ax.set_xscale('log')
        
        
        ax = axes[1]
        ax.axis('off')
        textstr = 'Center Frequency: ' + str(carrierFreq) + ' Hz' + '\n'\
                    + 'RBW: '  + str(rbw) + ' Hz'
        if commentText != None:
            textstr = textstr + '\n\nComment:\n' + commentText
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        plt.show()

###############################################################################
### VXA mode 

# %% VXA mode functions    

    def setToVsaAnalogDemod(self):
        '''
        set to analog demod modulation measurement in VSA mode

        Returns
        -------
        None.

        '''
        cmdString = ':INITiate:ADEMod'
        self.writeCmd(cmdString)        

# %%% analyzer setup console
    def readADeModCenterFrequency(self):
        '''
        reads out current carrier frequency

        Returns
        -------
        centerFrequency : float
            carrier frequency in Hz

        '''
        queryStr = ':SENSe:FREQuency:CENTer?'
        centerFrequency = self.queryCmd(queryStr)  
        centerFrequency = float(centerFrequency.strip())  
        
        return centerFrequency

    def setADeModCenterFrequency(self,centerFrequency):
        '''
        set carrier frequency in phase noise mode

        Parameters
        ----------
        centerFrequency : float 
            Carrier frequency in Hz

        Returns
        -------
        None.

        '''
        cmdStr = ':SENSe:FREQuency:CENTer {}'.format(str(centerFrequency))
        self.writeCmd(cmdStr)
            
    def readADeModSignalTrackIsOn(self):
        '''
        returns a bool determining whether signal track is on 

        Returns
        -------
        aDeModSignalTrackIsOn : bool
            signal track is on when return value is True

        '''
        queryStr = ':SENSe:ADEMod:FREQuency:CENTer:TRACk?'
        aDeModSignalTrackIsOn = self.queryCmd(queryStr)  
        aDeModSignalTrackIsOn = bool(int(aDeModSignalTrackIsOn.strip()))  
        
        return aDeModSignalTrackIsOn
    
    def setADeModSignalTrackIsOn(self,aDeModSignalTrackIsOn:bool = True):
        '''
        switches the signal track function in VSA/VXA mode

        Parameters
        ----------
        aDeModSignalTrackIsOn : bool, optional
            set to True to turn on carrier tracking
            set to False to turn off carrier tracking 
            The default is True.

        Returns
        -------
        None.

        '''
        
        if aDeModSignalTrackIsOn:
            cmdStr = ':SENSe:ADEMod:FREQuency:CENTer:TRACk 1'
        else:
            cmdStr = ':SENSe:ADEMod:FREQuency:CENTer:TRACk 0'
            
        self.writeCmd(cmdStr)

    def readADeModResolutionBandwidth(self):
        '''
        reads out the resoultion bandwidth in VXA analog demodultion mode

        Returns
        -------
        aDeModResolutionBandwidth_Hz : float
            resolution bandwidth in Hz.

        '''
        queryStr = ':SENSe:ADEMod:BANDwidth:RESolution?'
        aDeModResolutionBandwidth_Hz = self.queryCmd(queryStr)  
        aDeModResolutionBandwidth_Hz = float(aDeModResolutionBandwidth_Hz.strip()) 
        
        return aDeModResolutionBandwidth_Hz

    def setADeModResolutionBandwidth(self,aDeModResolutionBandwidth_Hz:float):
        '''
        set the resolution bandwidth in VXA-analog demodulation mode

        Parameters
        ----------
        aDeModResolutionBandwidth_Hz : float
            bandwidth in Hz.

        Returns
        -------
        None.

        '''
        cmdStr = ':SENSe:ADEMod:BANDwidth:RESolution {}'.format(str(aDeModResolutionBandwidth_Hz))
        self.writeCmd(cmdStr)
       
    def readADEModTraceFormat(self,traceNumber : int = 1 ):
        '''
        read out y-axes trace format of selected trace

        

        Parameters
        ----------
        traceNumber : int, optional
            selected trace number 
            The default is 1'.

        Returns
        -------
        traceFormat : str
            current y-axis format 
            MLOG | MLINear | REAL | IMAGinary | VECTor | CONS | PHASe | 
            UPHase | IEYE | QEYE | TRELlis | GDELay | MLGLinear
        '''
        
        queryStr = ':DISPlay:ADEMod:TRACe{}:FORMat?'.format(str(traceNumber))
        traceFormat = self.queryCmd(queryStr)  
        
        return traceFormat
    
    def setADEModTraceFormat(self,traceNumber : int = 1, traceFormat : str = 'MLOG'):
        '''
        set the y-axes trace format of the selected trace

        Parameters
        ----------
        traceNumber : int, optional
            The default is 1.
        traceFormat : str, optional
            current y-axis format 
            MLOG | MLINear | REAL | IMAGinary | VECTor | CONS | PHASe | 
            UPHase | IEYE | QEYE | TRELlis | GDELay | MLGLinear
            The default is 'MLOG'.

        Returns
        -------
        None.

        '''
        cmdStr = ':DISPlay:ADEMod:TRACe{}:FORMat {}'.format(str(traceNumber),traceFormat)
        self.writeCmd(cmdStr)

    def readADEModTraceDataType(self,traceNumber : int = 1 ):
        '''
        reads out the data type of selected trace

        Parameters
        ----------
        traceNumber : int, optional
            The default is 1.

        Returns
        -------
        traceDataType : str
            description of data format

        '''
        queryStr = ':DISPlay:ADEMod:TRACe{}:FEED?'.format(str(traceNumber))
        traceDataType = self.queryCmd(queryStr)  
        
        traceDataType = traceDataType.strip()
        traceDataType = traceDataType.strip('"')
        
        return traceDataType    
    
    def setADEModTraceDataType(self,traceNumber : int = 1, traceDataType : str = 'Spectrum1' ):
        '''
        
        Parameters
        ----------
        traceNumber : int, optional
            The default is 1.
        traceDataType : str, optional
            No Data
            
            AnDemod Auto Correl1
            AnDemod CCDF1
            AnDemod CDF1
            AnDemod Gate Time1
            AnDemod Inst Main Time1
            AnDemod Inst Spec1
            AnDemod Main Time1
            AnDemod PDF1
            AnDemod PSD1
            AnDemod Spectrum1
            
            Auto Correl1
            CCDF1
            CDF1
            Correction1
            Gate Time1
            Inst Main Time1
            Inst Main Time1
            Inst Spec1
            Main Time1
            PDF1
            PSD1
            Raw Main Time1
            Spectrum1
            
            Acp Summary Trc1
            Acp Summary Trc2
            Acp Summary Trc3
            Acp Summary Trc4
            Obw Summary Trc1
            Obw Summary Trc2
            Obw Summary Trc3
            Obw Summary Trc4
            
            The default is 'Spectrum1'.

        Returns
        -------
        None.

        '''
        
        # set string in double qoutes "" !!!
        cmdStr = ':DISP:ADEM:TRAC{}:FEED "{}"'.format(str(traceNumber),traceDataType)
        # cmdStr = ':DISPlay:VECT:TRACe{}:FEED {}'.format(str(traceNumber),traceDataType)
        self.writeCmd(cmdStr)
        
        queryStr = '*OPC?'
        self.queryCmd(queryStr)
    
    def readADEModTraceDataNames(self,traceNumber : int = 1 ):
        '''
        read of trace data options

        Parameters
        ----------
        traceNumber : int, optional
            The default is 1.

        Returns
        -------
        traceDataTypeNames : str
            list of option strings

        '''
        queryStr = ':CALCulate:ADEMod:DATA{}:NAMes? '.format(str(traceNumber))
        traceDataTypeNames = self.queryCmd(queryStr)  
        
        return traceDataTypeNames    

    def readADEModYAxesUnit(self,traceNumber : int = 1):
        '''
        current y-axis unit: Peak|RMS|Power|mRMS

        Parameters
        ----------
        traceNumber : int, optional
            DESCRIPTION. The default is 1.

        Returns
        -------
        yAxesUnit : TYPE
            DESCRIPTION.

        '''
        queryStr = ':DISPlay:ADEMod:TRACe{}:Y:UNIT?'.format(str(traceNumber))
        yAxesUnit = self.queryCmd(queryStr)  
        
        yAxesUnit = yAxesUnit.strip()
        yAxesUnit = yAxesUnit.strip('"')
        yAxesUnit = yAxesUnit.replace('/','_per_')
        
        
        return yAxesUnit        
    
# %%% Measurement console functions  / measurement setup

# 
    def runAdeModAutoScale(self,traceNumber : int = 1):
        cmdStr = ':DISPlay:ADEMod:TRACe{}:Y:AUTO:ONCE'.format(traceNumber)
        self.writeCmd(cmdStr)     
        
    def readADeModType(self):
        '''
        returns the current demodulation type in VSA mode

        Returns
        -------
        deModulationType : str
            Current type. OPtions AM|FM|PM.

        '''
        queryStr = ':SENSe:ADEMod:MODulation?'
        deModulationType = self.queryCmd(queryStr)  
        deModulationType = deModulationType.strip()
        
        return deModulationType
    
    def setADeModType(self,deModulationType:str = 'FM'):
        '''
        set the analog demodulation type. AM|PM|FM

        Parameters
        ----------
        deModulationType : str, optional
            demodulation option.
            AM|PM|FM
            The default is 'FM'.

        Returns
        -------
        None.

        '''
        cmdStr = ':SENSe:ADEMod:MODulation {}'.format(deModulationType)
        self.writeCmd(cmdStr)        

# %%% readout functions

    def readAdeModSpectrumTrace(self,traceNumberList = [1]):
        
        # :CALCulate:<meas>:DATA[1] | 2 | ...4? [Y | X | XY[,OFF | ON | 0 | 1] 
        
        traceDataDict = {}
        
        rbw = self.readADeModResolutionBandwidth()
        carrierFreq = self.readADeModCenterFrequency()
        
        traceDataDict['rbw_Hz'] = rbw
        traceDataDict['carrierFrequency_Hz'] = carrierFreq
        
        for traceNumber in traceNumberList:
            
            
            # retrieve x-axes data
            queryStr = ':CALCulate:ADEMod:DATA{}? X,ON'.format(traceNumber)
            xData = self.queryCmd(queryStr)  
            xData = xData.strip()
            xData = xData.split(',')
            xData = np.array(xData)
            xData = xData.astype(float)
            traceLabel = 'traceData_{}_xAxes'.format(traceNumber)
            traceDataDict[traceLabel] = xData
        
            # retrieve y-axes data
            queryStr = ':CALCulate:ADEMod:DATA{}? Y,ON'.format(traceNumber)
            yAxesData = self.queryCmd(queryStr)  
            yAxesData = yAxesData.strip()
            yAxesData = yAxesData.split(',')
            yAxesData = np.array(yAxesData)
            yAxesData = yAxesData.astype(float)
            traceLabel = 'traceData_{}_yAxes'.format(traceNumber)
            traceDataDict[traceLabel] = yAxesData
        
        return traceDataDict

    def readAdeModSmartSpectrumTrace(self,traceNumberList = [1]):
        
        # :CALCulate:<meas>:DATA[1] | 2 | ...4? [Y | X | XY[,OFF | ON | 0 | 1] 
        
        traceDataDict = {}
        
        rbw = self.readADeModResolutionBandwidth()
        carrierFreq = self.readADeModCenterFrequency()
        
        traceDataDict['rbw_Hz'] = rbw
        traceDataDict['carrierFrequency_Hz'] = carrierFreq
        
        for traceNumber in traceNumberList:
            
            singleTraceDict = {}
            
            # read information
            unitDict = self.determineAdeModUnits(traceNumber)
            
            xUnit = unitDict['xUnit']
            xField = unitDict['xField']
            yUnit = unitDict['yUnit']
            yField = unitDict['yField']
            
            
            traceLabel = 'unitdict_{}'.format(traceNumber)
            traceDataDict[traceLabel] = unitDict
            
            # retrieve x-axes data
            queryStr = ':CALCulate:ADEMod:DATA{}? X,ON'.format(traceNumber)
            xData = self.queryCmd(queryStr)  
            xData = xData.strip()
            xData = xData.split(',')
            xData = np.array(xData)
            xData = xData.astype(float)
            # traceLabel = 'x_{}_{}'.format(xField,xUnit)
            # singleTraceDict[traceLabel] = xData
            
            traceLabel = 'traceData_{}_xAxes'.format(traceNumber)
            traceDataDict[traceLabel] = xData
        
            # retrieve y-axes data
            queryStr = ':CALCulate:ADEMod:DATA{}? Y,ON'.format(traceNumber)
            yAxesData = self.queryCmd(queryStr)  
            yAxesData = yAxesData.strip()
            yAxesData = yAxesData.split(',')
            yAxesData = np.array(yAxesData)
            yAxesData = yAxesData.astype(float)
            # traceLabel = 'y_{}_{}'.format(yField,yUnit)
            # singleTraceDict[traceLabel] = yAxesData
        
            traceLabel = 'traceData_{}'.format(yField)
            traceDataDict[traceLabel] = singleTraceDict
            
            traceLabel = 'traceData_{}_yAxes'.format(traceNumber)
            traceDataDict[traceLabel] = yAxesData
            
        return traceDataDict

# %%% comfort function
    
    def determineAdeModUnits(self, traceNumber : int = 1):
        
        # 
        traceDataType = self.readADEModTraceDataType(traceNumber)
        # traceFormat = self.readADEModTraceFormat(traceNumber)
        traceYUnit = self.readADEModYAxesUnit(traceNumber)

        # detetermine dataType class: i.e. Pre-Demod or DeMod
        if traceDataType.startswith('AnDemod'):
            adeModType = self.readADeModType()
            unitDict = self.determineDeModUnits(adeModType,traceDataType,traceYUnit)
        else:
            unitDict = self.determineNotDeModUnits(
                                traceDataType,
                                traceYUnit)
        
        
        # TODO: add statistical units
        
        return unitDict
    
    def determineNotDeModUnits(self,traceDataType,traceYUnit):
        
        unitDict = {}
        xUnit = ''
        xField = ''
        
        yUnit = traceYUnit
        yField = ''
        
        if traceDataType in ['Spectrum1']:
            xField = 'Frequency'
            yField = 'Carrier Power'
            xUnit = 'Hz'
                    
        elif traceDataType in ['Main Time1'] :
            xField = 'Time'
            yField = 'Carrier Amplitude'
            xUnit = 's'
        
        elif traceDataType in ['PSD1']:
            xField = 'Frequency'
            yField = 'Carrier PSD'
            xUnit = 'Hz'
                
        else: 
            print('traceDataType: "{}" unknown'.format(traceDataType))    
        
        unitDict['xUnit'] = xUnit
        unitDict['xField'] = xField
        unitDict['yUnit'] = yUnit
        unitDict['yField'] = yField
        
        return unitDict

    def determineDeModUnits(self,adeModType,traceDataType,traceYUnit):
        
        unitDict = {}
        xUnit = ''
        xField = ''
        
        yUnit = traceYUnit
        yField = ''
        
        if traceDataType in ['AnDemod Spectrum1']:
            xField = 'Frequency'
            yField = adeModType + ' Spectrum'
            xUnit = 'Hz'
        elif traceDataType in ['AnDemod PSD1']:
            xField = 'Frequency'
            yField = adeModType + ' PSD'
            xUnit = 'Hz'
        elif traceDataType in ['AnDemod Main Time1']:
            xField = 'Time'
            yField = adeModType + ' deviation'
            xUnit = 's'
                
        else: 
            print('traceDataType: "{}" unknown'.format(traceDataType))    
        
        unitDict['xUnit'] = xUnit
        unitDict['xField'] = xField
        unitDict['yUnit'] = yUnit
        unitDict['yField'] = yField
        
        return unitDict

    def plotAdeModSpectrumTrace(self,traceNumber=1):
            
        data = self.readAdeModSpectrumTrace([traceNumber])
    
        xAxes = data['traceData_{}_xAxes'.format(traceNumber)] 
        yAxes = data['traceData_{}_yAxes'.format(traceNumber)] 
        
        fig, ax = plt.subplots()
        ax.plot(xAxes, yAxes)
        ax.grid()
        ax.set_xlabel('x-axes')
        ax.set_ylabel('y-axes')
        # ax.set_xscale('log')
        plt.show()

    def plotAdeModSmartSpectrumTrace(self,
                                     traceNumber=1,
                                     commentText = None,
                                     showPlot = True,
                                     data = None):
            
        if data == None:
            data = self.readAdeModSpectrumTrace([traceNumber])
            
            # read information
            unitDict = self.determineAdeModUnits(traceNumber)
            rbw = self.readADeModResolutionBandwidth()
            carrierFreq = self.readADeModCenterFrequency()
        else:
            traceLabel = 'unitdict_{}'.format(traceNumber)
            unitDict = data[traceLabel]
            
            rbw = data['rbw_Hz']
            carrierFreq = data['carrierFrequency_Hz']
        
        xAxes = data['traceData_{}_xAxes'.format(traceNumber)] 
        yAxes = data['traceData_{}_yAxes'.format(traceNumber)] 
        
        fig, axes = plt.subplots(1,2,figsize=(16,8))
        ax = axes[0]
        ax.plot(xAxes, yAxes)
        ax.grid()
        
        
        xLabel = unitDict['xField'] + ' ['+ unitDict['xUnit'] + ']'
        ax.set_xlabel(xLabel)
        yLabel = unitDict['yField'] + ' ['+ unitDict['yUnit'] + ']'
        ax.set_ylabel(yLabel)
        

        
        ax = axes[1]
        ax.axis('off')
        textstr = 'Center Frequency: ' + str(carrierFreq) + ' Hz' + '\n'\
                    + 'RBW: '  + str(rbw) + ' Hz'
        if commentText != None:
            textstr = textstr + '\n\nComment:\n' + commentText
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        if showPlot:
            plt.show()
            
        return fig, axes

# TODO: set averaging functions for VSA mode
# TODO: write averaging functions for SA mode

# %% main

if __name__ == '__main__':
    resourceStr = 'TCPIP0::A-N9030A-60137.local::inst0::INSTR'
    
    #'USB0::0x0957::0x0D0B::US51160137::INSTR'
    pxa = AgilentN9030A()
    
    # data = pxa.readADEModYAxesUnit(2)
    # data = pxa.plotAdeModSmartSpectrumTrace(3)
        
    # print(data)
    data = pxa.readPhaseNoiseTrace([1,2])
    print(data)
    
    freqs = data['traceFreqAxes_1_Hz']
    psd = data['traceData_1_dBcPerHz']
    
    fig, ax = plt.subplots()
    ax.plot(freqs, psd)
    ax.set_xscale('log')
    plt.show()
    
    # pxa.setCarrierTrackStatus()
    # data = pxa.readIsCarrierTrackOn()
    # print(data)
    # pxa.setCarrierTrackStatus(False)
    # data = pxa.readIsCarrierTrackOn()
    # print(data)  
    
    # pxa.restartMeasurement()
    # pxa.setStartFreq(125e6)
    # pxa.setStopFreq(180e6)
    # pxa.setResolutionBandwidth(1e3)
    # data = pxa.readCurrentTraceData()
    # freqs = data['frequencies_Hz']
    # psd = data['powerSpectralDensity_dBm']
    # rbw = data['resolutionBandwidth_Hz']
    
    # fig, ax = plt.subplots()
    # ax.plot(freqs*1.e-6, psd)
    
    # ax.set(xlabel='frequency [MHz]', ylabel='PSD [dBm]' + '(RBW='+str(rbw*1.e-3)+'kHz)')
    # ax.grid()
    
    
    
    
    # plt.show()
    # pxa.setAutoTune()
#    pxa.setToSingleMeasurement(True)
#    rawData = pxa.setMode('SA')
#    pxa.setMode('PNOISE')
#    pxa.readCurrentMeasurementQuery()
#    pxa.setMode('SA')
#    pxa.readCurrentMeasurementQuery()
#    rawData = pxa.read('SAN')
    pxa.disconnect();