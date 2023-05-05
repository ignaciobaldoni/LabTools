# -*- coding: utf-8 -*-
"""
Created on Wed May  3 09:37:19 2023

@author: ibaldoni
"""

import pyautogui

import os
import win32gui


def Automation_for_tim_files(FOLDER,subfolders):
    
    Options = ['P','A']    

    for folder_path in subfolders:
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


if __name__ == '__main__':
    
    FOLDER = (r'\\menloserver\MFS\03-Operations\03-Production\05-AU_PA'+\
              r'\AU07434-SmartComb-PMWG_Hensoldt\03-Endabnahme'+\
              r'\09-Microwave\AM to PM conversion\02 - Raw Data')


    folder1 = '\Freedom photonics MWU\Optical power 3.0 mW, MW power -15.2 dBm'
    folder2 = '\Freedom photonics MWU\Optical power 5.0 mW, MW power -11.4 dBm'
    folder3 = '\Freedom photonics MWU\Optical power 6.1 mW, MW power -8.67 dBm'
    folder4 = '\HHI Fraunhofer MWU\Optical power 3_0mW MW -18.8 dBm'
    folder5 = '\HHI Fraunhofer MWU\Optical power 5_0mW MW -14 dBm'
    folder6 = '\HHI Fraunhofer MWU\Optical power 8_10 mW MW -8.5 dBm'
    folder7 = '\HHI Fraunhofer MWU\Optical power 14.6 mW 7dBm MW (after HMC)'
    folder8 = '\HHI Fraunhofer MWU\Optical power 14.6 mW (second scheme)'
    
    
    # folder0 = '\Two_DUTs_One_OCXO_Ref'
    # folder0 = r'\preparation R_S'
    folder0 = r'\Overnight measurement for RS'
    
    
    subfolders = [FOLDER + folder for folder in [folder0, 
                                                 # folder2, 
                                                 # folder3, 
                                                 # folder4,
                                                 # folder5, 
                                                 # folder6,
                                                 # folder7,
                                                 # folder8
                                                 ]]
    

    print(subfolders)
    Automation_for_tim_files(FOLDER,subfolders)

