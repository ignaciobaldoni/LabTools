# -*- coding: utf-8 -*-
"""
Created on Sun Sep 19 10:52:29 2021

@author: akordts
"""
# python standard classes
import matplotlib.pyplot as plt
import numpy as np

# initilize figure
def plotRinFigures(freqValues,powValues,dc_voltage_V,figureFilePath = None,title = None):
    
    plt.ion()
    
    fig = plt.figure(1)
    plt.clf()
    
    
    rinVal = 20*np.log10(np.array(powValues)/dc_voltage_V)
    plt.plot(freqValues, rinVal)
    
    if title != None:
        plt.title(title)
    
    ax = plt.gca()
    ax.set_xscale('log')
    
    # ax.set(xlabel='frequency [Hz]', ylabel=r'power $\left[\mathrm{V}_{\mathrm{rms}}/\sqrt{\mathrm{Hz}}\right]$' )
    ax.set(xlabel='frequency [Hz]', ylabel=r'dBc/Hz' )
    ax.grid()
    
    fig.canvas.draw()
    fig.canvas.flush_events()
    
    if figureFilePath != None:
        plt.savefig(figureFilePath)