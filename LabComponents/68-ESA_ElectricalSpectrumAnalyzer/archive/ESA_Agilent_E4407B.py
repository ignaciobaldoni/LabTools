'''
Created on 23. nov. 2016

@author: arnek
'''
import visa
import numpy as np
import os
import saveDictToHdf5 as saveHDF5
import time

class ESA_Agilent_E4407B():
    def __init__(self):
        
        self.tool_settings = dict()
        self.traceList = list()
        self.traceData = dict()

    def openConnectionESA(self):
        ####################################################################################
        #                                     Parameter list
        ####################################################################################
        
        resourceManager = visa.ResourceManager()
        deviceList = resourceManager.list_resources()
        
        print(deviceList)
        #instrumentConnectionString = deviceList[5];
        instrumentConnectionString =  'GPIB0::18::INSTR';
        
        ####################################################################################
        #                     Connect to device 
        ####################################################################################
        
            # connect to device
        instrumentManager = resourceManager.open_resource(instrumentConnectionString)
        # instrumentManager.timeout = 1000;
        
        return instrumentManager
    
    def restartMeasurementAndReadOut(self):
        # connect 
        instrumentManager = self.openConnectionESA()
        # make restart
        instrumentManager.write(':SENSe:AVERage:COUNt 100')
        AverageCount = instrumentManager.query_ascii_values(':SENSe:AVERage:COUNt?')[0]
        print(''.join(['AverageCount: ',str(AverageCount)]))
        
        instrumentManager.write(':SENSe:AVERage:CLEar')
        instrumentManager.write(':INIT:IMM')
        instrumentManager.write('*OPC')
        time.sleep(1)
        
        # check whether measurement is finished 
        finishedOperation = 0;
        while not finishedOperation:
            resp = instrumentManager.query_ascii_values('*ESR?')
            finishedOperation = resp[0]
            print(finishedOperation)
            time.sleep(3)
        # read out dataA
        return self._readEsa(instrumentManager)
        
        
    def readESA(self):
        instrumentManager = self.openConnectionESA()
        return self._readEsa(instrumentManager)
    
    def _readEsa(self,instrumentManager):
        readOutTraceNumber = 1
            # collect device informations
        deviceIdentifyInfo = instrumentManager.query('*IDN?')
            ################################################################################
            # Log information
        print(''.join(['Device identifier: ' , deviceIdentifyInfo]))
            ################################################################################
            
        
        ####################################################################################
        #                                 read out dataA
        ####################################################################################
        #
        #     :WAVeform:POINts[?] <# points>
        ####################################################################################
        
        # calibrate x-Axes
        # get different parameters
        
            # SPAN
        SPAN = instrumentManager.query_ascii_values('FREQuency:SPAN?')[0]
        print(''.join(['SPAN (Hz): ',str(SPAN)]))
            # points
        POINTS = instrumentManager.query_ascii_values('SWEep:POINts?')[0] 
        print(''.join(['POINTS (1): ',str(POINTS)]))
            # start freq 
        StartFreq = instrumentManager.query_ascii_values('FREQuency:STARt?')[0]
        print(''.join(['StartFreq (Hz): ',str(StartFreq)]))
            # stop freq
        StopFreq = instrumentManager.query_ascii_values('FREQuency:STOP?')[0]
        print(''.join(['StopFreq (Hz): ',str(StopFreq)]))
        
        AverageCount = instrumentManager.query_ascii_values(':SENSe:AVERage:COUNt?')[0]
        print(''.join(['AverageCount: ',str(AverageCount)]))
        
        freqAxis = StartFreq + np.array(range(int(POINTS)))*(SPAN/POINTS)
        
        
            # set read out channel 
        traceString = ''.join(["TRACe" , str(readOutTraceNumber)])
            # set read out format
        dataA = np.array(instrumentManager.query_ascii_values(''.join([':TRACe:DATA? ',traceString])))  
        
            # RBW
        RBW = instrumentManager.query_ascii_values('BANDwidth:RESolution?')[0]
        VBW = instrumentManager.query_ascii_values(':BANDwidth:VIDeo?')[0]
        print(''.join(['RBW (Hz): ',str(RBW)]))
        
        instrumentManager.close()
        
        self.traceData = {
        'frequency_axis_Hz' : freqAxis,
        'dataA' : dataA
        }
        
        # save settings
        self.tool_settings['deviceIdentifyInfo'] = deviceIdentifyInfo
        self.tool_settings['SPAN_Hz'] = SPAN
        self.tool_settings['frequency_Start_Hz'] = StartFreq
        self.tool_settings['frequency_Stop_Hz'] = StopFreq
        self.tool_settings['resolution_bandwith_Hz'] = RBW
        self.tool_settings['video_bandwith_Hz'] = VBW
        self.tool_settings['AverageCount'] = AverageCount
        
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