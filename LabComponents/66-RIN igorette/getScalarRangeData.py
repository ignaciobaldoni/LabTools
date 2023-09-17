# -*- coding: utf-8 -*-
"""
Created on Sat Sep 18 13:19:46 2021

@author: akordts
"""

import numpy as np
import time 

##############################################################################
# content from igor:  GetScalarRangeData(...)
##############################################################################


def getScalarRangeData(visaobj,sweepPts,startFreq,stopFreq,avgPts):
    # cmd: [SENSe:]SWEep:POINts <number>|<step>|<bound>
                # <number> ::= 51|101|201|401|801|1601|3201
                # <step> ::= UP|DOWN
                # <bound> ::= MAX|MIN
        # Specifies the number of alias-protected frequency points
        # query: [SENSe:]SWEep[1|2]:POINts?
        

    # cmdStr = "SENSe:SWEep1:POINts "+'{:f}'.format(sweepPts)+";*WAI"
    cmdStr = "SENSe:SWEep1:POINts MAX;*WAI"
    visaobj.write(cmdStr)
    
    sweepPts = visaobj.query_ascii_values("SENSe:SWEep1:POINts?")
    sweepPts = sweepPts[0]
    
    # cmd: [SENSe:]FREQuency:STARt <param>
        # Defines the start (lowest) frequency for the measurement band.
    cmdStr = "SENSe:FREQ:STAR "+'{:f}'.format(startFreq)+";*WAI"
    visaobj.write(cmdStr)
    
    # cmd:[SENSe:]FREQuency:STOP <param>
        # Specifies the stop (highest) frequency in the measurement band.
    cmdStr = "SENSe:FREQ:STOP "+'{:f}'.format(stopFreq)+";*WAI"
    visaobj.write(cmdStr)
    
    # cmd:[SENSe:]AVERage:COUNt <number>|<step>|<bound>
        # Specifies the number of traces to be averaged or the weighting 
        # factor for exponential averaging
    cmdStr = "AVERage:COUNt "+'{:.0f}'.format(avgPts)+";*WAI"
    visaobj.write(cmdStr)    
    
    # get rbw
        # cmd:      [SENSe:]BANDwidth[:RESolution] <param>
        # query:    [SENSe:]BANDwidth[:RESolution]?
    rbwValue = visaobj.query_ascii_values("SENSe:BANDwidth:RESolution?")
    rbwValue = rbwValue[0]
    
    
    visaobj.write("ABORT;INIT")
    # visaobj.write("DISP:TRAC:Y:AUTO ONCE;*WAI")
    
    # wait for the operation to finish
    opVal = visaobj.query_ascii_values("*OPC?")
        
    visaobj.write("DISP:TRAC:Y:AUTO ONCE")
    
    powValues = visaobj.query_ascii_values("CALC:DATA?")
    
    
    # make unit conversion
        # from Vrms2 to Vrms/rtHz
    
    # powValues = powValues.tolist()
    
    # calculate freqValues 
    
    # equation from igor
    # SpanFreq[i]+(p-firstNewPt)*((SpanFreq[i+1]-SpanFreq[i])/(SetNumPts[i]-1))
     
    freqStep = (stopFreq-startFreq)/(sweepPts-1)
    freqValues = startFreq + np.arange(sweepPts) * freqStep
    freqValues = freqValues.tolist()
    
    return freqValues,powValues,rbwValue
    
    