# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 17:28:24 2020

@author: ibaldoni
"""

print('Only imports')

import numpy as np
from scipy.signal import find_peaks, peak_widths
import matplotlib.pyplot as plt
import pandas as pd

def Coupling_calc(n_med, gap,interes,No_Resonancias,orden,name_of_the_chip):
    
    name = str(name_of_the_chip)
    print('%s: Chip with %s micron gap'%(name, gap))
    

    #from numpy import trapz
    #from scipy import integrate
    #
    #from scipy.misc import electrocardiogram
    #from scipy.signal import find_peaks, argrelextrema
    #from scipy.optimize import curve_fit
    #from scipy import interpolate
    
    size=(10,7)
    c=299789452
    
    general = 'C:\\Users\\Administrator.MenloPC208\\Desktop\\Chip_analysis\\'
    #'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
    

    dibujitos = 'n'
    p=0
    
    wavelength=np.linspace(1520,1570,n_med)
    depth = np.zeros(len(wavelength))
    for jj in wavelength:
        print(jj)
        p=p+1
        med=pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\Chip_analysis\\'
                         +str(interes)+'\\Data_'+str(int(jj))+'_GAP_'
                         +str(gap)+'.csv')
        
        med=med.drop('Unnamed: 0',axis=1)
        med = med.rename(columns={"0":"transmission"})
        
        if len(med)> 10:
    
        
        #    t=med['x-axis']
        #    t = t.astype(float)
            
            res = med['transmission']#.rolling(10).mean()
            res = res.astype(float)
            
        #    'Normalize'
            res = 1-res/np.min(res)
            
    #        indice = res.index
        
            
            maximo = np.max(res)
            minimo = np.min(res)
            
            maximo_ind = np.min(np.where(res==maximo))
            minimo_ind = np.min(np.where(res==minimo))
            avg = np.mean(res)
            invento = (maximo+avg)*0.5
            
            
            
    
            
            wl = wavelength[p-1]
            
            if np.abs(maximo - minimo) > No_Resonancias:   
    
    # No funciona bonito            invento = 0.5*(res[minimo_ind-15] + res[minimo_ind+15])
                
                depth[p-1] = np.round(invento - minimo,4)
                if dibujitos == 'y':
                    plt.figure(p)
                    plt.title('Wavelength = %s nm'%jj)
                    plt.plot(res,'o-')
                #    plt.plot(t,res)
                    plt.hlines(avg,res.index[0],res.index[-1],'g')
                    plt.hlines(invento,res.index[0],res.index[-1],'m')
                    plt.plot(minimo_ind,minimo,'rx')
                    plt.plot(maximo_ind,maximo,'rx')
            
            else:
                depth[p-1] = 0
                print('No resonances on sight')
            
            print('Wavelength = %s nm; depth = %s' % (wl, depth[p-1]))
        
#### En caso de que quiera sacar algun outlier    
#    for i in range(0,len(depth)):
#        if depth[i] > 5*np.mean(depth):
#            depth[i] = 0
            
    res_pos = np.where(depth!=0)
    resonances = depth[res_pos]
    wl_res = wavelength[res_pos]
    
    z = np.polyfit(wl_res, resonances, orden)
    
    curva = np.poly1d(z)
    curva(wl_res)
    
    if orden == 1:
        slope = z[0]
        text_leg = 'Slope'
        print('Linear fit: %s x + %s ' % (z[0],z[1]))
    else:
        slope=-z[1]/(2*z[0])
        text_leg = 'Local max'
        print('Cuadratic fit: %s x2 + %s x + %s ' % (z[0],z[1],z[2]))

    xx = np.linspace(wl_res[0],wl_res[-1],100)   
    plt.figure(p+1,figsize = size)
    plt.plot(wl_res,resonances,'o', label = 'Data')

    plt.plot(xx,curva(xx),'r',label = str(text_leg)+' = %s' % np.round(slope,6))
    
    plt.xlabel('Wavelength (nm)',fontsize = 17)
    plt.ylabel('Resonance transmission (a.u)',fontsize = 17)
    plt.legend(fontsize = 15)
    plt.tick_params(labelsize=15)
    plt.title('Coupling Gap = %s microns ' % gap,fontsize = 20)
    
    # plt.savefig(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\Chip_analysis\\'
    #             +str(interes)+'\\Transmission_vs_lambda_GAP_'
    #             +str(gap)+'.png')
    
    
    return resonances, wl_res, slope


#resonances, wl_res, slope = Coupling_calc(51, 0.70,'20200430_Gap_070_v2',0.045,1)
#plt.close()
#resonances, wl_res, slope = Coupling_calc(51, 0.65,'20200430_Gap_065_v2',0.025,1)
#plt.close()
#resonances, wl_res, slope = Coupling_calc(51, 0.60,'20200504_Gap_060',0.0505,2,'D11')
#resonances, wl_res, slope = Coupling_calc(51, 0.55,'20200505_Gap_055',0.04,1)

#resonances, wl_res, slope = Coupling_calc(51, 0.55,'20200506_Gap_055_v6_NewPD_change_ppc',0.01,1)
#resonances, wl_res, slope = Coupling_calc(51, 0.55,'20200507_Gap_055_change_resolution_DAQ_5',0.0,1)

#resonances, wl_res, slope = Coupling_calc(51, 0.60,'20200511_Gap_06_0.1Hz_C2',0.000,2,'C2')

#resonances, wl_res, slope = Coupling_calc(51, 0.60,'20200511_Gap_06_0.1Hz_C2_v2',0.000,2,'C2')

#resonances, wl_res, slope = Coupling_calc(51, 0.60,'20200512_Gap_06_0.1Hz_D2',0.02,2,'D2')

resonances, wl_res, slope = Coupling_calc(51, 0.55,'20200514_Gap_055_B7',0.0,2,'B7')    