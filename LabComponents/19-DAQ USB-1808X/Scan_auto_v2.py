# -*- coding: utf-8 -*-
"""
Created on Fri May 29 16:19:47 2020

@author: Administrator
"""

import time
import pyautogui
import psutil
import subprocess
import win32gui
import win32process
import sys
import win32com
import win32com.client 

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import tkinter as tk
from DAQ_v5 import ULAIO01
from Nueva_DAQ import Scope_DAQ

from Temp_sensor_v2 import Temp_Sensor

#shell = win32com.client.Dispatch("WScript.Shell")
#shell.SendKeys('%')
#hwnd = win32gui.FindWindowEx(0,0,0, "TLB-6700 Tunable Laser Application")
#win32gui.SetForegroundWindow(hwnd)
#   
Chip_name = 'F3'
gap = 0.55
 
#interes = '20200512_Gap_06_Q_factor_'+str(Chip_name)+'_v2'

## Folder name
interes = str(Chip_name)

print('Before we start:')
check1 = input('Have you turned ON the laser? : ')
if check1 == 'y':
    check2 = input('Have you turned set the correct power? : ')
    if check2 == 'y':
        check3 = input('Have you turned set ACTUAL in power? : ')
        if check3 == 'y':
            print('Then we are ready to go!')
        else:
            raise ValueError('Do things right, then, you fucking asshole!')
    else:
        raise ValueError('Do things right, then, you fucking asshole!')
else:
    raise ValueError('Then do things right, you fucking asshole!')

time_begin = time.time()  

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


## Check if any chrome process was running or not.
 
if checkIfProcessRunning('TunableLaserApp'):
    print('Laser programm running. Alles gut. ')
    
    time.sleep(2)
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    hwnd = win32gui.FindWindowEx(0,0,0, "TLB-6700 Tunable Laser Application")
    win32gui.SetForegroundWindow(hwnd)
    
    pyautogui.click(100,100)
    pyautogui.click(100,100)
    pyautogui.click(100,100)

    
#    Wavelength/Power    
    for i in range(0,2):
        pyautogui.hotkey('tab')
        time.sleep(0.25)        
        
    pyautogui.hotkey('tab')
    p=0
    step = 1
    inicio = 20
    final = 70
    
    for i in range(inicio,final+step,step):
        
        nombre = "C:\\Users\\Administrator.MenloPC208\\Desktop\\Chip_analysis_Oct2020\\"+ \
        str(interes)+"\\Data_15"+str(i)+"_GAP_"+str(gap)+".csv"
        
        name_T = "C:\\Users\\Administrator.MenloPC208\\Desktop\\Chip_analysis_Oct2020\\"+ \
        str(interes)+"\\Temp_15"+str(i)+"_GAP_"+str(gap)+".csv"
        
        p = p+1
        print('Scanning wavelength: 15'+str(i))
        for ii in range(0,2):
            pyautogui.hotkey('tab')
            time.sleep(0.25)

        pyautogui.press('left',presses=10) 
        pyautogui.press('del',presses=10)  
        time.sleep(0.5)

        pyautogui.press('clear')        
        
        time.sleep(1)
        pyautogui.typewrite('15'+str(i)+',00') 
        
        pyautogui.hotkey('tab')
        for ii in range(0,8): #If you choose ACTUAL in Power
            pyautogui.hotkey('tab')
        pyautogui.hotkey('space')
        print('Wavelength track is ON')
        time.sleep(7*step)
        pyautogui.hotkey('space')
        print('Wavelength setpoint reached')
        
        print('Track wavelength is OFF')
        pyautogui.hotkey('space')
        
        time.sleep(6)
        print('System already stabilized in the new wavelength')

        print('We take and save the data from the oscilloscope')
        
        
        rate = 5000
        points_per_channel = 50000
        
        
        
        result = Scope_DAQ(rate,points_per_channel)
        
        Result=pd.DataFrame(result)
        Result.to_csv(nombre)
        
        
        
#        ULAIO01(Rate_In     = 30000, 
#            Points_In       = 30000,
#            Frequency_Out   = 2,
#            Rate_Out        = 3000,
#            Wave_Type       = 'Triangle',  
#            Amplitud        = 1,
#            Offset          = 0,
#            Name_file       = nombre,
#            master=tk.Tk()).mainloop()
#    
#        Data = pd.read_csv(str(nombre))
#        
##        t,t1,t2,h = Temp_Sensor(name_T)
##        print(np.round(t2,2))
               

else:
#    ya_hubo_un_problema = 1
    raise ValueError("Programm is not running!!")


minutes = (time.time() - time_begin)/60
print('Number of measurements = %s' % p)
print('Time for complete scan = %s minutes' % minutes)