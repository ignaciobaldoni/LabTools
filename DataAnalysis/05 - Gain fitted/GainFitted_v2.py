# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 22:43:48 2022

@author: ibaldoni
"""

import numpy as np

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def Gain(x,gss,P_sat):
    return gss/(1+(x/P_sat))


size_fig= (8,6) 

input_seed = np.array([0.560,0.250,0.1,0.050,0.025,0.010,0.005])*7.591040462427746

P       = np.linspace(0,input_seed[0],100)

powers = [18,46,74]

for i in powers:
    if i == powers[0]:
        output_meas = np.array([4.52268582e+00, 2.45545985e+00, 1.17998800e+00,
                                6.57609856e-01, 3.46142429e-01, 1.47469295e-01, 7.40690842e-02])

        output_sim = np.array([4.14,2.32,1.11,0.598,0.312,0.128,0.0648])
        
        
    elif i == powers[1]:
        output_meas = np.array([5.87377863e+00, 3.17182253e+00, 1.49217353e+00,
                                7.98282810e-01, 4.19509078e-01, 1.74190704e-01, 8.50332732e-02])
        
        output_sim = np.array([5.91,3.17,1.43,0.747,0.383,0.156,0.078])
        
        
    elif i == powers[2]:
        
        output_meas = np.array([6.66511954e+00, 3.58413219e+00, 1.62249368e+00,
                                8.45923621e-01, 4.46431341e-01, 1.79269984e-01, 9.15854778e-02])
        
        #output_sim = np.array([7.31,3.72,1.6,0.824,0.418,0.169,0.0846])
        output_sim = np.array([6.94,3.58,1.56,0.805,0.410,0.166,0.083])



    Y = 10*np.log10(output_meas/input_seed)
    sigma = np.ones(len(input_seed))
    plt.figure(figsize=size_fig)
    plt.plot(input_seed,Y,'o-',label='Measurement')
    popt, pcov = curve_fit(Gain, input_seed, Y,p0=[2.3,1],sigma=sigma)
    plt.plot(P, Gain(P, *popt), '--',
             label='fit: gss=%5.3f, P_sat=%5.3f' % tuple(popt))
    plt.legend()
        
    Z = 10*np.log10(output_sim/input_seed)
    
    plt.plot(input_seed,Z,'o-',label='Simulation')
    plt.title('Pump Power = '+str(i)+' mW', fontsize=17)
    # plt.legend(fontsize=17)
    plt.xlabel("seed [mW]", fontsize=17)
    plt.ylabel("Gain [dB]", fontsize=17)
    plt.tick_params(labelsize=17)
    plt.grid()
    #plt.ylim([-0.5,4])

    sigma = np.ones(len(input_seed)); # sigma[0:4] = 0.25
    
    popt, pcov = curve_fit(Gain, input_seed, Z,p0=[2.3,1],sigma=sigma)
    plt.plot(P, Gain(P, *popt), '--',
             label='fit: gss=%5.3f, P_sat=%5.3f' % tuple(popt))
    plt.legend()

