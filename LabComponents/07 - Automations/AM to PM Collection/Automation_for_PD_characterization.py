# -*- coding: utf-8 -*-
"""
Created on Wed May  3 09:37:19 2023

@author: ibaldoni
"""

import pyautogui
pyautogui.FAILSAFE = False
# import pyvisa as visa
import numpy as np

import os
# import win32gui
import subprocess
import time

# from Powermeter_PM100A import Thorlabs_PM100A
from Keysight_DC_Power_Supply_class import Keysight_E36312A_DC_Power_Supply
# from RhodeSchwarz_SMC100A_class import RhodeSchwarz_SMC100A
from AM2PM_forAutomation import AM2PM


def open_program(program_path):
    try:
        subprocess.Popen(program_path)
        print(f"Opened program: {program_path}")
    except Exception as e:
        print(f"Error opening program: {e}")
        

def dBm_to_mW(dBm):
    # print(10**(dBm/10))
    return 10**(dBm/10)

def AM_depth(dBm):
    power = dBm_to_mW(dBm)
    
    # 0.89 mW are a proper modulation power
    fraction = (0.89/power)*100


    AM_depth_power = fraction*dBm_to_mW(dBm)/100
    AM_depth_porcentage = fraction
      
    
    return AM_depth_porcentage, AM_depth_power,


        
        
    

def Automation_for_tim_files(bias = 4, optPower = 5, temperature = 23,
                             folder_path='Test', Options = ['P','A']):
    pyautogui.typewrite('P')
    pyautogui.sleep(1)
    pyautogui.hotkey('del')
    pyautogui.hotkey('Space')
    pyautogui.sleep(1)
    pyautogui.typewrite(f'{bias:.1f} V bias')
    pyautogui.hotkey('Enter')
    pyautogui.sleep(10)
    pyautogui.press('s')
    pyautogui.sleep(.5)
    pyautogui.typewrite(f'{folder_path}')
    pyautogui.sleep(0.5)
    pyautogui.hotkey('Enter')
    pyautogui.sleep(.5)
    pyautogui.typewrite(f"{bias:.1f} V bias")
    pyautogui.sleep(.5)
    pyautogui.hotkey('Enter')
    # pyautogui.hotkey('alt', 'f4')
    
    for i in Options:
        print(i)
        
        if 'P' in i: Noise = 'PM'
        if 'A' in i: Noise = 'AM'
    
        pyautogui.typewrite(f"'{i}'")
        pyautogui.sleep(.5)
        
        # Locate the coordinates of the FILE tab and the EXPORT ASCII option
        file_tab = (15, 40) # Replace with the actual coordinates of the FILE tab
              
        # Click on the FILE tab
        pyautogui.click(file_tab)
        
        # Move the cursor to the EXPORT ASCII option and click on it
        for i in range(11):
            pyautogui.press('down')
        pyautogui.hotkey('Enter')
        
        pyautogui.sleep(1.)
        pyautogui.typewrite(f'{folder_path}')
        pyautogui.hotkey('Enter')
        pyautogui.sleep(.5)
        pyautogui.typewrite(f"{bias:.1f} V bias_{Noise}")
        pyautogui.sleep(.25)
        pyautogui.hotkey('Enter')
        # pyautogui.sleep(3.0)
        
    pyautogui.typewrite("P")
    pyautogui.hotkey('del')
    


if __name__ == '__main__':
    
    # We open TimeLab
    program_path = r"C:\Program Files\Microchip\TimeLab\timelab64.exe"  # Replace with the actual program path
    open_program(program_path)
    
    # resourceStr_FG = "USB0::0x0AAD::0x006E::108450::INSTR"
    # FunctionGenerator = RhodeSchwarz_SMC100A(resourceStr_FG)
    # FunctionGenerator.setAM_frequency_kHz(10)  
    
    # resourceStr_powermeter = 'USB0::0x1313::0x8078::PM002940::INSTR'
    # powermeter = Thorlabs_PM100A( resourceStr_powermeter)

    resourceStr_bias = "USB0::0x2A8D::0x1102::MY61003592::INSTR"
    DC_PowerSupply = Keysight_E36312A_DC_Power_Supply(resourceStr_bias)
    
	
	
	
          
    
    
    FOLDER = (r'\\menloserver\mfs\03-Operations\03-Production\05-AU_PA'+\
              r'\AU07627_AU06630-RMA-Syncro\05_2023 - Photodiodes characterization'+\
              r'\HHI Fraunhoffer (new)\AM to PM NIST')
    
        
    folder = r'\TEST FOR AUTOMATION AU7434'
    subfolders = FOLDER + folder
    
    BiasVoltages = np.arange(15.0,3.5,10.1)
    AOM_Level = np.arange(13,19,102) 
    # AOM_Level = np.arange(0.1,1,.1)
    
    for levels in AOM_Level:

        
        
        # FunctionGenerator.setLevel(levels)
        
        # AM_depth_porcentage, AM_depth_power = AM_depth(levels)
        
        
        # FunctionGenerator.setAM_depth(AM_depth_porcentage)
        
        
    
        
        
        # powermeter.setWavelength(1542)
        # power = powermeter.readPower()
        power = 9.2
        print(power)
        
        

        
        for_results = subfolders
        results_folder = os.path.join(for_results, f'{power:.2f} mW')
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        
        
        
        previous_am2pm = 100
        bias_voltage = 5
        final_biasVoltage = 18
        while bias_voltage<final_biasVoltage: 
            
            
        
            time.sleep(1)
            
            bias = DC_PowerSupply.setBias(bias = bias_voltage, channel=2)    
            
            time.sleep(2)
            
            
                         
            print(bias_voltage,'V bias')
            
            # print(results_folder)
            
            ## Example usage
            Automation_for_tim_files(folder_path=results_folder, 
                                      bias = bias_voltage,
                                      optPower = power)
            
            
                
                
            last_am2pm, first_am2pm = AM2PM(folder=results_folder)
            print('done')
            
            print('AM2PM was:', last_am2pm)
            if (np.abs(last_am2pm-previous_am2pm)<1) and (np.abs(last_am2pm-first_am2pm)<10 or 
                                                          last_am2pm-previous_am2pm>0.5):
                bias_voltage += 0.5
            elif (np.abs(last_am2pm-previous_am2pm)>=1) and (np.abs(last_am2pm-first_am2pm)>=10):
                bias_voltage += 0.1
            else:
                print('No condition satisfied. We simply put bias voltage += 0.1 here')
                bias_voltage += 0.1
            print('Next Bias: ', bias_voltage)
            previous_am2pm = last_am2pm
            
            
                
            
        
        # pyautogui.hotkey('alt', 'f4')
        time.sleep(3600)    