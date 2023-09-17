# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 12:51:40 2021

@author: Administrator
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt

import logging

logger = logging.getLogger(__name__)


class HP89410A:
    '''
    A class for controlling the Agilent HP89410A Vector Signal Analyzer 
    using VISA commands. 
    '''

    # %% class initialization and device connection functions
    def __init__(self, resource=None):
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
        self.connect(resource)

    def findDeviceResourceStr(self, deviceIDNstr: str):
        rm = visa.ResourceManager()

        deviceList = rm.list_resources_info()

        for deviceStr in deviceList:
            print(deviceStr)

            if deviceStr.startswith('GPIB'):
                visaobj = rm.open_resource(deviceStr)
                query = '*IDN?;*WAI'

                try:
                    data = visaobj.query(query)
                    data = data.strip()
                    logger.debug(data)
                    if data == deviceIDNstr:
                        visaobj.close()
                        logger.debug('\nselected resource string: ' + deviceStr)
                        return deviceStr
                except visa.VisaIOError as exp:
                    logger.exception(exp)

    def connect(self, resource=None):
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

        idnStr = r'HEWLETT-PACKARD,89410A,3346A00496,A.02.06'

        rm = visa.ResourceManager()

        if resource == None:
            resource = self.findDeviceResourceStr(idnStr)

        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
            self.visaobj = rm.open_resource(resource)
            self.visaobj.timeout = 60000
        except visa.VisaIOError as exp:
            logger.exception(exp)
            raise exp

    def disconnect(self):
        '''
        Device goes to local control and resource manager is disconnected

        Returns
        -------
        None.

        '''
        self.visaobj.control_ren(6)  # sends GTL (Go To Local) command
        self.visaobj.close()

    def is_connected(self):
        if self.visaobj is not None:
            query = '*IDN?;*WAI'
            query_response = self.visaobj.query(query)
            query_response = query_response.strip()
            logger.debug('*IDN?: ' + query_response)
            return True

        return False

    def readDeviceOption(self):
        '''
        Reads out current measurement configuration

        Returns
        -------
        data : string
            information on current measurement configuration.

        '''

        queryStr = '*OPT?'
        data = self.queryCmd(queryStr)
        print('Current measurement configuration set to: ' + data)

        return data

    # %% pyVISA SCPI wrapper functions
    def writeCmd(self, cmd):
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

    def queryCmd(self, cmd):
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

    # %% Display

    # %%% Measurement Data Button

    def readTraceMeasurementType(self, traceNumber: int = 1):

        queryStr = 'CALCulate{}:FEED?'.format(str(traceNumber))
        traceDataType = self.queryCmd(queryStr)

        traceDataType = traceDataType.strip()
        traceDataType = traceDataType.strip('"')

        if traceDataType == 'XFR:POW 1':
            traceDataType = 'power spectrum'
        elif traceDataType == 'XFR:POW:PSD 1':
            traceDataType = 'PSD'
        elif traceDataType == 'XTIM:VOLT 1':
            traceDataType = 'amplitude'
        elif traceDataType == 'XFR:POW:RAT 2,1':
            traceDataType = 'frequency response'
        elif traceDataType == 'XFR:POW:COH:2,1':
            traceDataType = 'coherence'
        elif traceDataType == 'XFR:POW:CROS 2,1':
            traceDataType = 'cross spectrum'
        elif traceDataType == 'XTIM:VOLT:CORR 1':
            traceDataType = 'auto correlation'
        elif traceDataType == 'XTIM:VOLT:CORR:CROS 2,1':
            traceDataType = 'cross correlation'
        else:
            traceDataType = 'unknown'

        return traceDataType

    def setTraceMeasurementType(self, traceNumber: int = 1, traceDataType: str = 'Spectrum1'):
        '''
        set string in double qoutes "" !!!

        Parameters
        ----------
        traceNumber : int, optional
            The default is 1.
        traceDataType : str, optional
        
            In Vector mode:
                spectrum:               XFR:POW 1
                PSD:                    XFR:POW:PSD 1
                main time:              XTIM:VOLT 1
                gate time:              XTIM:VOLT:GATE 1
                freq response:          XFR:POW:RAT 2,1
                coherence:              XFR:POW:COH:2,1
                cross spectrum:         XFR:POW:CROS 2,1
                auto correlation:       XTIM:VOLT:CORR 1
                cross correlation:      XTIM:VOLT:CORR:CROS 2,1

        Returns
        -------
        None.

        '''

        cmdStr = "CALCulate{}:FEED '{}'".format(str(traceNumber), traceDataType)
        self.writeCmd(cmdStr)

    # %%% Data Format Button
    def readTraceFormat(self, traceNumber: int = 1):
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
            MLIN|MLOG|PHASe|UPH|REAL|IMAG|GDELay|COMP|CONS|IEYE|QEYE|TEYE
        '''

        queryStr = ':CALCulate{}:FORMat?'.format(str(traceNumber))
        traceFormat = self.queryCmd(queryStr)

        return traceFormat

    def setTraceFormat(self, traceNumber: int = 1, traceFormat: str = 'MLOG'):
        '''
        set the y-axes trace format of the selected trace
            
        CALCulate[1|2|3|4]:FORMat <param>
        
        Parameters
        ----------
        traceNumber : int, optional
            The default is 1.
        traceFormat : str, optional
            current y-axis format 
            MLIN|MLOG|PHASe|UPH|REAL|IMAG|GDELay|COMP|CONS|IEYE|QEYE|TEYE

        Returns
        -------
        None.

        '''
        cmdStr = ':CALCulate{}:FORMat {}'.format(str(traceNumber), traceFormat)
        self.writeCmd(cmdStr)

    def readTraceSpacing(self, traceNumber: int = 1):
        queryStr = 'DISPlay:WINDow{}:TRACe:X:SCALe:SPACing?'.format(str(traceNumber))
        traceFormat = self.queryCmd(queryStr).strip()

        return traceFormat

    def setTraceSpacing(self, traceNumber: int = 1, spacing: str = 'LIN'):
        '''
        set displayed spacing

        Parameters
        ----------
        traceNumber : int, optional
            DESCRIPTION. The default is 1.
        spacing : str, optional
            LOG or LIN
            The default is 'LIN'.

        Returns
        -------
        None.

        '''
        cmdStr = 'DISPlay:WINDow{}:TRACe:X:SCALe:SPACing {}'.format(str(traceNumber), spacing)
        self.writeCmd(cmdStr)

    # %%% RefLvl/Scale

    def readXAxesUnit(self, traceNumber: int = 1):

        queryStr = 'TRACe:X:UNIT? Trace{}'.format(str(traceNumber))
        xAxesUnit = self.queryCmd(queryStr)

        xAxesUnit = xAxesUnit.strip()
        xAxesUnit = xAxesUnit.strip('"')
        xAxesUnit = xAxesUnit.replace('/', '_per_')

        return xAxesUnit

    def readYAxesUnit(self, traceNumber: int = 1):

        queryStr = 'CALC{}:UNIT:ANGLe?'.format(str(traceNumber))
        yAxesUnit = self.queryCmd(queryStr).strip()

        if not yAxesUnit:
            queryStr = 'CALC{}:UNIT:AM?'.format(str(traceNumber))
            yAxesUnit = self.queryCmd(queryStr).strip()

        if not yAxesUnit:
            queryStr = 'CALC{}:UNIT:FREQuency?'.format(str(traceNumber))
            yAxesUnit = self.queryCmd(queryStr).strip()

        if not yAxesUnit:
            queryStr = 'CALC{}:UNIT:POWer?'.format(str(traceNumber))
            yAxesUnit = self.queryCmd(queryStr).strip()

        if not yAxesUnit:
            queryStr = 'CALC{}:UNIT:TIME?'.format(str(traceNumber))
            yAxesUnit = self.queryCmd(queryStr).strip()

        yAxesUnit = yAxesUnit.strip()
        yAxesUnit = yAxesUnit.strip('"')
        yAxesUnit = yAxesUnit.replace('/', '_per_')

        return yAxesUnit

    def setYAxesUnit(self, traceNumber: int = 1, unitStr: str = ':POW Vrms2'):
        writeCmdStr = 'CALC{}:UNIT:{}'.format(str(traceNumber), unitStr)
        self.writeCmd(writeCmdStr)

    def readUnits(self, traceNumber: int = 1):

        unitDict = {}
        unitDict['xUnit'] = self.readXAxesUnit(traceNumber)
        unitDict['yUnit'] = self.readYAxesUnit(traceNumber)

        if unitDict['xUnit'] == 's':
            unitDict['xField'] = 'time'
        elif unitDict['xUnit'] == 'Hz':
            unitDict['xField'] = 'frequency'

        unitDict['yField'] = self.readTraceMeasurementType(traceNumber)

        return unitDict

    # %% Measurement

    # %%% Freq Button functions

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

    def setCenterFreq(self, value):
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

    def setStartFreq(self, startFreq):
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

    def setStopFreq(self, stopFreq):
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

    def setSpanFreq(self, span):
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

    # %%% ResBW/Window Button functions

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

    def setResolutionBandwidth(self, rbw):
        '''
        sets the current resolution bandwidth

        Parameters
        ----------
        rbw : float
            rbw in Hz.

        '''

        cmdStr = 'SENS:BAND:RES {}'.format(str(rbw))
        self.writeCmd(cmdStr)

    def readNumberOfPoints(self):
        '''
        reads the number of measured points
        
        Parameters:
        -----------
                
        Returns:
        ----------
        numPoints : int
            number of aquired points
        
        '''
        # queryStr = 'CALC:DATA:HEAD:POIN?'
        queryStr = 'SENSe:SWEep1:POINts?'
        data = self.visaobj.query(queryStr)
        data = int(data.strip())
        return data

    # %%% Instrument Mode Button functions
    def readInstrumentMode(self):
        '''
        reads out the current device mode

        INSTrument[:SELect]?

        Returns
        -------
        data : string
            abbreviation of current device mode.
            SCALar|DEMod|ADEMod|DDEMod|VECTor|VDEMod|WCDMa            
            
        '''
        queryStr = 'INST:SEL?'
        data = self.queryCmd(queryStr)
        data = data.strip()
        print('Current mode set to: ' + data)
        return data

    def setInstrumentMode(self, mode):
        '''
        set the current device mode
        
        cmd: :INSTrument[:SELect] mode


        Parameters
        ----------
        mode : string
                 SCALar|DEMod|ADEMod|DDEMod|VECTor|VDEMod|WCDMa 

        Returns
        -------
        None.

        '''

        cmdStr = ':INSTrument:SELect ' + mode
        self.writeCmd(cmdStr)

    # %%% Sweep Button
    def setSingleMeasurementIsON(self, singleMeasurementIsON):
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
        cmdStr = 'INIT:IMM'
        self.writeCmd(cmdStr)

    # %% Readout

    # TODO: delete part, when readXaxes is tested and working
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
        numPoints = self.readNumberOfPoints()

        freqs = np.linspace(startFreq, stopFreq, numPoints)

        # TODO: TRAC:X[:DATA]?

        return freqs

    def readTraceData(self, traceNumber: int = 1):

        # get supporting information: RBW, units
        data = {}
        data['resolutionBandwidth_Hz'] = self.readResolutionBandwidth()

        unitDict = self.readUnits(traceNumber)
        data['unitDict'] = unitDict

        # get x-Axes data
        xLabel = 'traceData/xAxes'
        # data[xLabel] = self.readXAxesTrace(traceNumber)  
        data[xLabel] = self.readFrequencies()

        # get y-Axes data        
        yLabel = 'traceData/yAxes'
        data[yLabel] = self.readYAxesTrace(traceNumber)

        # # see manual (agilent89410a_gpibreference.pdf) page 447
        # data[xLabel] = data[xLabel][0:len(data[yLabel])]        

        return data

    def readXAxesTrace(self, traceNumber: int = 1):

        # set cmd such that x axes is returned in ascii
        cmdStr = 'FORMat:DATA ASCii'
        self.writeCmd(cmdStr)

        queryStr = 'TRAC:X:DATA? TRACe{}'.format(str(traceNumber))
        data = self.queryCmd(queryStr)
        data = data.strip()
        data = data.split(',')
        data = np.array(data)
        data = data.astype(float)
        return data

    def readYAxesTrace(self, traceNumber=1):
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

        # TRACe[:DATA]
        queryStr = 'CALC{}:DATA?'.format(str(traceNumber))

        data = self.visaobj.query(queryStr)
        data = data.strip()
        data = data.split(',')
        data = np.array(data)
        data = data.astype(float)
        return data

    # %% comfort function

    def plotTrace(self, traceNumber=1, commentText=None):

        data = self.readTraceData(traceNumber)

        # read information
        unitDict = data['unitDict']
        rbw = data['resolutionBandwidth_Hz']

        xAxes = data['traceData/xAxes']
        yAxes = data['traceData/yAxes']

        fig, axes = plt.subplots(1, 2)  # ,figsize=(16,8))
        ax = axes[0]
        ax.plot(xAxes, yAxes)
        ax.grid()

        spacing = self.readTraceSpacing(traceNumber)
        if spacing == 'LOG':
            ax.set_xscale('log')

        xLabel = unitDict['xField'] + ' [' + unitDict['xUnit'] + ']'
        ax.set_xlabel(xLabel)
        yLabel = unitDict['yField'] + ' [' + unitDict['yUnit'] + ']'
        ax.set_ylabel(yLabel)

        ax = axes[1]
        ax.axis('off')
        textstr = 'RBW: ' + str(rbw) + ' Hz'
        if commentText != None:
            textstr = textstr + '\n\nComment:\n' + commentText
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
                verticalalignment='top', bbox=props)

        plt.tight_layout()
        plt.show()


# TODO: set averaging functions for VSA mode
# TODO: write averaging functions for SA mode

# %% main

if __name__ == '__main__':
    resourceStr = 'GPIB1::1::INSTR'

    # 'USB0::0x0957::0x0D0B::US51160137::INSTR'
    vxa = HP89410A()

    # data = vxa.plotTrace(1)
    # data = vxa.queryCmd("MMEM:DATA? 'INT:AKSTATE.sta';*WAI")
    # data = vxa.queryCmd("MMEM:NAME `plot`")
    data = vxa.queryCmd("MMEM:NAME?")
    # vxa.writeCmd("MMEMory:LOAD:STATe 1, 'INT:RIN.sta';*WAI")
    # data = vxa.queryCmd('CALCulate1:FEED?')
    print(data)
    # data = pxa.plotAdeModSmartSpectrumTrace(2)

    # print(data)
    # data = pxa.readPhaseNoiseTrace([1,2])
    # print(data)

    # freqs = data['traceFreqAxes_1_Hz']
    # psd = data['traceData_1_dBcPerHz']

    # fig, ax = plt.subplots()
    # ax.plot(freqs, spectrum)
    # # ax.set_xscale('log')
    # plt.show()

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
    vxa.disconnect();
