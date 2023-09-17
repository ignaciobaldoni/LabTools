# -*- coding: utf-8 -*-
"""
Created on Sun Sep 19 14:20:00 2021

@author: akordts
"""

import numpy as np

avgs = [1,1,1,1,1000,1000,1000,1000]

measTimes = [25*60,130,13,1.3,0.13,0.05,0.05,0.05]

time = np.sum(np.asarray(avgs)*np.asarray(measTimes))/3600.
print(time)

time =    25*60  * 2 \
        + 130 * 10 \
        + 13 * 100 \
        + 1.3 * 1000 \
        + 0.13 * 2000 \
        + 0.05 * 2000 \
        + 0.05 * 2000 \
        + 0.05 * 2000        

time = time/3600

print(time)