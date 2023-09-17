# -*- coding: utf-8 -*-
"""
Created on Tue May  5 08:45:52 2020

@author: ibaldoni
"""



print('Better fit with Lorentzian')

import numpy as np
from scipy.signal import find_peaks, peak_widths
import matplotlib.pyplot as plt
import pandas as pd
from scipy import optimize

def _1lorentz(t, amp,cen,wid,res_max):
        return (amp*wid**2/((t-cen)**2+wid**2))*(-1) +res_max
    
def Coupling_calc(n_med, gap,Primary_Folder, interes,No_Resonancias,orden,name_of_the_chip):
    
    name = str(name_of_the_chip)
    print('%s: Chip with %s micron gap'%(name, gap))
    
    size=(10,7)
#    c=299789452
    

    dibujitos = 'n'
    dib_ajuste = 'n'
    printing = 'n'
    variacion = 47
    valor_exagerado = .750
    rolleo = 0
#    print('Tomar hasta que alcance el valor del invento?')
    
    p=0
    
    wavelength=np.linspace(1520,1570,n_med)
    
    depth = np.zeros(len(wavelength))
    for jj in wavelength:

        p=p+1
        med=pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                        +str(Primary_Folder)+'\\'
                         +str(interes)+'\\Data_'+str(int(jj))+'_GAP_'
                         +str(gap)+'.csv')
        
        
        
#        med=pd.read_csv('C:\\Users\\ibaldoni\\Desktop\\Que_mierda_pasa_loco.csv')
        
        med=med.drop('Unnamed: 0',axis=1)
        med = med.rename(columns={"0":"transmission"})
        

        
        if len(med)> 10:
            
            
            res = med['transmission']#.rolling(rolleo).mean()
            res = res.astype(float)
        
            
#            Tiempo1 = res.index[0]*11e-6
#            Tiempo2 = res.index[-1]*11e-6
            
#            Tiempo = np.linspace(Tiempo1,Tiempo2,len(res))
            
            
#            plt.figure(p+1)
#            plt.plot(Tiempo, res)
#            
        #    'Normalize and make it positive'
#            res = 1-res/np.min(res)

            res = res/np.max(res)            
            
            
            maximo = np.max(res)
            minimo = np.min(res)
            
            #Si hay más de uno toma el valor del menor indice
            maximo_ind = np.min(np.where(res==maximo))
            
            minimo_ind = np.min(np.where(res==minimo))
            avg = np.mean(res)
            invento = (maximo+avg)*0.5
            
            
                
            if minimo_ind - variacion < rolleo:
                minimo_ind = variacion + rolleo + 1
                
            
            
            
            
    
            
            wl = wavelength[p-1]
            
            if np.abs(maximo - minimo) > No_Resonancias:   
                
                t = res.index[minimo_ind-variacion:minimo_ind+variacion]
                
                for i in range(0,len(t)):
                    if t[i] == minimo_ind:
                        weight = i
                        
                res_max = res[t[0]]
                
                sigma =np.ones(len(t))
                sigma[weight] = 1
                
                
    
    # No funciona bonito            invento = 0.5*(res[minimo_ind-15] + res[minimo_ind+15])
                
                depth[p-1] = np.round(invento - minimo,4)
                inicial_values = [depth[p-1],minimo_ind,2,res_max]
                popt_1lorentz, pcov_1lorentz = optimize.curve_fit(_1lorentz, t, res[t],p0=inicial_values, 
#                                                                  bounds = (0, [1.01*depth[p-1],np.inf,np.inf,np.inf]), 
                                                                  maxfev=50000,
                                                                  sigma = sigma)
#                                                                  ,absolute_sigma=True)
                
#                1.5*depth[p-1]
     
                transmision = np.abs(_1lorentz(popt_1lorentz[1], *popt_1lorentz) -  _1lorentz(res.index[0], *popt_1lorentz))
                if dib_ajuste == 'y':
                    plt.figure(p)
                    x_plot_fit = np.linspace(t[0],t[-1],int(len(t)*5))
                    lorentz_peak_1 = _1lorentz(t, *popt_1lorentz)
                    plt.plot(t, lorentz_peak_1, "g")
                    plt.plot(t,res[t],'*r')
                    
                    
                    
                depth[p-1] = popt_1lorentz[0]
                
                depth[p-1] = transmision
                
                if depth[p-1] < 0 or depth[p-1]>valor_exagerado:
                    depth[p-1] = 0
                
                if dibujitos == 'y' and jj%1 == 0:#depth[p-1]<0:
                    plt.figure(p)
                    plt.title('Wavelength = %s nm'%jj)
                    plt.plot(res,'o-')
                #    plt.plot(t,res)
                    plt.hlines(avg,res.index[0],res.index[-1],'g')
                    plt.hlines(invento,res.index[0],res.index[-1],'m')
                    plt.plot(t,res[t],'*y')
                    plt.plot(minimo_ind,minimo,'rx')
                    plt.plot(maximo_ind,maximo,'rx')
                    
                    x_plot_fit = np.linspace(res.index[0],res.index[-1],int(len(res)*5))
                    lorentz_peak_1 = _1lorentz(x_plot_fit, *popt_1lorentz)
                    plt.plot(x_plot_fit, lorentz_peak_1, "r")
#                    plt.plot(t,res[t],'*b')
            
            else:
                depth[p-1] = 0 
                print('No resonances on sight at %s nm' % wl )
            
            if depth[p-1] < No_Resonancias:
                depth[p-1] = 0
            
            if printing == 'y':
                print('Wavelength = %s nm; depth = %s' % (wl, depth[p-1]))
        
#        if jj == wavelength[1]:
#            break
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
        print('Maxima in %s' % slope)

    xx = np.linspace(wl_res[0],wl_res[-1],100)   
    plt.figure(p+1,figsize = size)
    plt.plot(wl_res,resonances,'-o', label = 'Data '+str(name))

    plt.plot(xx,curva(xx),'r',label = 'Chip = '+str(name)+'\n'+str(text_leg)+' = %s' % np.round(slope,6))    

    for i, txt in enumerate(wl_res):
        print(wl_res[i])
        plt.annotate(txt, (wl_res[i], resonances[i]))
#    
    
    plt.xlabel('Wavelength (nm)',fontsize = 17)
    plt.ylabel('Resonance transmission (a.u)',fontsize = 17)
    plt.legend(fontsize = 15)
    plt.tick_params(labelsize=15)
    plt.title('Coupling Gap = %s microns ' % gap,fontsize = 20)
    
    # plt.savefig(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
    #             +str(Primary_Folder)+'\\'
    #             +str(interes)+'\\Transm_vs_lambda_LorentzFit_GAP_'
    #             +str(gap)+'.png')
    
    
    return resonances, wl_res, slope


#resonances, wl_res, slope = Coupling_calc(51, 0.70,'Chip_Analysis','20200430_Gap_070_v2',0.045,1,'C10')
#plt.show()
#plt.close()
#resonances, wl_res, slope = Coupling_calc(51, 0.65,'Chip_Analysis','20200430_Gap_065_v2',0.025,1,'B11_1')
#plt.show()
#plt.close()
#resonances, wl_res, slope = Coupling_calc(51, 0.60,'Chip_Analysis','20200504_Gap_060',0.042,2,'D10')
#plt.show()
#plt.close()
#resonances, wl_res, slope = Coupling_calc(51, 0.55,'Chip_Analysis','20200508_Gap_055_0.1Hz_v2',0.000,1,'B11_2')
#resonances, wl_res, slope = Coupling_calc(51, 0.60,'Chip_Analysis','20200511_Gap_06_0.1Hz_C2_v2',0.000,2,'C2')

#resonances, wl_res, slope = Coupling_calc(51, 0.60,'20200511_Looking_for_better_Q_factor',
#                                          '20200511_Gap_06_0.1Hz_C2_v2',0.01,2,'C2')
#
#resonances, wl_res, slope = Coupling_calc(51, 0.60,'20200511_Looking_for_better_Q_factor',
#                                          '20200511_Gap_06_0.1Hz_C2_v3',0.01,2,'C2')

#resonances, wl_res, slope = Coupling_calc(51, 0.60,'Chip_Analysis','20200512_Gap_06_0.1Hz_D2',0.0,2,'D2')

#resonances, wl_res, slope = Coupling_calc(51, 0.55,'Chip_Analysis','20200514_Gap_055_B7',0.5,1,'B7')
#resonances, wl_res, slope = Coupling_calc(51, 0.55,'Chip_Analysis','20200515_Gap_055_B7_v2',0.5,1,'B7')
#resonances, wl_res, slope = Coupling_calc(51, 0.55,'Chip_Analysis','20200515_Gap_055_B7_v3',0.5,1,'B7')
#resonances, wl_res, slope = Coupling_calc(51, 0.55,'Chip_Analysis','20200518_Gap_055_B7_v4',0.35,2,'B7')

Primary_Folder = '20200511_Looking_for_better_Q_factor'
#resonances, wl_res, slope = Coupling_calc(51, 0.6,Primary_Folder,'20200518_Gap_06_C10',0.25,1,'D10')


resonances, wl_res, slope = Coupling_calc(51, 0.6,Primary_Folder,'20200518_Gap_06_C10',0.25,1,'C10')
resonances, wl_res, slope = Coupling_calc(51, 0.6,Primary_Folder,'20200518_Gap_06_C6',0.25,1,'C6')
resonances, wl_res, slope = Coupling_calc(51, 0.6,Primary_Folder,'20200518_Gap_06_D6',0.25,1,'D6')
resonances, wl_res, slope = Coupling_calc(51, 0.6,Primary_Folder,'20200518_Gap_06_D9',0.25,1,'D9')












