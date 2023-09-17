# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 21:50:35 2023

@author: ibaldoni
"""



import pyautogui

import os
import win32gui

FOLDER = r'\\menloserver\MFS\03-Operations\03-Production\05-AU_PA\AU07434-SmartComb-PMWG_Hensoldt\03-Endabnahme\09-Microwave\AM to PM conversion\02 - Raw Data'

folder1 = '\Operating at optimal biases'
folder2 = '\\14.6 mW opt power 7dBm MW (after HMC)'
folder3 = '\First configuration_day 2'
print()

Options = ['P','A']



# FOLDER = (r'\\menloserver\MFS\03-Operations\03-Production\05-AU_PA\\'
#           r'AU07434-SmartComb-PMWG_Hensoldt\03-Endabnahme\\'
#           r'09-Microwave\AM to PM conversion')


folder1 = '\Freedom photonics MWU\Optical power 3.0 mW, MW power -15.2 dBm'
folder2 = '\Freedom photonics MWU\Optical power 5.0 mW, MW power -11.4 dBm'
folder3 = '\Freedom photonics MWU\Optical power 6.1 mW, MW power -8.67 dBm'
folder4 = '\HHI Fraunhofer MWU\Optical power 3_0mW MW -18.8 dBm'
folder5 = '\HHI Fraunhofer MWU\Optical power 5_0mW MW -14 dBm'
folder6 = '\HHI Fraunhofer MWU\Optical power 8_10 mW MW -8.5 dBm'

folder7 = '\HHI Fraunhofer MWU\Optical power 14.6 mW 7dBm MW (after HMC)'
folder8 = '\HHI Fraunhofer MWU\Optical power 14.6 mW (second scheme)'



Options = ['P','A']
sep = ','
headers = ['Frequency', 'PSD']

Folders = [FOLDER+folder8
    # FOLDER+folder1,
    #        FOLDER+folder2,
    #        FOLDER+folder3,
    #        FOLDER+folder4,
    #        FOLDER+folder5,
    #        FOLDER+folder6
    ]

# Folders=[r'\\menloserver\MFS\03-Operations\03-Production\05-AU_PA\AU07434-SmartComb-PMWG_Hensoldt\03-Endabnahme\09-Microwave\AM to PM conversion\HHI Fraunhofer MWU\Around maximum 10.5 V Bias voltage optical power 8 mW']


for folder_path in Folders:
    print(folder_path)
    
    os.chdir(folder_path)
    # Loop through all files in the directory
    for file in os.listdir(folder_path):
        # Check if file has .csv extension
        if file.endswith(".tim"):
            # Open file using the default program associated with .csv files
            os.startfile(file)
            # Wait for file to fully open
            
            pyautogui.sleep(.2)
            
            hwnd = win32gui.GetForegroundWindow()
            
            # Bring the file window to the foreground
            win32gui.SetForegroundWindow(hwnd)
            pyautogui.sleep(3)
            for i in Options:
                print(i)
                
                if 'P' in i: Noise = 'PM'
                if 'A' in i: Noise = 'AM'
            
                pyautogui.typewrite(f"'{i}'")
                pyautogui.sleep(1.5)
                
                
                
                
                # Locate the coordinates of the FILE tab and the EXPORT ASCII option
                file_tab = (25, 25) # Replace with the actual coordinates of the FILE tab
                      
                # Click on the FILE tab
                pyautogui.click(file_tab)
                
                # Move the cursor to the EXPORT ASCII option and click on it
                for i in range(11):
                    pyautogui.press('down')
                pyautogui.hotkey('Enter')
                
                pyautogui.sleep(3)
                pyautogui.typewrite(folder_path)
                pyautogui.hotkey('Enter')
                pyautogui.sleep(3)
                pyautogui.typewrite(f"{file[:-4]}_{Noise}")
                pyautogui.hotkey('Enter')
                
            # pyautogui.hotkey('Enter')
            
            
            pyautogui.hotkey('alt', 'f4')
