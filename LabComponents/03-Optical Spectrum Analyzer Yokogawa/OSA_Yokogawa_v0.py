# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 18:02:59 2021

@author: ibaldoni
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time

class Yokogawa_AQ6370B:
    '''
    A class for controlling the YOKOGAWA AQ6370B 
    Optical Spectrum Analyzer
    '''
    
    
    def __init__(self, resource, label = None):
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
        self.connect(resource, label) 
    
    def connect(self, resource, label = None):
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
        self.label = label
        
        # VisaIOError VI_ERROR_RSRC_NFOUND
        try:
          self.visaobj = rm.open_resource(resource)
          self.visaobj.timeout = 2000
          queryStr = '*IDN?'
          data = self.visaobj.query(queryStr)
          print('idns answer: '+ str(data)) 
        except visa.VisaIOError as e:
          print(e.args)
          raise SystemExit(1)
          

    def get_trace(self,trace,start,stop,res,sens=None):
        
        osa_reading_time = 3    
        
        #time for the OSA to read the signal entirely
        time.sleep(osa_reading_time)
    
        self.visaobj.write('STAWL'+start+'.00')
        self.visaobj.write('STPWL'+stop+'.00')
        
        self.visaobj.write('RESLN'+res)
        if sens != None:
            self.visaobj.query(sens)
    
        # remove the leading and the trailing characters, split values, remove the first value showing number of values in a dataset
        wl = self.visaobj.query('WDAT'+trace).strip().split(',')[1:]
        intensity = self.visaobj.query('LDAT'+trace).strip().split(',')[1:]
        # list of strings -> numpy array (vector) of floats
        wl = np.asarray(wl,'f').T
        intensity = np.asarray(intensity,'f').T
        return wl, intensity
    


if __name__ == '__main__':
    
    measurementPurpose = 'Level of comb at normal output'
    
   
    resourceStr = 'GPIB0::1::INSTR' # OSA Path with GPIB
    
    osa = Yokogawa_AQ6370B(resourceStr)
   
    trace = 'c'
    start = '1530'
    stop = '1570'
    resolution = '0.02'
    sensitivity = 'SHI3'
    
    # run the measurement
    wavelength, intensity = osa.get_trace(trace,start,stop,resolution)
    
    plt.figure(figsize=(12,8))
    plt.plot(wavelength,intensity)
    plt.ylim([-100,0])
    plt.grid()
    plt.xlabel('Wavelength [nm]',fontsize=20)
    plt.ylabel('PSD [dB/nm]',fontsize=20)
    plt.title(measurementPurpose,fontsize=20)
    plt.tick_params(labelsize=17)
    plt.savefig(measurementPurpose+'.png')
        
        
        