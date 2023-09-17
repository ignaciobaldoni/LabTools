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
        # print(folder_path)
        
        os.chdir(folder_path)
        
        if any(file.endswith('.csv') for file in os.listdir(folder_path)):
            print("This folder was already converted to CSV files")
        else:
    
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
                    pyautogui.sleep(2)
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
                        
                        pyautogui.sleep(1.0)
                        pyautogui.typewrite(folder_path)
                        pyautogui.hotkey('Enter')
                        pyautogui.sleep(1.0)
                        pyautogui.typewrite(f"{file[:-4]}_{Noise}")
                        pyautogui.hotkey('Enter')
                        
                    # pyautogui.hotkey('Enter')
                    
                    
                    pyautogui.hotkey('alt', 'f4')


if __name__ == '__main__':
    

    FOLDER = (r'\\menloserver\mfs\03-Operations\03-Production\05-AU_PA'+\
              r'\AU07627_AU06630-RMA-Syncro\05_2023 - Photodiodes characterization'+\
              r'\HHI Fraunhoffer (new)\AM to PM NIST\Temperature dependence measurements\22.5 degrees')
    
        
    folder1 = r'\9 mW'
    folder2 = r'\3 mW'
    folder3 = r'\4 mW'
    folder4 = r'\5 mW'
    folder5 = r'\6 mW'
    folder6 = r'\7 mW'
    folder7 = r'\8 mW'
        
        

    
    
    subfolders = [FOLDER + folder for folder in [folder1, 
                                                 folder2, 
                                                 folder3, 
                                                 folder4,
                                                 folder5, 
                                                 folder6,
                                                 folder7,
                                                 # folder8
                                                 ]]
    

    print(subfolders)
    Automation_for_tim_files(FOLDER,subfolders)

