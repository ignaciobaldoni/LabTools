# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 09:48:52 2022

@author: ibaldoni
"""
import numpy as np
import matplotlib.pyplot as plt

s_a_Er = 6.72e-25 #{state absorption}
s_e_Er = 6.55e-25 #{state emission}

planck = 6.62607004e-34
frequency = 194e12
radio = 5e-6
mfa = np.pi*radio**2

E_sat = mfa*planck*frequency/(s_a_Er+s_e_Er)
print(E_sat)


