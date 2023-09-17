# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 12:08:07 2023

@author: Administrator
"""

import pyvisa as visa
import time

#user define list voltage output
listMode = [5,0,5,0,5,0,5,0,5,0,5,0]
try:
    #Open Connection Keysight Visa 
    rm = visa.ResourceManager()
    #Connect to VISA Address
    myinst = rm.open_resource("USB0::0x0AAD::0x006E::108450::INSTR")
    #Set Timeout - 5 seconds
    myinst.timeout = 5000
    #*IDN? - Query Instrumnet ID    
    myinst.write("*IDN?")
    print(myinst.read())

    
    myinst.write(':SOURce:AM 15PCT')
    
    myinst.write('SOUR:POW:LEV:IMM:AMPL 15')
    
    myinst.write('SOURce:LFOutput:FREQuency 5kHz')
    

        
#Close Connection
    myinst.close()
    print('close instrument connection')
except Exception as err:
    print('Exception: ' + str(err.message))
finally:
#perform clean up operations
    print('complete')