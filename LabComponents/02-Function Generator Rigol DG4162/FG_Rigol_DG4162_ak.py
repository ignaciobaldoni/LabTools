# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 12:01:37 2021

@author: akordts
"""
import logging
logger = logging.getLogger(__name__)

import pyvisa as visa

class RigolDG4162:
    '''
    A class for controlling the Rigol DG4162 Function generator
    '''
    
    # %% connections functions
    def __init__(self, resource):
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
    
    def connect(self, resource):
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
        
        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
          self.instrumentManager = rm.open_resource(resource)
          self.instrumentManager.timeout = 2000
          queryStr = '*IDN?'
          data = self.instrumentManager.query(queryStr)
          logger.debug('selected device is: '+ data.strip())
        except visa.VisaIOError as e:
          logger.error(e.args)
    
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
        # self.visaobj.control_ren(6) # sends GTL (Go To Local) command
        self.instrumentManager.close()
        logger.info('FG disconnected')

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
        try:
            # cmd = cmd + ';*WAI'
            self.instrumentManager.write(cmd)
        except Exception as exc:
            logger.error(exc)
        else:
            logger.debug('writeCmd: ' + cmd)
        finally:
            pass

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
        data = None

        try:
            cmd = cmd + ';*WAI'
            data = self.instrumentManager.query(cmd)
        except Exception as exc:
            logger.error(exc)
        else:
            logger.debug('query: ' + cmd)
        finally:
            pass

        return data
    
    # %% waveform selection
    
    def setWaveformToRamp(self,channelNr):
        # [:SOURce<n>]:APPLy:RAMP [<freq>[,<amp>[,<offset>[,<phase>]]]]
        
        cmdStr = ':SOURce'+str(channelNr) \
                 +':APPLy:RAMP '
        self.writeCmd(cmdStr)
        logger.debug(
                'Channel ' + str(channelNr)+ 
                ' : waveform set to ramp'
            ) 
    
    # %% source settings
    
    def readSourceLowLevel(self,channelNr):
        """
        [:SOURce<n>]:VOLTage[:LEVel][:IMMediate]:LOW? [MINimum|MAXimum]

        Parameters
        ----------
        channelNr : int
            select channel 1 or 2

        Returns
        -------
        data : float
            low level voltage

        """
        
        queryStr = ":SOURce{}:VOLTage:LOW?".format(str(channelNr))
        data = self.queryCmd(queryStr)
        data = float(data.strip())
        logger.debug('Channel ' + str(channelNr)+ ' : current low level is: '+ data)
    
        return data

    def set_offset_level_volt(self, channel_nr, offset_volt):
        # [:SOURce<n>]:VOLTage[:LEVel][:IMMediate]:OFFSet

        cmd_str = ':SOURce' + str(channel_nr) \
                  + ':VOLTage:LEVel:OFFSet ' + str(offset_volt)
        self.writeCmd(cmd_str)
        logger.debug(
            'Channel ' + str(channel_nr) +
            ' : current low level set to: ' + str(offset_volt)
        )

    def read_offset_level_volt(self, channel_nr):
        query_str = ":SOURce{}:VOLTage:OFFSet?".format(str(channel_nr))
        data = self.queryCmd(query_str)
        data = float(data.strip())
        logger.debug('Channel ' + str(channel_nr) + ' : current high level is: ' + str(data))

        return data

    def setSourceLowLevel(self,channelNr,lowLevel_V):
        """
        [:SOURce<n>]:VOLTage[:LEVel][:IMMediate]:LOW? [MINimum|MAXimum]

        Parameters
        ----------
        channelNr :  int
            select channel 1 or 2
        lowLevel_V : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # [:SOURce<n>]:VOLTage[:LEVel][:IMMediate]:LOW <voltage>|MINimum|MAXimum
        
        cmdStr = ':SOURce'+str(channelNr) \
                 +':VOLTage:LEVel:LOW ' + str(lowLevel_V)
        self.writeCmd(cmdStr)
        logger.debug(
                'Channel ' + str(channelNr)+ 
                ' : current low level set to: '+ str(lowLevel_V)
            ) 
    
    def readSourceHighLevel(self,channelNr):
        """
        [:SOURce<n>]:VOLTage[:LEVel][:IMMediate]:HIGH? [MINimum|MAXimum]

        Parameters
        ----------
        channelNr : int
            select channel 1 or 2

        Returns
        -------
        data : float
            high level voltage

        """
        
        queryStr = ":SOURce{}:VOLTage:HIGH?".format(str(channelNr))
        data = self.queryCmd(queryStr)
        data = float(data.strip())
        logger.debug('Channel ' + str(channelNr)+ ' : current high level is: '+ data)
    
        return data
    
    def setSourceHighLevel(self,channelNr,highLevel_V):
        """
        [:SOURce<n>]:VOLTage[:LEVel][:IMMediate]:HIGH? [MINimum|MAXimum]

        Parameters
        ----------
        channelNr :  int
            select channel 1 or 2
        highLevel_V : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        cmdStr = ':SOURce'+str(channelNr) \
                 +':VOLTage:LEVel:HIGH ' + str(highLevel_V)
        self.writeCmd(cmdStr)
        logger.debug(
                'Channel ' + str(channelNr)+ 
                ' : current high level set to: '+ str(highLevel_V)
            ) 

    def readSourceFixedFrequency(self,channelNr):
        """
        [:SOURce<n>]:FREQuency[:FIXed]? [MINimum|MAXimum]

        Parameters
        ----------
        channelNr : int
            select channel 1 or 2

        Returns
        -------
        data : float
            Fixed Frequency in Hz

        """
        
        queryStr = ':SOURce'+str(channelNr)+\
                    ':FREQuency:FIXed?'
                    
        data = self.queryCmd(queryStr)
        data = float(data.strip())
        logger.debug('Channel ' + str(channelNr)+ ' : current fixed frequency is: '+ str(data))
    
        return data

    def setSourceFixedFrequency(self,channelNr,fixedFrequency_Hz):
        """
        [:SOURce<n>]:FREQuency[:FIXed] <frequency>|MINimum|MAXimum        

        Parameters
        ----------
        channelNr : int
            select channel 1 or 2
        fixedFrequency_Hz : float
            fixed Frequency in Hz

        Returns
        -------
        None.

        """
        cmdStr = ':SOURce'+str(channelNr) \
                 +':FREQuency:FIXed ' + str(fixedFrequency_Hz)
        self.writeCmd(cmdStr)
        logger.debug(
                'Channel ' + str(channelNr)+ 
                ' : current fixed frequency set to: '+ str(fixedFrequency_Hz)
            ) 
    
    # %% burst mode settings
    
    def readburstModeState(self,channelNr):
        """
        [:SOURce<n>]:BURSt[:STATe]?

        Parameters
        ----------
        channelNr : int
            select channel 1 or 2

        Returns
        -------
        data : str
            ON or OFF

        """
        queryStr = ':SOURce'+str(channelNr)+\
                    ':BURSt:STATe?'
                    
        data = self.queryCmd(queryStr)
        logger.debug('Channel ' + str(channelNr)+ ' : burstmode state is: '+ data)
    
        return data
    
    def setburstModeState(self,channelNr,stateBool): 
        """
        [:SOURce<n>]:BURSt[:STATe] ON|OFF

        Parameters
        ----------
        channelNr : int
            select channel 1 or 2
        stateBool : bool 
            True for burst mode ON
            False for burst mode OFF

        Returns
        -------
        None.

        """
        
        if stateBool:
            stateStr = 'ON'
        else:
            stateStr = 'OFF' 
        
        cmdStr = ':SOURce'+str(channelNr) \
                 +':BURSt:STATe ' + str(stateStr)
        self.writeCmd(cmdStr)
        logger.debug(
                'Channel ' + str(channelNr)+ 
                ' : burstmode state set to: '+ str(stateStr)
            ) 
        
    def readBurstModeTriggerSource(self,channelNr):
        """
        SOURce[:SOURce<n>]:BURSt:TRIGger:SOURce?

        Parameters
        ----------
        channelNr : int
            select channel 1 or 2

        Returns
        -------
        data : str
            trigger Source description

        """
        queryStr = ':SOURce'+str(channelNr)+\
                    ':BURSt:TRIGger:SOURce?'
                    
        data = self.queryCmd(queryStr)
        logger.debug('Channel ' + str(channelNr)+ ' : burstmode trigger SOURce is: '+ data)
    
        return data
    
    def setBurstModeTriggerSource(self,channelNr,triggerSource):
        """
        [:SOURce<n>]:BURSt:TRIGger:SOURce INTernal|EXTernal|MANual

        Parameters
        ----------
        channelNr : int
            select channel 1 or 2
        triggerSource : str
            INTernal|EXTernal|MANual

        Returns
        -------
        None.

        """
        cmdStr = ':SOURce'+str(channelNr) \
                 +':BURSt:TRIGger:SOURce ' + str(triggerSource)
        self.writeCmd(cmdStr)
        logger.debug(
                'Channel ' + str(channelNr)+ 
                ' : burstmode state set to: '+ str(triggerSource)
            ) 
        
    
    def readBurstModeStartPhase(self,channelNr):
        """
        [:SOURce<n>]:BURSt:PHASe? [MINimum|MAXimum]

        Parameters
        ----------
        channelNr : int
            select channel 1 or 2

        Returns
        -------
        data : float
            start phase of burst mode

        """
        queryStr = ':SOURce'+str(channelNr)+\
                    ':BURSt:PHASe?'
                    
        data = self.queryCmd(queryStr)
        data = float(data.strip())
        logger.debug('Channel ' + str(channelNr)+ ' : burstmode start phase is: '+ str(data))
 
        return data
    
    def setBurstModeStartPhase(self,channelNr,startPhase_DEG):
        """
        [:SOURce<n>]:BURSt:PHASe <phase>|MINimum|MAXimum

        Parameters
        ----------
        channelNr : int
            select channel 1 or 2
        startPhase : float
            start phase in burst mode

        Returns
        -------
        None.

        """
        cmdStr = ':SOURce'+str(channelNr) \
                 +':BURSt:PHASe ' + str(startPhase_DEG)
        self.writeCmd(cmdStr)
        logger.debug(
                'Channel ' + str(channelNr)+ 
                ' : burst mode start phase set to: '+ str(startPhase_DEG)
            ) 
    
    def burstModeTrigger(self,channelNr):
        # [:SOURce<n>]:BURSt:TRIGger[:IMMediate]
        cmdStr = ':SOURce'+str(channelNr) \
                 +':BURSt:TRIGger:IMMediate'
        self.writeCmd(cmdStr)
        logger.debug(
                'Channel ' + str(channelNr)+ 
                ' : burst mode triggered'
            ) 

    # %% output settings
    def readOutputState(self,channelNr):
        """
        :OUTPut[<n>][:STATe]?

        Parameters
        ----------
        channelNr : int
            select channel 1 or 2

        Returns
        -------
        data : str
            ON or OFF

        """
        queryStr = ':OUTPut'+str(channelNr)+\
                    ':STATe?'
                    
        data = self.queryCmd(queryStr)
        logger.debug('Channel ' + str(channelNr)+ ' : output is: '+ data)
 
        return data
    
    def setOutputState(self,channelNr,stateBool):
        """
        :OUTPut[<n>][:STATe] ON|OFF

        Parameters
        ----------
        channelNr : int
            select channel 1 or 2
        stateBool : bool 
            True for output ON
            False for output OFF

        Returns
        -------
        None.

        """
        if stateBool:
            stateStr = 'ON'
        else:
            stateStr = 'OFF' 
        
        cmdStr = ':OUTPut' + str(channelNr) \
                  +':STATe ' + stateStr
        self.writeCmd(cmdStr)
        logger.debug(
                'Channel ' + str(channelNr)+ 
                ' : output is ' + stateStr
            ) 
    
    # %% simple channel settings      
    def is_enable(self):
        """ Query the state of the output of the signal. """
        data = self.instrumentManager.query(":OUTP:STAT?")
        logger.debug(data)

    def enable(self):
        """ Enables the output of the signal. """
        self.instrumentManager.write(':OUTP ON')
        

    def disable(self):
        """ Disables the output of the signal. """
        self.instrumentManager.write(":OUTP OFF")
    
    
    def read_frequency(self):
        """ Current frequency"""
        self.instrumentManager.timeout = 60000 # set timeout to 60s for measurement
        data = self.instrumentManager.query(':FREQ?')
        self.instrumentManager.timeout = 2000 # set timeout back to 2s

        return data  
    
    def read_amplitude(self):
        """ Current amplitude """
        
        self.instrumentManager.timeout = 60000 # set timeout to 60s for measurement
        data = self.instrumentManager.query(':POW?')
        self.instrumentManager.timeout = 2000 # set timeout back to 2s

        return data  
    
    def set_frequency(self,value):
        """Set frequency in Hz (according to manual)"""
        
        self.instrumentManager.timeout = 6000 # set timeout to 60s
        
        word = "FREQ {}".format(str(value))
        data = self.instrumentManager.write(word)
        # data = self.visaobj.query(word)
        logger.debug('Frequency set at %s Hz'%value)
        # self.visaobj.timeout = 2000 # set timeout back to 2s


    def set_amplitude(self,channel,value):
        """Set Amplitude in V for selected channel output"""
        
        self.instrumentManager.timeout = 10000 # set timeout to 60s for measurement
        word = "SOUR{}:VOLT {}".format(str(channel),str(value))
        
        data = self.instrumentManager.write(word)
        
        self.instrumentManager.timeout = 2000 # set timeout back to 2s
        logger.debug('Amplitude of channel %s set to %s Vpp'%(channel,value))
        return data  
    
    
    def set_offset(self,channel, value):
        """ Set Offset in V for selected channel output"""
        
        self.instrumentManager.timeout = 10000 # set timeout to 60s for measurement
        word = "SOUR{}:VOLT:OFFS {}".format(str(channel),str(value))
        data = self.instrumentManager.write(word)
        self.instrumentManager.timeout = 2000 # set timeout back to 2s
        logger.debug('Offset of channel %s set to %s Vpp'%(channel,value))
        return data  

    
# %% test code

def initilizeFG(resourceStr):
    
   channelNr = 1
   highLevel_V = 0
   lowLevel_V = -1.5
   fixedFrequency_Hz = 60
   startPhase_DEG = 90
   triggerSource = 'MANual' 
   
   fg = RigolDG4162(resourceStr)         
   fg.setWaveformToRamp(channelNr)
   fg.setSourceHighLevel(channelNr, highLevel_V)
   fg.setSourceLowLevel(channelNr, lowLevel_V)
   fg.setSourceFixedFrequency(channelNr, fixedFrequency_Hz)
   fg.setBurstModeStartPhase(channelNr, startPhase_DEG)
   fg.setOutputState(channelNr, True)
   fg.setburstModeState(channelNr, True)
   fg.setBurstModeTriggerSource(channelNr, triggerSource)
   fg.disconnect()
        
# %% main call  
if __name__ == '__main__':

    resourceStr = 'TCPIP0::10.0.3.170::INSTR'
    
    # initilizeFG(resourceStr)
    
    # time.sleep(3)  
    
    fg = RigolDG4162(resourceStr)
    fg.set_offset_level_volt(2, 0.05)
    fg.disconnect()
    
    # fg.is_enable()    
    # fg.enable()    
    # fg.is_enable()    
    # fg.set_frequency(50)
    
    # channel = 2
    
    # for i in np.arange(-2, 0,0.2):
        
    #     fg.set_offset(channel,i)
    #     # fg.set_amplitude(channel,abs(i))
    #     time.sleep(3)  
    
    # fg.disable()