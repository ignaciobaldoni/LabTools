# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 09:43:39 2023

@author: ibaldoni

Useful functions for plotting with predefined parameters

"""

import matplotlib.pyplot as plt

def Plot_parameters(style='default', width = 8):
    golden_ratio = (1 + 5 ** 0.5) / 2
    plt.rcParams.update({
        'xtick.labelsize': 15,
        'ytick.labelsize': 15,
        'font.size': 15,
        'figure.figsize': (width,width/golden_ratio),
        'savefig.dpi': 300,
        'grid.alpha': 0.75,
        'figure.constrained_layout.use':True
    })

    plt.style.use(style)
    # plt.style.use('seaborn-dark')
 #%%   
def Plot(x, y, filename='', num=1, 
         xLabel = 'Frequency [Hz]', yLabel = 'Voltage [V]', Title = '',
         label = '', Savefig = False, log_scale = False,loglog = False):

    x = x.astype(float)
    y = y.astype(float)
    
    plt.figure(num)
    plt.plot(x,y,label=str(label))
    plt.xlabel(str(xLabel))
    plt.ylabel(str(yLabel))
    plt.title(str(Title))
    plt.legend()
    plt.grid(which='both',alpha = 0.75)
    if log_scale: plt.xscale('log')
    if loglog: plt.xscale('log'); plt.yscale('log')
    if Savefig: plt.savefig(f'{filename}_plot.png')
    
#%%
def Subplots_21(x1,y1,x2,y2, filename='',num=1, 
                xLabel_1 = 'Frequency [Hz]', yLabel_1 = 'Voltage [V]', Title_1 = '',
                xLabel_2 = 'Frequency [Hz]', yLabel_2 = 'Voltage [V]', Title_2 = '',
                label1 = 'data1' , label2 = 'data2', 
                nRows = 2, nCols = 1,
                Savefig=True,log_scale = False,loglog = False):
    
    
    fig, axes = plt.subplots(nrows=nRows, ncols=1, gridspec_kw={'hspace': 0.10})

    x1 = x1.astype(float)
    y1 = y1.astype(float)
    x2 = x2.astype(float)
    y2 = y2.astype(float)

    
    axes[0].plot(x1, y1, label=str(label1))
    axes[0].set_xlabel(str(xLabel_1))
    axes[0].set_ylabel(str(yLabel_1))
    axes[0].legend()
    axes[0].set_title(str(Title_1))
           
    axes[1].plot(x2, y2, label=str(label2))
    axes[1].set_xlabel(str(xLabel_2))
    axes[1].set_ylabel(str(xLabel_2))
    axes[1].legend()
    axes[1].set_title(str(Title_2))

    for ax in axes:
        ax.grid(which='both',alpha = 0.75)
    if loglog: plt.xscale('log'); plt.yscale('log')    
    if log_scale: 
        plt.xscale('log')
    if log_scale or loglog: 
        plt.grid(True, which='major', color='k',linestyle='-')  # style of major grid lines
        plt.grid(True, which='minor', color='grey', linestyle='--')  # style of minor grid lines
    
    if Savefig: plt.savefig(f'{filename}_plot.png')



#%%
def Plot_yy(x,y1,y2, filename='', label='',num=1, alpha_1 = 1, alpha_2 = 1,marker = '',
            xLabel = 'Frequency [Hz]', yLabel_1 = 'PSD [dBc/Hz]', yLabel_2= 'Jitter',
            Title='', Savefig = False, log_scale = False, loglog = False):
    '''
    https://pythonforundergradengineers.com/how-to-make-y-y-plots-with-matplotlib.html
    '''

    x = x.astype(float)
    y1 = y1.astype(float)
    y2 = y2.astype(float)
    
    fig, ax1 = plt.subplots()
    if loglog: plt.xscale('log'); plt.yscale('log')    
    if log_scale or loglog: 
        plt.grid(True, which='major', color='k',linestyle='-')  # style of major grid lines
        plt.grid(True, which='minor', color='grey', linestyle='--')  # style of minor grid lines
    else:
        plt.grid(True)
    
    ax1.plot(x,y1,label=str(label),marker = marker,alpha=alpha_1)
    ax1.set_title(str(Title))
    ax1.set_xlabel(str(xLabel))
    ax1.set_ylabel(str(yLabel_1))
    if label != '': ax1.legend()

    ax2 = ax1.twinx()
    ax2.plot(x,y2,label=str(label),alpha=alpha_2)   
    ax2.set_ylabel(str(yLabel_2))
    if loglog: plt.loglog()   

    
    
    
    if Savefig: plt.savefig(f'{filename}_plot.png')
    
#%%
def Plot_xx(y, x1, x2, filename='', num=1, 
            xLabel_1='Wavelength [nm]', yLabel='PSD [dBm/nm]',
            xLabel_2='Frequency [Hz]', Label='data1', 
            Title='', Savefig=False, log_scale=False,loglog = False):
    
    y = y.astype(float)
    x1 = x1.astype(float)
    x2 = x2.astype(float)
    
    fig, ax = plt.subplots()
    ax.plot(x1, y, label=Label)
    ax.set_title(Title)
    ax.set_xlabel(xLabel_1)
    ax.set_ylabel(yLabel)
    ax.legend()
    
    ax2 = ax.twiny()
    ax2.set_xlabel(xLabel_2)
    ax2.legend()

    for ax in [ax, ax2]: ax.grid(which='both', alpha=0.75)
    if log_scale: ax.set_xscale('log') 
    if loglog: plt.xscale('log'); plt.yscale('log')
    if log_scale or loglog: 
        plt.grid(True, which='major', color='k',linestyle='-')  # style of major grid lines
        plt.grid(True, which='minor', color='grey', linestyle='--')  # style of minor grid lines
        
    if Savefig: plt.savefig(f'{filename}_plot.png')
        
    return fig, ax
#

#%%
# def Plot_xx(y,x1,x2, filename='',
#             xLabel_1 = 'Wavelength [nm]', yLabel = 'PSD [dBm/nm]',
#             xLabel_2 = 'Frequency [Hz]', 
#             Label1 = 'data1', Label2 = 'data2', 
#             Title='', Savefig = True, log_scale = False):
    
#     y = y.astype(float)
#     x1 = x1.astype(float)
#     x2 = x2.astype(float)

#     fig, axes = plt.subplots()    
#     axes[0].plot(x1, y, label=str(Label1))
#     axes[0].set_title(str(Title))
#     axes[0].set_xlabel(str(xLabel_1))
#     axes[0].set_ylabel(str(yLabel))
#     axes[0].legend()
    
#     axes[1] = axes[0].twiny()    
#     axes[1].set_xlabel(str(xLabel_2))
#     axes[1].legend()

#     for ax in axes:
#         ax.grid(which='both',alpha = 0.75)
#     if log_scale: plt.xscale('log')
#     if Savefig: plt.savefig(f'{filename}_plot.png')    