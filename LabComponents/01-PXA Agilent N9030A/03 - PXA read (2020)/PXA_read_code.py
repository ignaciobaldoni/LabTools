# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 18:25:21 2020

@author: ibaldoni
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PXA_Lines = 44
Nummer = 11
file = 'Trace_00'+str(Nummer)

interes     = '20201211_Single_soliton_12GHz\\1 - Raw Data\With RF amplifier\\Right Microwave Amplifier\\'
interes2    = '20201211_Single_soliton_12GHz\\3 - Results'
data = pd.read_csv(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                    +str(interes)+str(file)+'.csv',
                    skiprows=PXA_Lines)

data.columns = ["Frequency", "Pow"]

Center_Freq_index = np.where(data.Pow == data.Pow.max())
Center_freq_GHz = np.round(data.Frequency.iloc[Center_Freq_index].values[0]*1e-9,6)
variable = (data.Frequency.max()-data.Frequency.min())*0.5

Freq = np.linspace(-variable,variable,len(data.Frequency)); Freq_kHz = Freq*1e-3

plt.figure(figsize=(22,14))
plt.plot(Freq_kHz,data.Pow, linewidth=2, label = "Center frequency = "+str(Center_freq_GHz)+"GHz")
plt.plot(Freq_kHz[Center_Freq_index],data.Pow.max(),'w.',label='Max RF = '+str(np.round(data.Pow.max(),2))+"dBm")
plt.legend(fontsize=23)
plt.title("12 GHz microwave signal",fontsize=27)
plt.xlabel("Frequency (kHz)",fontsize=23)
plt.ylabel("dBm",fontsize=23)
plt.grid()
plt.yticks(fontsize=25, rotation=0)
plt.xticks(fontsize=25, rotation=0)

plt.savefig(r'\\menloserver\\MFS\\03-Operations\\02-DCP\\03-Entwicklungsprojekte\\9552-KECOMO\\52-Messergebnisse\\'
                    +str(interes2)+"\\"+str(file)+'.png')