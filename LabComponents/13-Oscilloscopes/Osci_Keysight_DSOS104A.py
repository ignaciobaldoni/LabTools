'''
Created on 19. aug. 2016

@author: qpitlab
'''
import struct
from time import sleep
import visa
import numpy as np
import time
import os


class Oszi_Keysight_DSOS104a():
    def __init__(self):
        
        self.tool_settings = dict()
        self.traceList = list()
        self.traceData = dict()
        self.channel_setting = dict()
        
    ####################################################################################        
    def openConnectionOszi(self):
        
        instrumentConnectionString =  'TCPIP0::WINDOWS-6TBN82B.local::hislip0::INSTR';
        resourceManager = visa.ResourceManager()
            # connect to device
        
        self.instrumentManager = resourceManager.open_resource(instrumentConnectionString)
            # collect device informations
        self.instrumentManager.timeout = 20000
        self.instrumentManager.write(':SYSTem:HEADer OFF')  
        
        return self.instrumentManager

    def closeConnetion(self):
        self.instrumentManager.close()
        
    ####################################################################################
    def updateToolSetting(self):
        instrumentManager = self.instrumentManager
        deviceIdentifyInfo = instrumentManager.query('*IDN?')
        deviceOptionList = instrumentManager.query('*OPT?')  
        acquireMode = instrumentManager.query(":ACQuire:MODE ?");
        averaging = instrumentManager.query(":ACQuire:AVERage ?"); 
        sampleCount =  instrumentManager.query_ascii_values(":ACQuire:POINts ?"); 
        samplingrate = instrumentManager.query_ascii_values(":ACQuire:SRATe ?"); 
        timebasePosition = instrumentManager.query_ascii_values(":TIMebase:POSition ?");    
        timeSpan = instrumentManager.query_ascii_values(":TIMebase:RANGe?");
        
        self.tool_settings['deviceIdentifyInfo'] = deviceIdentifyInfo
        self.tool_settings['deviceOptionList'] = deviceOptionList
        self.tool_settings['acquireMode'] = acquireMode
        self.tool_settings['averaging'] = averaging
        self.tool_settings['sampleCount'] = sampleCount
        self.tool_settings['samplingRate'] = samplingrate
        self.tool_settings['timebasePosition'] = timebasePosition
        self.tool_settings['timeSpan'] = timeSpan
        
    ####################################################################################
    def autoScaleScope(self):
        instrumentManager  = self.instrumentManager
        instrumentManager.write(':AUToscale:CHANnels DISPlayed') 
        instrumentManager.write(':AUToscale;*OPC?')
        instrumentManager.read()
        
    ####################################################################################
    def measureMinimum(self,ChannelNumber):
        cmdString = ':MEASure:VMIN? CHANnel' + str(ChannelNumber)
        res = self.instrumentManager.query_ascii_values(cmdString) 
        return res[0]
    
    ####################################################################################
    def measureMaximum(self,ChannelNumber):
        cmdString = ':MEASure:VMax? CHANnel' + str(ChannelNumber)
        res = self.instrumentManager.query_ascii_values(cmdString) 
        return res[0]     
    
    ####################################################################################
    def measureAverageValue(self,ChannelNumber):
        cmdString = ':MEASure:VAVerage? DISPlay,CHANnel' + str(ChannelNumber)
        res = self.instrumentManager.query_ascii_values(cmdString)
        return res[0]     
    
    ####################################################################################
    def measureStandardDeviationValue(self,ChannelNumber):
        cmdString = ':MEASure:VRMS? DISPlay,AC,CHANnel' + str(ChannelNumber) + ',Volt'
        res = self.instrumentManager.query_ascii_values(cmdString) 
        return res[0]  
         
    ####################################################################################
    def setAverage(self,averageOn):
        # no average implemented in the moment
        if averageOn:
            self.instrumentManager.write(":ACQuire:AVERage ON"); 
        else:
            self.instrumentManager.write(":ACQuire:AVERage OFF"); 
 
    ####################################################################################
    def setAverageCount(self,averageNumber):
        self.instrumentManager.write(":ACQuire:AVERage:COUNt "+ str(averageNumber));
     
    ####################################################################################
    def setTimeOffset(self,timeOffset):
        self.instrumentManager.write(":TIMebase:POSition "+str(timeOffset));    
    
    ####################################################################################
    def setTimeSpan(self,timeSpan):
        self.instrumentManager.write(":TIMebase:REFerence LEFT");   
        timeRangeString = ''.join([":TIMebase:RANGe ", str(timeSpan)])
        self.instrumentManager.write(timeRangeString);  
    
    ####################################################################################
    def setChannelOffset(self,channelNumber,channelOffset):
        self.instrumentManager.write(":CHANnel"+str(channelNumber)+":OFFSet "+str(channelOffset)); 
        
    ####################################################################################
    def setChannelRange(self,channelNumber,ChannelRange):
        self.instrumentManager.write(":CHANnel"+str(channelNumber)+":RANGe "+str(ChannelRange));      
    
    ####################################################################################
    def setTriggerLevel(self,channelNumber,level):
        self.instrumentManager.write(":TRIGger:LEVel CHANnel"+str(channelNumber)+","+str(level));      
        
    ####################################################################################
    def verticalAutoRange(self,channelNumber,NrOfStd = 2, offset=0,v_range=40):   
        self.setChannelOffset(channelNumber, offset)
        self.setChannelRange(channelNumber,v_range)                
              
        for i in np.arange(5):   
            self._readScopeSingle([channelNumber],1,0)
            avg = self.measureAverageValue(channelNumber)
            max = self.measureMaximum(channelNumber)
            min = self.measureMinimum(channelNumber)
            std = self.measureStandardDeviationValue(channelNumber)
            self.setChannelOffset(channelNumber, avg)
            if v_range/2>(max-min):
                v_range = v_range/2
            else:
                v_range = (max-min)
            self.setChannelRange(channelNumber, v_range)  
        v_range = (max-min)*2   
        self.setChannelRange(channelNumber, v_range)   
        self.setTriggerLevel(channelNumber, avg)
        #self.setChannelRange(channelNumber, NrOfStd*std)   
             
    ####################################################################################
    def readScope(self,readOutChannelNumberList = [1],sampleRate=1e9,pointCount = 512.5e3,onlyReadOut = False,plotResult = False):
        ####################################################################################
        #                     Connect to device and get device Information
        self.openConnectionOszi()
        data = self._readScope(readOutChannelNumberList,sampleRate,pointCount,onlyReadOut,plotResult)
        self.closeConnetion()
        return data
    
    def _readScopeSingle(self,readOutChannelNumberList = [1],stopAfterFinish = 0,ReadOut=True):

        ####################################################################################
        #                 setup measurement configuration and measurement
        instrumentManager = self.instrumentManager
        updateDataDelayTime = 0.1
       
        ####################################################################################
        #                         take single measurement
        instrumentManager.write(":STOP");
        instrumentManager.query_ascii_values(":ADER?");
        
        currentTime = 0;
        timeOutTime = 60;
        instrumentManager.write(":SINGLE");  # make sure new data is acquired
        
        while(currentTime <= timeOutTime):
            ader = instrumentManager.query_ascii_values(":ADER?")
            if (ader[0] == 1):
                break;
            else:
                sleep(updateDataDelayTime)
                currentTime = currentTime + updateDataDelayTime;
            
        result = []
        if ReadOut:
            result =  self._readOutChannels(readOutChannelNumberList)
        
        if not(stopAfterFinish):
            instrumentManager.write(":RUN"); 
        
        return result 
    
    def _readOutChannels(self,readOutChannelNumberList = [1]):  
        readOutDelayTime = 0.1  # time delay in [s] between write and read commands of data 
                                # transfer to prevent empty readings
         
        ####################################################################################
        #                                 read out data
        #  
        instrumentManager = self.instrumentManager
        traceList = list()
           
        for readOutChannelNumber in readOutChannelNumberList:
                
                # check for number of acquired points    
            acquiredPoints  =  instrumentManager.query(":WAVeform:POINTs?")
            #print(''.join(['number of acquired samples: ', str(acquiredPoints)]))
                     
                # set read out channel 
            channelString = ''.join(["CHANnel" , str(readOutChannelNumber)])
                # set read out format
            instrumentManager.write(''.join([':WAVeform:SOURce ',channelString]))
                # set data transfer type format
            instrumentManager.write(":WAVeform:FORMat WORD")
                # sent read out prepare command
            instrumentManager.write(":WAVeform:DATA?")
                # small pause, otherwise empty result is retrieved 
            sleep(readOutDelayTime) 
                # read out channel
            rawDataByteArray = instrumentManager.read_raw()  
            
                # get data trace conversion parameter for x-axes
            XINCrement = instrumentManager.query_ascii_values(':WAVeform:XINCrement?')
            XORigin = instrumentManager.query_ascii_values(':WAVeform:XORigin?')
            XREFerence = instrumentManager.query_ascii_values(':WAVeform:XREFerence?') # should always be zero 
            XUNits = instrumentManager.query(':WAVeform:XUNits?')
            XUNits = XUNits.rstrip('\n').lower()
            
                # get data trace conversion parameter for y-axes
            YINCrement = instrumentManager.query_ascii_values(':WAVeform:YINCrement?')
            YORigin = instrumentManager.query_ascii_values(':WAVeform:YORigin?')
            YREFerence = instrumentManager.query_ascii_values(':WAVeform:YREFerence?') # should always be zero 
            YUNits = instrumentManager.query(':WAVeform:YUNits?')
            YUNits = YUNits.rstrip('\n').lower()
            
            # convertData -> check manual for concrete data structure convention
                # check whether first byte equals '#' sign 
            if  '#' == rawDataByteArray[0:1].decode("utf-8"):
                # read next byte giving the number of bytes in the length block 
                lengthBytes = int(rawDataByteArray[1:2].decode("utf-8"));
                dataLength = int(rawDataByteArray[2:2+lengthBytes].decode("utf-8"));
                fmt = 'h'*int(dataLength/2)
                yAxesData = struct.unpack_from(fmt, rawDataByteArray, offset=1+lengthBytes)
                
                # log number of collected data points
            numOfPoints = len(yAxesData)
            #print(''.join(['number of collected samples: ', str(numOfPoints)]))
            
                # convert x-axes trace 
            xAxes = np.array(range(numOfPoints))*XINCrement+XORigin
                # convert y-axes trace 
            calyAxesData = np.array(yAxesData)*YINCrement[0] + YORigin
            
            
            traceData = {
                'traceNumber' : readOutChannelNumber,
                'xAxes' : xAxes,
                'yAxes' : calyAxesData,
                'yAxesRaw' : yAxesData
                }
            
            traceList.append(traceData)
            
            # update channel settings
            CH_dic = {}  
            CH_dic['XINCrement'] = XINCrement
            CH_dic['XORigin'] = XORigin
            CH_dic['XREFerence'] = XREFerence
            CH_dic['XUNits'] = XUNits
            
            CH_dic['YINCrement'] = YINCrement
            CH_dic['YORigin'] = YORigin
            CH_dic['YREFerence'] = YREFerence
            CH_dic['YUNits'] = YUNits 
            self.channel_setting[channelString] =  CH_dic;
        
        # get some para    
        samplingRate = instrumentManager.query_ascii_values(":ACQuire:SRATe?");
        #print(str(samplingRate))
        #resultData = {'traceList':traceList, 'samplingRate':samplingRate }
            
        return traceList
    
    
    def _readScope(self,readOutChannelNumberList = [1],sampleRate=1e9,pointCount = 512.5e3,onlyReadOut = False,plotResult = False):
        # plotResult: 
                # switch: True: read out result is plotted at the end
                #         False: not plotted
        # onlyReadOut = False;    
                # switch: True: only read out preacquired scope data
                #         False: make single shot realTime measurement
        
        readOutDelayTime = 0.1  # time delay in [s] between write and read commands of data 
                                # transfer to prevent empty readings
        
        timeSpan = pointCount/sampleRate; # in s
        #print(timeSpan)
        updateDataDelayTime = 0.1
        

        
        ####################################################################################
        #                 setup measurement configuration and measurement
        instrumentManager = self.instrumentManager
        systemHeaders = instrumentManager.write(':SYSTem:HEADer OFF')  
        
        if not(onlyReadOut):
            ####################################################################################
            #                 setup measurement configuration and measurement
            # 
            #    Manual preparation tasks: set oszi in way that the signal is well in y-range 
            #    Prgramming task: set sample rate and time span
            # 
            
            instrumentManager.write(":ACQuire:MODE RTIMe");
                # no average implemented in the moment
            instrumentManager.write(":ACQuire:AVERage OFF"); 
            
                # max number of points
            pointsString = ''.join([":ACQuire:POINts ", str(pointCount)])   
            instrumentManager.write(pointsString); 
        
                # sample rate 
            sampleRateString = ''.join([":ACQuire:SRATe ", str(sampleRate)])   
            #print(sampleRateString)
            instrumentManager.write(sampleRateString); 
            
                # time range settings
            instrumentManager.write(":TIMebase:POSition 0");     
            instrumentManager.write(":TIMebase:REFerence LEFT");   
            timeRangeString = ''.join([":TIMebase:RANGe ", str(timeSpan)])
            instrumentManager.write(timeRangeString); 
                   
         
            srSpanString = instrumentManager.query(":ACQuire:SRATe?");       # time span
            #print(''.join(["time span: ", str(srSpanString.rstrip('\n')), "s"]))     
            timeSpanString = instrumentManager.query(":TIMebase:RANGe?");       # time span
            #print(''.join(["time span: ", str(timeSpanString.rstrip('\n')), "s"]))       
            
        
            ####################################################################################
            #                         take single measurement
            instrumentManager.write(":STOP");
            instrumentManager.query_ascii_values(":ADER?");
            
            currentTime = 0;
            timeOutTime = 30;
            instrumentManager.write(":SINGLE");  # make sure new data is acquired
            
            while(currentTime <= timeOutTime):
                ader = instrumentManager.query_ascii_values(":ADER?")
                if (ader[0] == 1):
                    break;
                else:
                    sleep(updateDataDelayTime)
                    currentTime = currentTime + updateDataDelayTime;
            
            
        result =  self._readOutChannels(readOutChannelNumberList)
        
        if not(onlyReadOut):
            instrumentManager.write(":RUN"); 
            
        return result 
    
            
        ####################################################################################
        # update tool setting
        self.updateToolSetting()  
    
    
    ####################################################################################
    # save data
    #################################################################################### 
 
    def saveData(self,traceList,singleMeasureName,measurementPurposeShort):
        # build fileString
        fs = "\\"
        
        rootDataLocation = "C:\\Users\\arnek\\OneDrive\\Unis\\DTU\\QPIT-Data"
        
        operatorInitials = 'AK'   
        
        folderTimeStamp = time.strftime("%Y-%m-%d")
        folderName = ''.join([folderTimeStamp,'-',operatorInitials,'-',measurementPurposeShort])
        
        fileTimeStamp = time.strftime("%H%M")
        fileName = ''.join([fileTimeStamp, '_' , singleMeasureName])
        
        folderLocation = ''.join([rootDataLocation,fs,folderName,fs,'rawData'])
        fileLocation = ''.join([folderLocation, fs, fileName])
        
        try:
            os.stat(folderLocation)
        except:
            os.makedirs(folderLocation)       
        
        for traceDict in traceList:
            traceNumber = traceDict['traceNumber']
            traceString = ''.join([fileLocation,'_CH',str(traceNumber)])
            xAxes = traceDict['xAxes']
            yAxes = traceDict['yAxes']
            yAxesRaw = traceDict['yAxesRaw']
            np.savetxt(''.join([traceString,'.csv']), np.c_[xAxes,yAxes], delimiter=",", newline='\r\n')
            np.savetxt(''.join([traceString,'_raw.csv']), np.c_[np.array(yAxesRaw, dtype=np.int16)], delimiter=",", newline='\r\n', fmt='%d')
            
if False:
    tool = Oszi_Keysight_DSOS104a()
    tool.openConnectionOszi()
    tool.setChannelOffset(1, 0.02)
    tool.setChannelRange(1, 2)
    tool.verticalAutoRange(1, 2)
    tool.setTimeOffset(300e-6)
    tool.setTimeSpan(300e-6)
    tool.setAverageCount(100)
    tool.setAverage(1)
    tool._readScopeSingle([1],1)
    avg = tool.measureAverageValue(1)
    std = tool.measureStandardDeviationValue(1)
    print('avg: '+ str(avg)+ ' std: ' + str(std))
    tool.setChannelOffset(1, avg-3*std)
    tool.setChannelRange(1, 6*std)
        
    tool.setAverageCount(1000)
    tool.setAverage(1)
    tool._readScopeSingle([1],1)
    avg = tool.measureAverageValue(1)
    std = tool.measureStandardDeviationValue(1)
    print('avg: '+ str(avg)+ ' std: ' + str(std))
    # 500: avg: 0.0131576 std: 3.03893e-05
    tool.closeConnetion()