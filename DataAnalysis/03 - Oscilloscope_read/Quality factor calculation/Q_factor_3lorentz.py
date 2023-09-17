# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 10:35:51 2020

@author: ibaldoni
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
from scipy.signal import find_peaks, peak_widths



wl = 1550.142 *1e-9
Quality_factor = []
sideband = 250 # MHz
p   = 0
zz  = 0
dibujitos = 'no'
for jj in range(29,43):
    zz=zz+1
    

    print('-----------------------------------------------------------------')
    general = '\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
    interes = '20200324_Chip_alignment_setup__Q_factor_calculation'
    
    
    med=pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                         +str(interes)+'\\scope_'+str(jj)+'.csv')
    
    roll = 50 
    med=med.drop(med.index[0])    
    
    finito = int(len(med)*.25)
    t=med['x-axis']
    t = t[finito:len(med)-finito].astype(float)
    res=med['1'].rolling(roll).mean()
    res=res[finito:len(med)-finito].astype(float)
    res=res.div(max(res))
    #t = (t-np.min(t))#.mul(10000)
    
    #plt.plot(t,res)   
    
#    amp1=3e-01  cen1=3e-06   wid1=3e-06 amp2=4e-01  cen2=3e-05  wid2=2e-05  amp3=4e-01  cen3=-3e-05   wid3=1.5e-05

    
    inicial_values = [3e-01,3e-06,3e-06,4e-01 ,3e-05,2e-05,4e-01,-3e-05,2e-05]
    
    res_max = 1.01*np.mean(res)
    
    for i in range(1,len(res)):
        if res.iloc[i]>1.01*res_max:
            if i == 1:
                res.iloc[i]=res_max
            else:
                res.iloc[i]=res.iloc[i-1]
    
    
    def _3lorentz(t, amp1, cen1, wid1, amp2,cen2,wid2, amp3,cen3,wid3):
        return ((amp1*wid1**2/((t-cen1)**2+wid1**2)) +\
                (amp2*wid2**2/((t-cen2)**2+wid2**2)) +\
                (amp3*wid3**2/((t-cen3)**2+wid3**2)))*(-1) +res_max
                    
    
    def _1lorentz(t, amp,cen,wid):
        return (amp*wid**2/((t-cen)**2+wid**2))*(-1) +res_max
    
    
    #popt_lorentz, pcov_lorentz = optimize.curve_fit(_1lorentz, t, res, p0=[amp1, cen1, wid1],maxfev=1000)
    #perr_lorentz = np.sqrt(np.diag(pcov_lorentz))
                
    popt_3lorentz, pcov_3lorentz = optimize.curve_fit(_3lorentz, t, res, p0=inicial_values,maxfev=50000)
    #[amp1, cen1, wid1, amp2,cen2,wid2, amp3,cen3,wid3],maxfev=50000)
    perr_3lorentz = np.sqrt(np.diag(pcov_3lorentz))
    
    
    triple_lorentz = _3lorentz(t, *popt_3lorentz)
    
    sample_number=[]
    trace=[]
    for ii in range(1,len(triple_lorentz)-1):
        before  =   triple_lorentz.iloc[ii-1] 
        middle  =   triple_lorentz.iloc[ii]
        after   =   triple_lorentz.iloc[ii+1]
        
        if middle < before and middle < after:
            sample_number.append(int(ii-1+finito))       
    
    if len(sample_number) < 3:
        print('I have not found the three dips')
        p=p+1
    else:        
    # Interpolation for getting the value of the frequency
        fp = [0,sideband*1e6,2*sideband*1e6]
        xp = t[sample_number]
        z = np.polyfit(xp, fp, 1)
        
        t0 = 2*popt_3lorentz[2]
        
        FHWM = z[0]*t0 # In Hz
        
#        print('FHWM is %s MHz' % (FHWM*1E-6))
    
        c = 299792458   # Speed of light
        vo = c/wl
        
        Q = vo/(FHWM)             
        Quality_factor.append(Q)
        
        kappa = 2*np.pi*FHWM
        
#        print(kappa*1e-6)
        
        print('FHWM is %s MHz and Q factor is %s million' % (round(FHWM*1E-6, 2), round(Q*1e-6,2)))
        

    
    if dibujitos == 'y':
        pars_1 = popt_3lorentz[0:3]
        pars_2 = popt_3lorentz[3:6]
        pars_3 = popt_3lorentz[6:9]
        lorentz_peak_1 = _1lorentz(t, *pars_1)
        lorentz_peak_2 = _1lorentz(t, *pars_2)
        lorentz_peak_3 = _1lorentz(t, *pars_3)
        
        plt.figure(1)
        plt.plot(t, res, "k", linewidth=0.7)
        
        plt.plot(t, lorentz_peak_1, "g")
        plt.fill_between(t, lorentz_peak_1.min(), lorentz_peak_1, facecolor="green", alpha=0.15)
          
        plt.plot(t, lorentz_peak_2, "m")
        plt.fill_between(t, lorentz_peak_2.min(), lorentz_peak_2, facecolor="magenta", alpha=0.15)  
        
        plt.plot(t, lorentz_peak_3, "b")
        plt.fill_between(t, lorentz_peak_3.min(), lorentz_peak_3, facecolor="blue", alpha=0.15)  
        plt.show()
        plt.close()
    
    
    residual_3lorentz = res - (_3lorentz(t, *popt_3lorentz))       
    
Q_avg = np.mean(Q)

print('N° data analised: %s // and N° lost data: %s ' % (zz,p))   

print('Average Q factor of this chip: %s million'% np.round(Q_avg*1E-6,2))
