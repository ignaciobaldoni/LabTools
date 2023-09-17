# -*- coding: utf-8 -*-
"""
Created on Wed May 31 17:08:39 2023

@author: ibaldoni
"""


import pyvisa as visa
import time

#user define list voltage output
listMode = [5,0,5,0,5,0,5,0,5,0,5,0]
try:
    #Open Connection Keysight Visa 
    rm = visa.ResourceManager()
    #Connect to VISA Address
    myinst = rm.open_resource("USB0::0x2A8D::0x1102::MY61003592::INSTR")
    #Set Timeout - 5 seconds
    myinst.timeout = 5000
    #*IDN? - Query Instrumnet ID    
    myinst.write("*IDN?")
    print(myinst.read())
    #Select Channel Output to program, This line is multiple channel output
    myinst.write(':INSTrument:NSELect 1')
    #Enable output ON
    myinst.write(':OUTPut:STATe 1')
    #generate voltage level output in sequence
    for x in range (len(listMode)):
        myinst.write(':SOURce:VOLTage:LEVel:IMMediate:AMPLitude %G' % listMode[x])
        #change this delay to increase or decrease output intervals        
        myinst.timeout = 1000
        time.sleep(1)
        
#Close Connection
    myinst.close()
    print('close instrument connection')
except Exception as err:
    print('Exception: ' + str(err.message))
finally:
#perform clean up operations
    print('complete')