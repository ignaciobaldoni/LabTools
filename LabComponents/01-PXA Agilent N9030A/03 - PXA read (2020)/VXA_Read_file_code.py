# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 18:25:21 2020

@author: ibaldoni
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PXA_Lines = 68
Nummer = 1
file = 'Vector_Analyzer_'+str(Nummer)

interes     = '20201211_Single_soliton_12GHz\\1 - Raw Data\With RF amplifier\\Right Microwave Amplifier\\'
interes2    = '20201211_Single_soliton_12GHz\\3 - Results'
data = pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                    +str(interes)+str(file)+'.csv',
                    skiprows=PXA_Lines)

data.columns = ["variable"]

plt.figure(figsize=(22,14))
plt.plot(np.log(data.variable),label='')
plt.legend(fontsize=23)
plt.title("12 GHz microwave signal",fontsize=27)
plt.xlabel("Frequency (kHz)",fontsize=23)
plt.ylabel("dBm",fontsize=23)
plt.grid()
plt.yticks(fontsize=25, rotation=0)
plt.xticks(fontsize=25, rotation=0)

plt.savefig(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                    +str(interes2)+"\\"+str(file)+'.png')