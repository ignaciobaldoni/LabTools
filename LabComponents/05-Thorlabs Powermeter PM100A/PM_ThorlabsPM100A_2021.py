'''
Created on 14. sep. 2016

@author: arnek
'''

import visa
import matplotlib
#matplotlib.use('qt5agg')
import matplotlib.pyplot as plt
import numpy as np
import time

def readPower(powerMeterIdent):
    resourceManager = visa.ResourceManager()
    # deviceList = resourceManager.list_resources()
    # print(deviceList)
    
    if powerMeterIdent == 2:
        toolString = 'USB0::0x1313::0x8079::p1002888::0::INSTR'
    if powerMeterIdent == 1:
        toolString = 'USB0::0x1313::0x8079::p1000807::0::INSTR'
    if powerMeterIdent == 3:
        toolString = 'USB0::0x1313::0x8078::p0003774::0::INSTR'
    if powerMeterIdent == 4: #UCSB power meter
        toolString = 'USB0::0x1313::0x8072::P2001157::0::INSTR'    
    
    instrumentManager = resourceManager.open_resource(toolString)
    # deviceIdentifyInfo = instrumentManager.query('*IDN?')
    # print(deviceIdentifyInfo)
    instrumentManager.write('SENS:CURR:RANG:AUTO ON\n')
    power = instrumentManager.query_ascii_values('Measure:Scalar:POWer?')[0]
    return power

def monitorPower(powerMeterId):
    
    dataA = np.zeros(100);
    xAces = np.arange(100);
    memMax = 0
    
    plt.axis([0, 100, 0, 1])
    plt.ion()
    
    startTime = time.time()
    while 1:
        # get power
        idCa = readPower(4)
        dataA[0] = idCa * 1e6
        dataA = np.roll(dataA, -1)
        
        plt.figure(1)
        plt.cla()
        plt.scatter(xAces,dataA,color='red')
        
        plt.pause(0.02)
        
        currentTime = time.time()
        if currentTime-startTime>600:
            break

    return memMax

if __name__=='__main__':
    monitorPower(4)
    #print(readPower(4))