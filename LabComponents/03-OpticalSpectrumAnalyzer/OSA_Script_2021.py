# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 18:02:59 2021

@author: Administrator
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time

# Oscilloscope = 'TCPIP0::a-mx2024a-00544::inst0::INSTR'
# FuncGenerator = 'TCPIP0::10.0.3.79::inst0::INSTR'
# OSA = 'TCPIP0::169.254.202.228::10001::SOCKET'
# OSA = 'GPIB0::1::INSTR'

def get_trace(OSA_path,trace,start,stop,res,sens=None):
    
    rm = visa.ResourceManager()

    OSA_rm = rm.open_resource(OSA_path, timeout = 3000,read_termination='\n',write_termination='\n')
    osa_reading_time = 3
    
    # print(OSA_rm.query('*IDN?'))
    
    #time for the OSA to read the signal entirely
    time.sleep(osa_reading_time)

    OSA_rm.query('STAWL'+start+'.00')
    OSA_rm.query('STPWL'+stop+'.00')
    
    OSA_rm.query('RESLN'+res)
    if sens != None:
        OSA_rm.query(sens)

    # remove the leading and the trailing characters, split values, remove the first value showing number of values in a dataset
    wl = OSA_rm.query('WDATa').strip().split(',')[1:]
    intensity = OSA_rm.query('LDATa').strip().split(',')[1:]
    # list of strings -> numpy array (vector) of floats
    wl = np.asarray(wl,'f').T
    intensity = np.asarray(intensity,'f').T
    return wl, intensity


if __name__ == '__main__':
    
    measurementPurpose = 'testing OSA'
    
    # OSA Path with GPIB
    OSA = 'GPIB0::1::INSTR'

    trace = 'A'
    start = '1530'
    stop = '1580'
    resolution = '0.02'
    sensitivity = 'SHI1'
    
    # run the measurement
    wavelength, intensity = get_trace(OSA,trace,start,stop,resolution)
    
    plt.figure(figsize=(12,8))
    plt.plot(wavelength,intensity)
    plt.ylim([-100,0])
    plt.grid()
    plt.xlabel('Wavelength [nm]',fontsize=20)
    plt.ylabel('PSD [dB/nm]',fontsize=20)
    plt.title(measurementPurpose,fontsize=20)
    plt.tick_params(labelsize=17)
    # plt.savefig()
    
    # OSA_rm.close()