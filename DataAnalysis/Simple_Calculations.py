# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 11:49:48 2021

@author: ibaldoni
"""
import numpy as np
import matplotlib.pyplot as plt

L_f =  .600 
L_pm1 =  2.35 
L_pm2=  .350 
L_comp= .435


D_pm = 17.5
D_compressor = -100
D_gain = -17.5



result = L_f*D_gain + D_pm*(L_pm1+L_pm2) + D_compressor*L_comp
print(result)

print((L_f*D_gain + D_pm*(L_pm1+L_pm2))/-D_compressor)

GVD1 = -25509e-30
tau0 = 100e-15

GDD1 = L_pm1 * GVD1
tau_b = tau0*np.sqrt(1+(4*np.log(2)*GDD1/(tau0**2))**2)
print(tau_b*1e12)

# Second calculation
tau_ap = 4*np.log(2)*GDD1/tau0
print(tau_ap*1e12)


GVD2 = 125509e-30

GDD2 = L_f * GVD2
tau_c = tau_b*np.sqrt(1+(4*np.log(2)*GDD2/(tau_b**2))**2)
print(tau_c*1e12)



peak = [1.45,5.26,16.01,35.49]
conc = [450,950,2000,4400]

plt.plot(peak, conc,'o-')

m,b = np.polyfit(peak, conc, 1)
print(m,b)