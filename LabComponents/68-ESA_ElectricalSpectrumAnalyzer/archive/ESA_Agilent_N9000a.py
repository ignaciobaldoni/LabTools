'''
Created on 19.08.2016

@author: Arne
'''
import visa
import numpy as np
import os
import saveDictToHdf5 as saveHDF5
import time

class ESA_Agilent_N9000a():
    def __init__(self):
        
        self.tool_settings = dict()
        self.traceList = list()
        self.traceData = dict()

    def openConnectionESA(self):
        ####################################################################################
        #                                     Parameter list
        ####################################################################################
        
        resourceManager = visa.ResourceManager()
        #deviceList = resourceManager.list_resources()
        #print(deviceList)
        
        #instrumentConnectionString = deviceList[5];
        instrumentConnectionString =  'GPIB0::18::INSTR';
        
        ####################################################################################
        #                     Connect to device 
        ####################################################################################
        
            # connect to device
        self.instrumentManager = resourceManager.open_resource(instrumentConnectionString)
        # instrumentManager.timeout = 1000;
        
        return self.instrumentManager

    def closeConnection(self):
        self.instrumentManager.close()
        
    def peakDetect(self,markerNum = 2):
        instrumentManager = self.instrumentManager
        cmdStr = 'CALC:MARK'+str(markerNum)+':MODE Pos'
        instrumentManager.write(cmdStr)
        cmdStr = ':CALCulate:MARKer'+str(markerNum)+':MAXimum'
        instrumentManager.write(cmdStr)
        cmdStr = ':CALCulate:MARKer'+str(markerNum)+':X?' # in hertz (display unit)
        xPos = instrumentManager.query_ascii_values(cmdStr)[0]
        #xPos = self.convertFreqs([xPos])[0]
        cmdStr = ':CALCulate:MARKer'+str(markerNum)+':Y?' # in dBm (display unit)
        yPos = instrumentManager.query_ascii_values(cmdStr)[0]
        return [xPos,yPos]    
        
    def _setESA(self,startFreq,stopFreq,RBW,points):
        instrumentManager = self.instrumentManager
        
        instrumentManager.write('SWEep:POINts ' + str(points)) 
            # start freq (Hz)
        instrumentManager.write('FREQuency:STARt ' + str(startFreq))
            # stop freq (Hz)
        instrumentManager.write('FREQuency:STOP ' + str(stopFreq))
            # RBW (Hz)
        instrumentManager.write('BANDwidth:RESolution '+str(RBW))
    
    def singleMeasurement(self):    
        instrumentManager = self.instrumentManager
        # make restart
        
        instrumentManager.write(':INITiate:CONTinuous Off')
        instrumentManager.write(':INIT:IMM')
        instrumentManager.write('*OPC')
        time.sleep(0.1)
        
        # check whether measurement is finished 
        finishedOperation = 0;
        while not finishedOperation:
            resp = instrumentManager.query_ascii_values('*ESR?')
            finishedOperation = resp[0]
            #print(finishedOperation)
            time.sleep(1)
            
    def restartMeasurementAndReadOut(self):
        # connect 
        instrumentManager = self.instrumentManager
        # make restart
        instrumentManager.write('BANDwidth:RESolution '+str(500000))
        instrumentManager.write('SWEep:POINts ' + str(100))
        instrumentManager.write(':SENSe:AVERage:COUNt 100')
        AverageCount = instrumentManager.query_ascii_values(':SENSe:AVERage:COUNt?')[0]
        #print(''.join(['AverageCount: ',str(AverageCount)]))
        
        instrumentManager.write(':SENSe:AVERage:CLEar')
        instrumentManager.write(':INIT:IMM')
        instrumentManager.write('*OPC')
        time.sleep(1)
        
        # check whether measurement is finished 
        finishedOperation = 0;
        while not finishedOperation:
            resp = instrumentManager.query_ascii_values('*ESR?')
            finishedOperation = resp[0]
            #print(finishedOperation)
            time.sleep(3)
        # read out dataA
        return self._readEsa()
        
        
    def readESA(self):
        instrumentManager = self.openConnectionESA()
        return self._readEsa()

    def convertFreqs(self,points = [-1]):
        
        instrumentManager = self.instrumentManager
        # calibrate x-Axes
        # get different parameters
        
            # SPAN
        SPAN = instrumentManager.query_ascii_values('FREQuency:SPAN?')[0]
        #print(''.join(['SPAN (Hz): ',str(SPAN)]))
            # points
        POINTS = instrumentManager.query_ascii_values('SWEep:POINts?')[0] 
        #print(''.join(['POINTS (1): ',str(POINTS)]))
            # start freq 
        StartFreq = instrumentManager.query_ascii_values('FREQuency:STARt?')[0]
        #print(''.join(['StartFreq (Hz): ',str(StartFreq)]))
            # stop freq
        StopFreq = instrumentManager.query_ascii_values('FREQuency:STOP?')[0]
        #print(''.join(['StopFreq (Hz): ',str(StopFreq)]))
        
        self.tool_settings['SPAN_Hz'] = SPAN
        self.tool_settings['frequency_Start_Hz'] = StartFreq
        self.tool_settings['frequency_Stop_Hz'] = StopFreq
    
        if points[0] == -1:
            points = range(int(POINTS))
        
        freqAxis = StartFreq + np.array(points)*(SPAN/POINTS)
        return freqAxis
    
    def _readEsa(self,readOutTraceNumber = 1):
            # collect device informations
        instrumentManager = self.instrumentManager
        deviceIdentifyInfo = instrumentManager.query('*IDN?')
        deviceOptionList = instrumentManager.query('*OPT?')  
            ################################################################################
            # Log information
        #print(''.join(['Device identifier: ' , deviceIdentifyInfo]))
            ################################################################################
            
        
        ####################################################################################
        #                                 read out dataA
        ####################################################################################
        #
        #     :WAVeform:POINts[?] <# points>
        ####################################################################################
        
        freqAxis = self.convertFreqs();
        
            # set read out channel 
        traceString = ''.join(["TRACe" , str(readOutTraceNumber)])
            # set read out format
        data = np.array(instrumentManager.query_ascii_values(''.join([':TRACe:DATA? ',traceString])))  
        
            # RBW
        RBW = instrumentManager.query_ascii_values('BANDwidth:RESolution?')[0]
        VBW = instrumentManager.query_ascii_values(':BANDwidth:VIDeo?')[0]
        #print(''.join(['RBW (Hz): ',str(RBW)]))
        
        self.traceData = {
        'frequency_axis_Hz' : freqAxis,
        'data' : data
        }
        
        # save settings
        self.tool_settings['deviceIdentifyInfo'] = deviceIdentifyInfo
        self.tool_settings['deviceOptionList'] = deviceOptionList
        self.tool_settings['resolution_bandwith_Hz'] = RBW
        self.tool_settings['video_bandwith_Hz'] = VBW
        
        
        return self.traceData
    
    ####################################################################################
    #                                save as HDF5
    ####################################################################################
    def saveDataAsHDF5(self, filename):
        
        rawDataDic = {'toolSettings': self.tool_settings, 'rawData':self.traceData}
        saveDic = {'ESA_Agilent_N9000a':rawDataDic}
        
        saveHDF5.save_dict_to_hdf5(saveDic, filename)
    
    ####################################################################################
    #                           deprecated save method
    ####################################################################################
    def saveESATrace(self,saveFolder,fileName,traceData):    
        try:
            os.stat(saveFolder)
        except:
            os.makedirs(saveFolder)  
        freqAxis = traceData['freqAxis']
        dataA = traceData['dataA']
        np.savetxt(''.join([saveFolder,'\\',fileName,'.csv']), np.c_[freqAxis,dataA], delimiter=",")
    
test1 = False
test2 = False

if test1:
    tool = ESA_Agilent_N9000a()
    tool.openConnectionESA()
    center = 1e9
    span = 10e6
    startFreq =  center-span/2
    stopFreq = center+span/2
    RBW = 10e3
    points = 3e3
    tool._setESA(startFreq, stopFreq, RBW, points)
    tool.closeConnection()
    
if test2:
    tool = ESA_Agilent_N9000a()
    tool.openConnectionESA()
    tool.singleMeasurement()
    data = tool.peakDetect()
    print(data)
    tool.closeConnection()
    