# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 19:11:07 2013

@author: Administrator
"""

display_start_values_only = False
use_triple_lorentz = True
normalize = False

reprate_MHz = 20000.
modFreq_MHz = 100.

center = 1000.
dist = 500.
width= 38.
peak = 29.
sband= 0.03

#import modules
import tkinter as Tkinter
import tkinter.filedialog as tkFileDialog
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

def lorentz(x, a, x0, g):
    return a*g/((x-x0)*(x-x0)+g*g)

def triple_lorentz(x, a0, a1, a2, x00, x01, x02, g0, g1, g2, offs):
    return offs + lorentz(x, a0, x00, g0) + lorentz(x, a1, x01, g1) + lorentz(x, a2, x02, g2)

#read in an scope file and get the data
root = Tkinter.Tk()
root.withdraw()
filename = tkFileDialog.askopenfilename(parent=root, title='open an oscilloscope trace')
#filename = "C:/Dokumente und Einstellungen/Administrator/Desktop/WAVE/CAV_3191.CSV"
sample_number=[]
trace=[]
f = open(filename,'r')
i=-20
for line in f.readlines():
    if i>0:
        sample_number.append(float(i))        
        trace.append(float(line.strip().split(',')[1]))
    i+=1
# change scaling
for i in range(len(sample_number)):
    sample_number[i] -= 0000.
    trace[i] -= 0.012
if normalize:
    m = max(trace)
    trace = [trace[i]/float(m) for i in range(len(trace))]


x=np.array(sample_number)
y=np.array(trace)


if use_triple_lorentz:
    start_val=[peak*sband,peak, peak*sband, center-dist, center, center+dist, width, width, width, 0.0]
    if display_start_values_only:
        ev = start_val
    else:
        ev, cov = curve_fit(triple_lorentz, x, y, start_val)
    # generate fit
    fit=[]
    for i in sample_number:
        fit.append(triple_lorentz(i, ev[0], ev[1], ev[2], ev[3], ev[4], ev[5], ev[6], ev[7], ev[8], ev[9]))
else:
    start_val=[1.0, center, 100.]
    if display_start_values_only:
        ev=start_val
    else:
        ev, cov = curve_fit(lorentz, x, y, start_val)
    # generate fit
    fit=[]
    for i in sample_number:
        fit.append(lorentz(i, ev[0], ev[1], ev[2]))
        
FWHM=0.
if use_triple_lorentz:
    FWHM=2*ev[7]
else:
    FWHM=2*ev[2]
fit_label="fit:\nFWHM = "+str(round(FWHM,2))
if use_triple_lorentz:
    fit_label+="\ndist = "+str(round(ev[5]-ev[3],2))

plt.plot(sample_number,trace, 'b-', linewidth=1.0, label="scope data")
plt.plot(sample_number, fit, 'r-', linewidth=1.5, label = fit_label)
plt.xlabel("sample number")
plt.ylabel("transmitted power [a.u.]")
plt.title("Finesse: "+ str( round(reprate_MHz/(FWHM/((ev[5]-ev[3])/(modFreq_MHz*2))),0) ))
#plt.xlim(0000,6800)
#plt.ylim(-0.1,1.2)
plt.legend(loc=2)
plt.show()