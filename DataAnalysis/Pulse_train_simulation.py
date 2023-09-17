# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 08:52:03 2021

@author: ibaldoni
"""

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
t = np.linspace(0, 50, 2 * 10000, endpoint=False)

print('For chirped pulse: https://www.brown.edu/research/labs/mittleman/sites/brown.edu.research.labs.mittleman/files/uploads/lecture6_0.pdf')
rep = 10
bandwidth = 1
center = bandwidth*10
chirp = 2*t**2/7
pulse = np.exp(-(t-center)**2/bandwidth)*np.sin(4*chirp*2*np.pi)+np.exp(-(t-center-rep)**2/bandwidth)*np.sin(4*chirp*2*np.pi) +      np.exp(-(t-center-2*rep)**2/bandwidth)*np.sin(4*chirp*2*np.pi)

#i, q, e = signal.gausspulse(t, fc=5, retquad=True, retenv=True)
#i = signal.gausspulse(t, fc=5, retquad=False, retenv=False) 
#i, q = signal.gausspulse(t, fc=5, retquad=False, retenv=True)
plt.plot(t, pulse)

#imp = signal.unit_impulse(200, [10,40,50])


from scipy.fftpack import fft, fftfreq
# Number of sample points
N = len(t)
# sample spacing
T = 1.0 / 800.0
x = t#np.linspace(0.0, N*T, N, endpoint=False)
y = pulse#np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)
yf = fft(y)
xf = fftfreq(N, T)[:N//2]

plt.figure()
plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]),'.')
plt.grid()
plt.show()

#n = np.arange(0,25+1) # Get 0 through 25 harmonics
#tau = 0.125; f0 = 1; A = 1;
#Xn = A*tau*f0*sinc(n*f0*tau)*exp(-1j*2*pi*n*f0*tau/2)
## Xn = -Xn # Convert the coefficients from xa(t) t0 xb(t)
## Xn[0] += 1
#figure(figsize=(6,2))
#f = n # Assume a fundamental frequency of 1 Hz so f = n
#ss.line_spectra(f,Xn,mode='mag',sides=2,fsize=(6,2))
#xlim([-25,25]);
##ylim([-50,10])
#figure(figsize=(6,2))
#ss.line_spectra(f,Xn,mode='phase',fsize=(6,2))
#xlim([-25,25]);