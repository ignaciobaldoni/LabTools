# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 11:19:40 2023

@author: ibaldoni

MEAN REVERSION STRATEGY

https://raposa.trade/blog/how-to-build-your-first-mean-reversion-trading-strategy-in-python/

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# end_date='2020-12-31'
Start_Date = '2018-01-01' #'2000-01-01'

def SMAMeanReversion(ticker, sma, threshold, shorts=False,
    start_date=Start_Date):
    yfObj = yf.Ticker(ticker)
    data = yfObj.history(start=start_date)#, end=end_date)
    data['SMA'] = data['Close'].rolling(sma).mean()
    data['extension'] = (data['Close'] - data['SMA']) / data['SMA']
    
    data['position'] = np.nan
    data['position'] = np.where(data['extension']<-threshold,
        1, data['position'])
    if shorts:
        data['position'] = np.where(
            data['extension']>threshold, -1, data['position'])
        
    data['position'] = np.where(np.abs(data['extension'])<0.01,
        0, data['position'])
    data['position'] = data['position'].ffill().fillna(0)
    
    # Calculate returns and statistics
    data['returns'] = data['Close'] / data['Close'].shift(1)
    data['log_returns'] = np.log(data['returns'])
    data['strat_returns'] = data['position'].shift(1) * \
        data['returns']
    data['strat_log_returns'] = data['position'].shift(1) * \
        data['log_returns']
    data['cum_returns'] = np.exp(data['log_returns'].cumsum())
    data['strat_cum_returns']  = np.exp(data['strat_log_returns'].cumsum())
    data['peak'] = data['cum_returns'].cummax()
    data['strat_peak'] = data['strat_cum_returns'].cummax()
    
    return data.dropna()




def SMAMeanReversionSafety(ticker, sma, threshold, 
    safety_threshold=0.25, shorts=False, 
    start_date=Start_Date):
    yfObj = yf.Ticker(ticker)
    data = yfObj.history(start=start_date)#, end=end_date)
    data['SMA'] = data['Close'].rolling(sma).mean()
    data['extension'] = (data['Close'] - data['SMA']) / data['SMA']
    
    data['position'] = np.nan
    data['position'] = np.where(
        (data['extension']<-threshold) & 
        (data['extension']>-safety_threshold), 
        1, data['position'])
    
    if shorts:
        data['position'] = np.where(
            (data['extension']>threshold) & 
            (data['extension']<safety_threshold),
            -1, data['position'])
        
    data['position'] = np.where(np.abs(data['extension'])<0.01,
        0, data['position'])
    data['position'] = data['position'].ffill().fillna(0)
    
    # Calculate returns and statistics
    data['returns'] = data['Close'] / data['Close'].shift(1)
    data['log_returns'] = np.log(data['returns'])
    data['strat_returns'] = data['position'].shift(1) * \
        data['returns']
    data['strat_log_returns'] = data['position'].shift(1) * data['log_returns']
    data['cum_returns'] = np.exp(data['log_returns'].cumsum())
    data['strat_cum_returns'] =\
        np.exp(data['strat_log_returns'].cumsum())
    data['peak'] = data['cum_returns'].cummax()
    data['strat_peak'] = data['strat_cum_returns'].cummax()
    
    return data.dropna()



ticker = 'DIS'
SMA = 50
threshold = 0.1
shorts = False
data = SMAMeanReversion(ticker, SMA, threshold, shorts)
plots = True

if plots:
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    fig, ax = plt.subplots(3, figsize=(10, 8), sharex=True)
    long = data.loc[data['position']==1]['Close']
    ax[0].plot(data['Close'], label='Price', linestyle=':', color=colors[1])
    ax[0].plot(data['SMA'], label='SMA', linestyle='--', color=colors[0])
    ax[0].scatter(long.index, long, label='Long', c=colors[2])
    ax[0].legend(bbox_to_anchor=[1, 0.75])
    ax[0].set_ylabel('Price ($)')
    ax[0].set_title(f'{ticker} Price and Positions with {SMA}-Day Moving Average')
    ax[1].plot(data['extension']*100, label='Extension', color=colors[0])
    ax[1].axhline(threshold*100, linestyle='--', color=colors[1])
    ax[1].axhline(-threshold*100, label='Threshold', linestyle='--', color=colors[1])
    ax[1].axhline(0, label='Neutral', linestyle=':', color='k')
    ax[1].set_title('Price Extension and Buy/Sell Thresholds')
    ax[1].set_ylabel('Extension (%)')
    ax[1].legend(bbox_to_anchor=[1, 0.75])
    ax[2].plot(data['position'])
    ax[2].set_xlabel('Date')
    ax[2].set_title('Position')
    ax[2].set_yticks([-1, 0, 1])
    ax[2].set_yticklabels(['Short', 'Neutral', 'Long'])
    plt.tight_layout()
    plt.show()
#########################################################


safety_threshold = 0.15

data = SMAMeanReversion(ticker, SMA, threshold, shorts)
data_safe = SMAMeanReversionSafety(ticker, SMA, threshold, safety_threshold, shorts)
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(data_safe['strat_cum_returns'], label='Mean Reversion Strategy with Safety')
ax.plot(data['strat_cum_returns'], label='Mean Reversion Strategy')
ax.plot(data_safe['cum_returns'], label=f'{ticker}')
ax.set_xlabel('Date')
ax.set_ylabel('Returns (%)')
ax.set_title('Cumulative Returns for Mean Reversion and Buy and Hold Strategies')
ax.legend()
plt.show()

print('Strategy Safe:\t',data_safe['strat_cum_returns'].iloc[-1])
print('Strategy:\t\t',data['strat_cum_returns'].iloc[-1])
print('Buy and Hold:\t',data_safe['cum_returns'].iloc[-1])


import calendar
ticks = [pd.to_datetime(f'2020-{i}-01') for i in np.arange(1, 13)]

t   = pd.to_datetime(data_safe.index)
t   = t.tz_localize(None)
t1  = pd.to_datetime(data.index)
t1  = t1.tz_localize(None)

cr_mr_safe = np.exp(data_safe.loc[t>=ticks[0]]['strat_log_returns'].cumsum())
cr_mr = np.exp(data.loc[t1>=ticks[0]]['strat_log_returns'].cumsum())
cr_base = np.exp(data.loc[t1>=ticks[0]]['log_returns'].cumsum())

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(cr_mr_safe, label='Mean Reversion Strategy with Safety')
ax.plot(cr_mr, label='Mean Reversion Strategy')
ax.plot(cr_base, label=f'{ticker}')
ax.set_xlabel('Date')
ax.set_ylabel('Returns (%)')
ax.set_title('Cumulative Returns for Mean Reversion and Buy and Hold Strategies')
ax.set_xlim([pd.to_datetime('2020-01-01'), data.index[-1]])
ax.set_xticks(ticks)
ax.set_xticklabels([i for i in calendar.month_abbr if i is not ''])
ax.legend()
plt.show()