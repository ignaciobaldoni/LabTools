# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 19:06:40 2022

@author: ibaldoni
"""

import numpy as np

c = 299789452.0

wl = 1542e-9                #[m]
repetition_rate = 12.13e9   #[Hz]
freq = c/wl                 #[Hz] 

def d_wl(repetition_rate,wl): 
    return repetition_rate*wl**2/c

R = wl/d_wl(repetition_rate,wl)         # from wavelengths

# R = freq/repetition_rate                # from frequencies

print('R:',R)





