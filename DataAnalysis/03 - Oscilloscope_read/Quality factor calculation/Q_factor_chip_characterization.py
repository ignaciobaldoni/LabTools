# -*- coding: utf-8 -*-
"""
Created on Mon May 11 17:57:51 2020

@author: ibaldoni
"""


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
from scipy.signal import find_peaks, peak_widths

def Q_factor(name, Primary_Folder, interes, sideband, n_med, gap, variacion,
             seleccion_de_picos, distancia_sidebands,size_resonance,n_plots):
    
    
    name_of_the_chip = str(name)
    Quality_factor = []
    FHWM_ = []
    wavelength_ = []

    p   = 0
    zz  = 0
    dibujitos_ajuste = 'y'
    dibujitos_ajuste_bueno = 'y'
    ajuste = 'y'
    ajuste_malo = 'n'
    no_ajuste = 'n'
    
#    gap = 0.6
#    Primary_Folder = '20200511_Looking_for_better_Q_factor'
    
#    n_med = 51
#    n_med = 
    wavelength=np.linspace(1520,1570,n_med)
    
#    wavelength[6] = wavelength[7]
#    wavelength[10] = wavelength[22]
#    wavelength = [wavelength[6],wavelength[9]]
    


    rolleo = 0
    

    for jj in wavelength:
        
        
        wl = jj *1e-9
            
        print('Studying wavelength %s nm' % jj)
        zz=zz+1
        
#        general = '\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
#        interes = '20200511_Gap_06_Q_factor_C3'
        
        
        med=pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                             +str(Primary_Folder)+'\\'
                             +str(interes)+'\\Data_'+str(int(jj))+'_GAP_'
                             +str(gap)+'.csv')
        
    
        med=med.drop(med.index[0])    
        med=med.drop('Unnamed: 0',axis=1)
        med = med.rename(columns={"0":"transmission"})
        
        res = med['transmission']
        res = res.astype(float)
        
        
        t = res.index.values
        t0 = t[0]


    
    
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
            


        
    
            
        t = res.index[minimo_ind-variacion:minimo_ind+variacion]
        t = t.values
                    
#        plt.figure(zz)            
#        plt.plot(t,res[t],'r')   
        
#        res_max = res[t[0]]
        
        x_i = t[0]
        x_f = t[-1]
        y_i = res[x_i]
        y_f = res[x_f]
               
        pendiente = (y_f - y_i)/(x_f-x_i)
        ordenada = (y_f-pendiente*x_f)
        lineal = pendiente*t + ordenada  
        
##        Evito que se haga negativo
        res[t] = 1+res[t]-lineal
        
#        plt.plot(t, res[t])
        res_max = res[t[0]]
        
         
    #    
    ##    amp1=3e-01  cen1=3e-06   wid1=3e-06 amp2=4e-01  cen2=3e-05  wid2=2e-05  amp3=4e-01  cen3=-3e-05   wid3=1.5e-05
    #
    #    
#        inicial_values = [0.04,minimo_ind,20,0.01 ,minimo_ind-distancia_sidebands,
#                          5,0.01,minimo_ind+distancia_sidebands,5]
        
        inicial_values = [0.6,minimo_ind,150,
                          0.1,minimo_ind-distancia_sidebands,50,
                          0.1,minimo_ind+distancia_sidebands,50]
        
        inicial_values = [0.5,minimo_ind,7,
                          0.1,minimo_ind-distancia_sidebands,5,
                          0.1,minimo_ind+distancia_sidebands,5]
    
    #    res_max = 1.01*np.mean(res)
    #    
    #    for i in range(1,len(res)):
    #        if res.iloc[i]>1.01*res_max:
    #            if i == 1:
    #                res.iloc[i]=res_max
    #            else:
    #                res.iloc[i]=res.iloc[i-1]
    #    
    #    
        def _3lorentz(t, amp1, cen1, wid1, amp2,cen2,wid2, amp3,cen3,wid3):
            return ((amp1*wid1**2/((t-cen1)**2+wid1**2)) +\
                    (amp2*wid2**2/((t-cen2)**2+wid2**2)) +\
                    (amp3*wid3**2/((t-cen3)**2+wid3**2)))*(-1) +res_max
                        
        
        def _1lorentz(t, amp,cen,wid):
            return (amp*wid**2/((t-cen)**2+wid**2))*(-1) +res_max
        
        if ajuste == 'y':
            #popt_lorentz, pcov_lorentz = optimize.curve_fit(_1lorentz, t, res, p0=[amp1, cen1, wid1],maxfev=1000)
            #perr_lorentz = np.sqrt(np.diag(pcov_lorentz))
                        
            popt_3lorentz, pcov_3lorentz = optimize.curve_fit(_3lorentz, t, res[t], p0=inicial_values,maxfev=50000)
            #[amp1, cen1, wid1, amp2,cen2,wid2, amp3,cen3,wid3],maxfev=50000)
            perr_3lorentz = np.sqrt(np.diag(pcov_3lorentz))
            
            amplitudes = [popt_3lorentz[0],popt_3lorentz[3],popt_3lorentz[6]]
            
            
            
            
            triple_lorentz = _3lorentz(t, *popt_3lorentz)
            
            
            
            sample_number=[]
            trace=[]
            for ii in range(1,len(triple_lorentz)-1):
                before  =   triple_lorentz[ii-1] 
                middle  =   triple_lorentz[ii]
                after   =   triple_lorentz[ii+1]
                
                if middle < before and middle < after:
                    sample_number.append(int(ii-1))   
                    
        
            print('Ojo, cambie el numero de picos que tiene que encontrar la cosa')
            
            if (len(sample_number) < 2 or any(n < 0 for n in amplitudes)) or res[minimo_ind]>=0.85:
                print('I have not found the three dips')
                
                
            
            else:  
                # Chequeo que encuentre buenos picos y no unos de mierda por culpa del ajuste.. 
                if True:
#                    np.abs(_3lorentz(t[sample_number[0]],*popt_3lorentz) -
#                          _3lorentz(t[sample_number[2]],*popt_3lorentz)) <= seleccion_de_picos*np.mean(
#                                  [_3lorentz(t[sample_number[0]],*popt_3lorentz),_3lorentz(t[sample_number[2]],*popt_3lorentz)]
#                                  ) and (size_resonance*_3lorentz(t[sample_number[1]],*popt_3lorentz) < _3lorentz(t[sample_number[0]],*popt_3lorentz)):
#    #                print(t[sample_number])
                    
                # Interpolation for getting the value of the frequency
#                    fp = [0,sideband*1e6,2*sideband*1e6]
#                    xp = t[sample_number]
#                    
##                    print (fp,xp)
#                    z = np.polyfit(xp, fp, 1)
                    
#                    Cambio enfoque. Tomo solo dos puntos.
                    fp = [0,sideband*1e6]
                    xp = [t[sample_number[0]],t[sample_number[1]]]
                    
#                    print (fp,xp)
                    z = np.polyfit(xp, fp, 1)
                    
                    

                    
                    t0 = 2*popt_3lorentz[2]
                    
                    print(popt_3lorentz)
                    print(t0)
                    
                    FHWM = z[0]*t0 # In Hz
                    
            #        print('FHWM is %s MHz' % (FHWM*1E-6))
                
                    c = 299792458   # Speed of light
                    vo = c/wl
                    
                    FHWM = np.abs(FHWM)
                    Q = vo/FHWM   
                    
                    
#                    linea= z[0]*fp+z[1]
                    
#                    print(Q)
                    plt.figure(3)

#                    prueba = np.linspace(0,1000e6,200000)
#                    plt.plot(xp,fp,'o', xp, z[0]*xp+z[1],'r')                    
                    
                    if ((Q > 0) and (Q*1e-6<100)):
                        Quality_factor.append(Q)
                        
                        FHWM_.append(FHWM)
                        
                        wavelength_.append(wl)
                        
                        p=p+1
                    
                        kappa = 2*np.pi*FHWM
                    
                #        print(kappa*1e-6)
                        
                        print('FHWM is %s MHz and Q factor is %s million' % (round(FHWM*1E-6, 2), round(Q*1e-6,2)))
                        if dibujitos_ajuste_bueno == 'y':
                            plt.figure(zz)
                            plt.plot(t,res[t],color="green", linewidth=0.6)
                            t_plot = np.linspace(t[0],t[-1],1000)
                            plt.plot(t_plot,_3lorentz(t_plot,*popt_3lorentz))
                            centros = [popt_3lorentz[1],
                                       popt_3lorentz[4],
                                       popt_3lorentz[7]]
                            plt.plot(centros,_3lorentz(popt_3lorentz[1:8:3],*popt_3lorentz),'r*')
                            plt.plot(minimo_ind,res[minimo_ind],'m*')
                            texto = 'Chip = %s \nWavelength = %s nm \nFHWM = %s MHz \nQ = %s million' % (str(name_of_the_chip),
                                                                                    int(jj),
                                                                                      round(FHWM*1E-6, 2), round(Q*1e-6,2))
                            plt.text(t[0],0.66*np.mean(res[t]),str(texto))
                else:
                    print('Hace un buen ajuste, encuentra picos pero no son buenos')
                    if ajuste_malo == 'y':
                        plt.figure(zz)
                        plt.plot(t,res[t],color="green", linewidth=0.6)
                        plt.plot(t,_3lorentz(t,*popt_3lorentz))
                        
                
        
            
            if dibujitos_ajuste == 'y':
                pars_1 = popt_3lorentz[0:3]
                pars_2 = popt_3lorentz[3:6]
                pars_3 = popt_3lorentz[6:9]
                lorentz_peak_1 = _1lorentz(t, *pars_1)
                lorentz_peak_2 = _1lorentz(t, *pars_2)
                lorentz_peak_3 = _1lorentz(t, *pars_3)
                
                plt.figure(1)
                plt.plot(t, res[t], "k", linewidth=0.7)
                
                plt.plot(t, lorentz_peak_1, "g")
                plt.fill_between(t, lorentz_peak_1.min(), lorentz_peak_1, facecolor="green", alpha=0.15)
                  
                plt.plot(t, lorentz_peak_2, "m")
                plt.fill_between(t, lorentz_peak_2.min(), lorentz_peak_2, facecolor="magenta", alpha=0.15)  
                
                plt.plot(t, lorentz_peak_3, "b")
                plt.fill_between(t, lorentz_peak_3.min(), lorentz_peak_3, facecolor="blue", alpha=0.15)  
                
        #        plt.plot(t[sample_number],res[t[sample_number]],'r*')
                plt.show()
                plt.close()
        
        
#        residual_3lorentz = res[t] - (_3lorentz(t, *popt_3lorentz))       
        
            
        else:
            if no_ajuste == 'y':
                
                plt.figure(zz)
                plt.plot(res, 'm')
            else:
                print('Al parecer, no queres ver un carajo')
                
    Q_avg = np.mean(Quality_factor)
    
    Linewidth = np.mean(FHWM_)*1e-6
    
    fhwm_plot   = np.asarray(FHWM_, dtype=np.float32)
    q_plot      = np.asarray(Quality_factor, dtype=np.float32)
    wl_plot     = np.asarray(wavelength_, dtype=np.float32)
    
    plt.figure()
    plt.plot(fhwm_plot*1e-6, q_plot*1e-6,'o')
    plt.xlabel('Linewidth (MHz)')
    plt.ylabel('Quality factor (mill.)')
    
    plt.figure()
    plt.plot(wl_plot*1e9, q_plot*1e-6,'o-')
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Quality factor (mill.)')
    
#    print(Quality_factor)
    
    print('------------------------------------------------------------------')
    print('------------------------------------------------------------------')
    print('N° data analised: %s // and N° used data: %s ' % (zz,p))   
    
    print('Average Q factor of this chip: %s million'% np.round(Q_avg*1E-6,2))
    print('Average FHWM of this chip: %s MHz'% np.round(Linewidth,2))
    print('------------------------------------------------------------------')
    print('------------------------------------------------------------------')    
    return Q_avg, Quality_factor, zz 



#sideband = 500 # MHz
    
gap = 0.55 #micron
mediciones = 51

variacion = 600
#seleccion_de_picos = 0.05
distancia_sidebands = 220
size_resonance = 3


#interes = '20200511_Gap_06_Q_factor_C3'

n_plots = 0
zz = 0

#Primary_Folder = '20201009_3rd_Run_EPFL'
##3erd RUN from EPFL
#Q_avg, Quality_factor, zz  = Q_factor('F3',
#                                      Primary_Folder, 
#                                      'F3', 
#                                      280, 
#                                      mediciones, 
#                                      gap, 
#                                      500,
#                                      0.05, 
#                                      150,
#                                      size_resonance,
#                                      n_plots)




#%% Old chips
Primary_Folder = '20200511_Looking_for_better_Q_factor'
#Q_avg, Quality_factor, zz  = Q_factor('D2',
#                                      Primary_Folder, 
#                                      '20200512_Gap_06_Q_factor_D2', 
#                                      800, 
#                                      mediciones, 
#                                      gap, 
#                                      500,
#                                      0.05, 
#                                      150,
#                                      size_resonance,
#                                      n_plots)

#n_plots = zz
#Q_avg, Quality_factor, zz  = Q_factor('C3',Primary_Folder, '20200511_Gap_06_Q_factor_C3', 500, mediciones, gap, variacion,
#             0.05, distancia_sidebands,size_resonance,n_plots)

#n_plots = zz
#Q_avg, Quality_factor, zz  = Q_factor('C2',
#                                      Primary_Folder, 
#                                      '20200511_Gap_06_Q_factor_C2_v2', 
#                                      500, 
#                                      n_med = mediciones, 
#                                      gap = 0.6, 
#                                      variacion = 500,
#                                      seleccion_de_picos = 0.027, 
#                                      distancia_sidebands = 250,
#                                      size_resonance = 0.3,
#                                      n_plots = zz)

#n_plots = zz
#Q_avg, Quality_factor, zz  = Q_factor('D2',
#                                      Primary_Folder='20200511_Looking_for_better_Q_factor', 
#                                      interes = '20200512_Gap_06_Q_factor_D2_v2', 
#                                      sideband = 800, 
#                                      n_med = mediciones, 
#                                      gap = 0.6, 
#                                      variacion = 500,
#                                      seleccion_de_picos = 0.027, 
#                                      distancia_sidebands = 250,
#                                      size_resonance = 0.3,
#                                      n_plots = zz)

#Q_avg, Quality_factor, zz  = Q_factor('D3',
#                                      Primary_Folder = '20200511_Looking_for_better_Q_factor', 
#                                      interes = '20200514_Gap_06_Q_factor_D3_v2', 
#                                      sideband = 800, 
#                                      n_med = mediciones, 
#                                      gap = 0.6, 
#                                      variacion = 600,
#                                      seleccion_de_picos = .20, 
#                                      distancia_sidebands = 250,
#                                      size_resonance = 0.3,
#                                      n_plots = zz)


#n_plots = zz

Q_avg, Quality_factor, zz  = Q_factor(name = 'F3',
                     Primary_Folder='20200511_Looking_for_better_Q_factor', 
                     interes = '20200518_Gap_06_C6', 
                     sideband = 800, 
                     n_med = mediciones, 
                     gap = 0.6, 
                     variacion = 500,
                     seleccion_de_picos = .20, 
                     distancia_sidebands= 220,
                     size_resonance = 0.3,
                     n_plots = zz)
n_plots = zz

#Q_avg, Quality_factor, zz  = Q_factor('C10',
#                                      Primary_Folder='20200511_Looking_for_better_Q_factor',
#                                      interes= '20200518_Gap_06_C10', 
#                                      sideband = 800, 
#                                      n_med=mediciones,
#                                      gap=0.6,
#                                      variacion = 600,
#                                      seleccion_de_picos = .20,
#                                      distancia_sidebands = 220,
#                                      size_resonance = 0.3,
#                                      n_plots = zz)
#n_plots = zz

#Q_avg, Quality_factor, zz  = Q_factor('C10',
#                                      Primary_Folder='20200511_Looking_for_better_Q_factor', 
#                                      interes = '20200518_Gap_06_C10_500MHz', 
#                                      sideband = 500, 
#                                      n_med = mediciones, 
#                                      gap = 0.6, 
#                                      variacion = 350,             
#                                      seleccion_de_picos = .20, 
#                                      distancia_sidebands = 220,
#                                      size_resonance = 0.3,
#                                      n_plots = zz)
#n_plots = zz

#Q_avg, Quality_factor, zz  = Q_factor('D6',
#                                      Primary_Folder='20200511_Looking_for_better_Q_factor', 
#                                      interes = '20200518_Gap_06_D6', 
#                                      sideband = 800,                                        
#                                      n_med = mediciones, 
#                                      gap = 0.6, 
#                                      variacion = 350,
#                                      seleccion_de_picos = .20, 
#                                      distancia_sidebands= 150,
#                                      size_resonance = 0.3,
#                                      n_plots = zz)
#n_plots = zz

#Q_avg, Quality_factor, zz = Q_factor(name = 'D9',
#                                     Primary_Folder='20200511_Looking_for_better_Q_factor', 
#                                     interes = '20200518_Gap_06_D9', 
#                                     sideband = 500, 
#                                     n_med = mediciones, 
#                                     gap = 0.6, 
#                                     variacion = 300,
#                                     seleccion_de_picos = .20, 
#                                     distancia_sidebands= 150,
#                                     size_resonance = 0.3,
#                                     n_plots = zz)

#
#Q_avg, Quality_factor, zz  = Q_factor('Ortwin packaged',
#                                      Primary_Folder = '20200511_Looking_for_better_Q_factor', 
#                                      interes = '20200520_20GHz_packaged', 
#                                      sideband = 250, 
#                                      n_med = mediciones, 
#                                      gap = 0.6, 
#                                      variacion = 300,
#                                      seleccion_de_picos = 0.30, 
#                                      distancia_sidebands = 100, #250
#                                      size_resonance = 0.3,
#                                      n_plots = zz)





#Q_avg, Quality_factor, zz  = Q_factor('B6',
#                                      Primary_Folder = '20200511_Looking_for_better_Q_factor', 
#                                      interes = '20200520_12GHz_600MHz_1st_run_Ligentec', 
#                                      sideband = 600, 
#                                      n_med = mediciones, 
#                                      gap = 0.55, 
#                                      variacion = 300,
#                                      seleccion_de_picos = 10.30, 
#                                      distancia_sidebands = 150, #250
#                                      size_resonance = 1,
#                                      n_plots = zz)


#Q_avg, Quality_factor, zz  = Q_factor('Col_3,Fila_1',
#                                      Primary_Folder = '20200511_Looking_for_better_Q_factor', 
#                                      interes = '20200520_12GHz_EPFL_run', 
#                                      sideband = 250, 
#                                      n_med = mediciones, 
#                                      gap = 0.55, 
#                                      variacion = 300,
#                                      seleccion_de_picos = 10.30, 
#                                      distancia_sidebands = 100, #250
#                                      size_resonance = 1,
#                                      n_plots = zz)
#
#Q_avg, Quality_factor, zz  = Q_factor('Col_7,Fila_1',
#                                      Primary_Folder = '20200511_Looking_for_better_Q_factor', 
#                                      interes = '20200520_12GHz_EPFL_2nd_run', 
#                                      sideband = 250, 
#                                      n_med = mediciones, 
#                                      gap = 0.55, 
#                                      variacion = 300,
#                                      seleccion_de_picos = 10.30, 
#                                      distancia_sidebands = 100, #250
#                                      size_resonance = 1,
#                                      n_plots = zz)

#Q_avg, Quality_factor, zz  = Q_factor('Col_7,Fila_1',
#                                      Primary_Folder = '20200511_Looking_for_better_Q_factor', 
#                                      interes = 'EPFL_2nd_run_v7', 
#                                      sideband = 250, 
#                                      n_med = mediciones, 
#                                      gap = 0.55, 
#                                      variacion = 300,
#                                      seleccion_de_picos = 10.30, 
#                                      distancia_sidebands = 100, #250
#                                      size_resonance = 1,
#                                      n_plots = zz)

#Q_avg, Quality_factor, zz  = Q_factor('1st_run_EPFL_Scratched_10GHz',
#                                      Primary_Folder = '20200511_Looking_for_better_Q_factor', 
#                                      interes = 'Scratched_10GHz_EPFL_300MHz', 
#                                      sideband = 250, 
#                                      n_med = mediciones, 
#                                      gap = 0.55, 
#                                      variacion = 300,
#                                      seleccion_de_picos = 10.30, 
#                                      distancia_sidebands = 100, #250
#                                      size_resonance = 1,
#                                      n_plots = zz)

#Q_avg, Quality_factor, zz  = Q_factor('Ortwin_packaged_chip',
#                                      Primary_Folder = '20200511_Looking_for_better_Q_factor', 
#                                      interes = 'Ortwin_chip_toma2', 
#                                      sideband = 250, 
#                                      n_med = mediciones, 
#                                      gap = 0.55, 
#                                      variacion = 300,
#                                      seleccion_de_picos = 10.30, 
#                                      distancia_sidebands = 100, #250
#                                      size_resonance = 1,
#                                      n_plots = zz)

#print((4.66+9.81+6.33+6.09+8.28+6.14+8.22)/7)



