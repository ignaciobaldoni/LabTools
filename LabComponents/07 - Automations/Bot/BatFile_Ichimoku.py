# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 14:37:52 2023

@author: ibaldoni

This script automates the process of opening the Spyder IDE, opening the Python 
script of "Ichimoku_bot", and runs it.
"""

import time
import pyautogui
import psutil
  
# # check if chrome is open
# if ('pythonw.exe' not in (i.name() for i in psutil.process_iter())):

pyautogui.hotkey('win', 'r')

time.sleep(2)
pyautogui.typewrite("C:\\Users\\ibaldoni\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Anaconda3 (64-bit)\\Spyder (Anaconda3).lnk")
pyautogui.hotkey('Enter')    
time.sleep(50)
    
pyautogui.hotkey('ctrl', 'o')

pyautogui.typewrite('C:\\Users\\ibaldoni\\Desktop\\Bot\\Ichimoku_Bot.py')

time.sleep(1)
pyautogui.hotkey('Enter')

time.sleep(2)
pyautogui.hotkey('F5')


time.sleep(300)

pyautogui.hotkey('alt','f4')