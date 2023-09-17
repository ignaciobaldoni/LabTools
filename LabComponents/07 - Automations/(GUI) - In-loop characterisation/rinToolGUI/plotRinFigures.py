# -*- coding: utf-8 -*-
"""
Created on Sun Sep 19 10:52:29 2021

@author: akordts
"""
# python standard classes
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.ticker as ticker

# initilize figure
def plotRinFigures(
        freqValues,
        rinVal,
        dc_voltage_V,
        figureFilePath = None,
        presetLimits = True,
        showFig = True,
        plotNum = 1,
        measLabel = '',
        specLabel = '',
        filename_spec = None):
    
    
    plotStylereferenceFile = os.getcwd() + os.sep + 'RIN_v2.mplstyle'
    
    # %% Menlo reference plotting
    
    xlimits     = [1,10**7]
    ylimits     = [-160,-70]#[0, .07]
    
    fig = plt.figure(plotNum)
    plt.clf()  
    plt.style.use(plotStylereferenceFile)
    plt.ion()
    # plt.close()
    # Plot spectra
    
    # fig, ax = plt.subplots(1) 
    ax = plt.gca()
    # plt.semilogx(freqValues, rinVal, label="Measurement")
    
    plt.plot(freqValues, rinVal, label = measLabel)
    ax.set_xscale('log')
    
    if filename_spec != None:
        spec = np.loadtxt(filename_spec, delimiter=',',skiprows = 2)
        # plt.semilogx(spec[:,0], spec[:,1], label="Spec. (T) Output",marker='x',linestyle=':', markersize = 4)
        plt.plot(spec[:,0], spec[:,1], label=specLabel,marker='x',linestyle=':', markersize = 4,markeredgewidth=0.5)
    
    plt.legend(loc="upper right")  
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("One-sided PSD of RIN (dBc/Hz)")
    
    # if title != None:
    #     plt.title(title)
    
    if xlimits != [] and presetLimits:
        plt.xlim(xlimits[0],xlimits[1])
    #
    if ylimits != [] and presetLimits  :
        plt.ylim(ylimits[0],ylimits[1])
    

    if figureFilePath != None and specLabel != '':
        figureFilePath = figureFilePath.replace('\\', '/')
        # filename = figureFilePath.split(os.sep)[-1]
        print(figureFilePath)
        filename = figureFilePath.split('/')[-2:]
        filename = filename[0] + '/' + filename[1] 
        filename = filename.split('.')[0] + '.*'
        
        textstr = filename #+ '\n$\lambda_\mathrm{c}=%.1f$ nm\n$\lambda_\mathrm{FWHM}=%.1f$ nm\n$P=%.2f$ mW'%(lCarrier, lWidth, power)
        #    
        props = dict(boxstyle='round', facecolor='white', alpha=1) # these are matplotlib.patch.Patch properties
        ax.text(0.05, 0.10, textstr, transform=ax.transAxes, fontsize=5,verticalalignment='top', bbox=props)    # place a text box in upper left in axes coords
   
    
    
    ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
    
    x_major = ticker.LogLocator(base = 10.0, numticks = 10)
    ax.xaxis.set_major_locator(x_major)

    x_minor = ticker.LogLocator(base = 10.0, subs = np.arange(1.0, 10.0, 2) * 0.1, numticks = 10)
    # x_minor = ticker.LogLocator(base = 10.0, subs = 'all', numticks = 5)
    ax.xaxis.set_minor_locator(x_minor)
   
    plt.tight_layout() 
    
    if showFig:
        fig.canvas.draw()
        fig.canvas.flush_events()

    if figureFilePath != None:
        plt.savefig(figureFilePath)# + '2.png')

    def move_figure(f, x, y):
        """Move figure's upper left corner to pixel (x, y)"""
        backend = plt.get_backend()
        if backend == 'TkAgg':
            f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
        elif backend == 'WXAgg':
            f.canvas.manager.window.SetPosition((x, y))
        else:
            # This works for QT and GTK
            # You can also use window.setGeometry
            f.canvas.manager.window.move(x, y)

    if plotNum == 1:
        move_figure(fig,10, 10)
    else:
        move_figure(fig,910, 10)

    # plt.show()
    
    # # %% origional plotting
    
    # fig = plt.figure(2)
    # plt.clf()
    # plt.style.use(plotStylereferenceFile)
    
    # plt.plot(freqValues, rinVal)
    
    # if title != None:
    #     plt.title(title)
    
    # ax = plt.gca()
    # ax.set_xscale('log')
    
    # # ax.set(xlabel='frequency [Hz]', ylabel=r'power $\left[\mathrm{V}_{\mathrm{rms}}/\sqrt{\mathrm{Hz}}\right]$' )
    # ax.set(xlabel='frequency [Hz]', ylabel=r'dBc/Hz' )
    # ax.grid()
    
    # fig.canvas.draw()
    # fig.canvas.flush_events()
    
    # if figureFilePath != None:
    #     plt.savefig(figureFilePath)
    
    print(rinVal)    
    return rinVal

    
# %% main
if __name__ == '__main__':

    import sys

    plotRinFigures(
            [1,2,4,5,7],
            [1e-6,2e-6,4e-6,5e-6,7e-6],
            3.4,
            plotNum = 2,
            figureFilePath = os.getcwd() + '/' + 'bla.png')
    # sys.exit(app.exec_()) 