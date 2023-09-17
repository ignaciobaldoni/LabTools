# -*- coding: utf-8 -*-
"""
Created on Sat Sep 18 15:24:36 2021

@author: akordts
"""

import time

##############################################################################
# content from igor initScalar()
##############################################################################

def initESAforRINmeasurement(visaobj, isCrossSpectrumConf = False):
    # cmds list:
        # *WAI
            # Holds off processing of subsequent commands until all preceding 
            # commands have been processed.
        # *CLS
            # Clears the Status Byte by emptying the error queue and clearing 
            # all event registers.
            # In addition, *CLS cancels any preceding *OPC command or query. 
            # This ensures that bit 0 of the Standard Event register is not 
            # set to 1 and that a response is not placed in the analyzer’s 
            # output queue when pending overlapped commands are completed
        # *OPC
            # Specifies or queries completion of all pending overlapped commands
        # ABORT
            # Abort the current measurement in progress.
    
    
    # load Rin.sta instrument state from floppy disk
        # cmd: MMEMory:LOAD:STATe <number>,<filename
            # <number> ::= a real number (state number) limits: 1:1
            # <filename> ::= ‘[<msus>]<filespec>’
            # <msus> ::= RAM:|NVRAM:|INT:|EXT:
            # <filespec> ::= ASCII characters
            
            # Loads an instrument state into the analyzer from the mass 
            # storage unit specified (msus).
    # data = visaobj.write(" MMEMory:LOAD:STATe 1, 'RIN.sta';*WAI")
    
    
    visaobj.write("SYSTem:PRESet;*WAI")
    
    # [SENSe:]VOLTage[1|2][:DC]:RANGe:AUTO OFF|0|ON|1|ONCE
    # [SENSe:]VOLTage[1|2][:DC]:RANGe:AUTO:DIRection UP|EITHer
    visaobj.write("SENSe:VOLTage:RANGe:AUTO:DIRection EITHer;*WAI")
    visaobj.write("SENSe:VOLTage:RANGe:AUTO ON;*WAI")
    
    # [SENSe:]SWEep:POINts <number>|<step>|<bound>
    # SWE1:POIN +1601
    visaobj.write("SENSe:SWEep:POINts MAX;*WAI")
    
    
    # Data Format: x-axes log-scale
    visaobj.write("DISPlay:WINDow1:TRACe:X:SCALe:SPACing LOG;*WAI")
    
    
    # resetting the ESA 
    data = visaobj.write("*CLS")
    data = visaobj.write("ABORT")
    
        # turns off the source port of the ESA, which is not used in the 
        # measurement
        # cmd: OUTPut[:STATe] OFF|0|ON|1
            # Turns the source output on and off
    # data = visaobj.write("OUTP OFF;*WAI")
    data = visaobj.write("OUTP OFF")
           
    # set analyzer into vector mode
        # select instrument mode
    data = visaobj.write("INSTrument vector")
    
        # set receiver type: signal input is connected to channel 1
    data = visaobj.write("ROUTe:RECeiver INPUT")
    
        # turns ons the specific channel: 
        # cmd: INPut[1|2][:STATe] OFF|0|ON|1
    if isCrossSpectrumConf:
        data = visaobj.write("INPut1 1")
        data = visaobj.write("INPut2 1")
    else:
        data = visaobj.write("INPut1 1")
        data = visaobj.write("INPut2 0")    
    
        # set impedance to 1M
        # full cmd: INPut[1|2]:IMPedance <number>[<unit>]
        # possible value: 50, 75, 1e6, 1MOHM
    # data = visaobj.write("INPut1:IMPedance 50")
    data = visaobj.write("INPut1:IMPedance 1e6")
    data = visaobj.write("INPut2:IMPedance 1e6")
    
        # full cmd: [SENSe:]BANDwidth:MODE:ARBitrary OFF|0|ON|1
        # description: 
            # When BAND:MODE:ARB is OFF, only values in the 1-3-10 sequence 
            # are valid entries. When it is ON, any value (within limits) is valid.
    data = visaobj.write("SENSe:BANDwidth:MODE:ARBitrary 0")
    
        # full cmd: [SENSe:]BANDwidth[:RESolution]:AUTO OFF|0|ON|1
        # description: 
            # At preset and power-on, resolution bandwidth (RBW) tracks span 
            # changes to maintain an internally-defined RBW/span ratio. 
            # (The resulting RBW also depends on the state of BAND:MODE:ARB.)
    data = visaobj.write("SENSe:BANDwidth:RESolution:AUTO 1")
        
        # Selects the FFT window type
        # cmd: [SENSe:]WINDow[:TYPE] UNIForm|FLATtop|HANNing|GTOP
    data = visaobj.write("SENSe:WINDow:TYPE FLAT;*WAI")
    
        # cmd: [SENSe:]AVERage[:STATe] OFF|0|ON|1
            # Turns averaging on and off
        # cmd: [SENSe:]AVERage:TYPE MAX|RMS|COMPlex
            # [SENSe:]AVERage:TYPE MAX|RMS|COMPlex
        # [SENSe:]AVERage:TCONtrol EXPonential|NORMal|REPeat
            # Terminal Control specifies the action of the AVERage subsystem when 
            # AVERage:COUNt measurement results are generated
            # EXPonential: Continue the average with an exponential weighting 
                # applied to old values.
    data = visaobj.write("SENSe:AVERage:STATe ON;TYPE RMS;TCON EXP")
    
        # set data to be displayed to PSD
        # cmd: CALCulate[1|2|3|4]:FEED <string>
            # Selects the measurement data to be displayed
        # cmd: CALCulate[1|2|3|4]:UNIT:POWer <unit>
            # Specifies the default y-axis units for power measurements

    if isCrossSpectrumConf:        
                # XFR:POW:CROS 2,1
        data = visaobj.write("CALCulate:FEED 'XFR:POW:CROS 2,1';*WAI")
        data = visaobj.write('CALCulate:UNIT:POW Vrms2;*WAI')
    else:
        data = visaobj.write("CALCulate:FEED 'XFR:POW 1';*WAI")
        data = visaobj.write('CALCulate:UNIT:POW Vrms2;*WAI')

    #         # XFR:POW 1

    
    #         # XFR:POW:PSD 1
    # data = visaobj.write("CALCulate:FEED 'XFR:POW:PSD 1';*WAI")
    # data = visaobj.write('CALCulate:UNIT:POW Vrms/rtHz;*WAI')
        
