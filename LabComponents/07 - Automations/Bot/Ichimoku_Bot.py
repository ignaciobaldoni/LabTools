# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 18:09:14 2023

@author: ignacio

This Python script analyzes the stock market performance of a list of companies 
contained in the 'Cartera' list, and it generates a chart with a technical 
analysis of each stock. The technical analysis includes the MACD indicator, 
which is a momentum oscillator that shows the relationship between two moving 
averages of an asset's price, and the Ichimoku Cloud, which is a Japanese charting 
technique that uses a combination of indicators to provide trading signals.

The script uses the 'yfinance' package to download historical prices for each 
stock in the 'Cartera' list. It then calculates the MACD and Ichimoku Cloud 
indicators for each stock and generates a chart that shows these indicators for 
the last 70 days of trading. The chart is divided into two sections: the top 
section shows the Ichimoku Cloud, and the bottom section shows the MACD.

The script also sets the style of the chart to 'seaborn-dark'. It then uses a 
cycle iterator to generate a list of colors and styles for the different lines 
in the chart. Finally, the script generates a bar plot that shows the MACD 
histogram for the last 70 days of trading.

The code also sends a message to a Telegram bot after the conditions are met.
(For this, the user needs to make its own telegram bot).

It checks f the comparison between the two conditions is not equal, meaning the 
condition has changed. If this is true, then it saves a plot of the data in an 
image file and sends it along with a message to a Telegram chat using the 
Telegram API.

The code then waits for 0.5 seconds and prints the comparison and a separator 
line. If it is not Sunday, it will execute the run_report() function, and at 
the end, it sends a message to the same Telegram chat to notify that the script 
has been executed, for keeping track of the script's activity.

"""

import pandas as pd
import matplotlib.pyplot as plt
from itertools import cycle, islice

import requests

#  pip install yfinance --upgrade

plt.close('all')
plt.style.use('seaborn-dark')
# plt.style.use('default')
pd.core.common.is_list_like = pd.api.types.is_list_like

import time
import yfinance as yf
from datetime import date

Cartera = ['GOOG','GOLD','NFLX','META','DIS','TSLA','AMZN','ABNB','MELI',
              'BKNG','MCD','ADS.DE','SBUX','NKE','KO',
              'CTRA','PXD','OXY','MPC','V','PYPL','BRK-B','MA',
              'JNJ','AIR.DE','LHA.DE','DE','BA','GLOB','AMD','AAPL',
              'TSM','MU','INTC','ZM','MSFT','ASML','CSCO','ADBE','CRM',
              'NA9.DE','MOH.DE','BMW.DE','^IXIC','^GSPC','^DJI','^GDAXI','YPF','GGAL','SUPV']




def run_report():     
    for Activo in Cartera:
        print(Activo)
        df = yf.download(Activo,period = '4y', )
        
        # name = yf.Ticker(Activo).info
        # Name = name['shortName']
        # if '&' in Name: Name = 'SP 500'
        # print(Name)
        
        Name = Activo
        df.rename(columns={'Adj Close':'Adj_Close'}, inplace=True) 
        
        high_9 = df['High'].rolling(window= 9).max()
        low_9 = df['Low'].rolling(window= 9).min()
        
        df['ema12']         = df.Adj_Close.ewm(span=12, adjust=False).mean()
        df['ema26']         = df.Adj_Close.ewm(span=26, adjust=False).mean()
        df['MACD_1']        = (df.ema12 - df.ema26)#/df.ema12
        df['Signal_line']   = df.MACD_1.ewm(span=9,adjust=False).mean()
        df['MACD']          = (df.MACD_1-df.Signal_line) 
        
        
        
        df['Conversion_Line'] = (high_9 + low_9) /2
        
        high_26 = df['High'].rolling(window= 26).max()
        low_26 = df['Low'].rolling(window= 26).min()
        df['Base_Line'] = (high_26 + low_26) /2
            
        df['Leading_Span_a'] = ((df['Conversion_Line'] + df['Base_Line']) / 2).shift(26)
        
        high_52 = df['High'].rolling(window= 52).max()
        low_52 = df['Low'].rolling(window= 52).min()
        df['Leading_Span_b'] = ((high_52 + low_52) /2).shift(26)
        
        # most charting softwares dont plot this line
        df['Lagging_span'] = df['Adj_Close'].shift(-26) #sometimes -26 
        
        Ichi_future1 = ((df['Conversion_Line'] + df['Base_Line']) / 2).iloc[-1]
        Ichi_future2 = ((high_52 + low_52) /2).iloc[-1]
        
        Future = ['r' if Ichi_future2>Ichi_future1 else 'g']
        tmp = df[['Base_Line','Conversion_Line','Lagging_span','Adj_Close','Leading_Span_a','Leading_Span_b']].tail(70)
        
        my_colors = list(islice(cycle(['m', 'orange','red','b', 'g', 'r']), None, len(df)))
        
        my_style = list(islice(cycle(['-', '-', '--', '-', '-','-']), None, len(df)))
        
        # a1 = tmp.plot(figsize=(8,8),color=my_colors,style=my_style)
        

        
        fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, gridspec_kw={'height_ratios': [3,1]})
        a1 = tmp.plot(figsize=(8,8),color=my_colors,style=my_style,ax=axes[0])
        a1.legend(["Base Line","Conversion line","Lagging"]);
        a2 = df.MACD.tail(70).plot(ax=axes[1],alpha=0.01)
        a2.set_ylabel('MACD')
        a2.axhline(y=0.002,linewidth=0.5,color='k')

        
        for i in range(70,0,-1):#df.MACD.tail(70):
            
            if df.MACD[len(df)-i]>0: colour_hist = 'g'
            if df.MACD[len(df)-i]<0: colour_hist = 'r'
            # print(df.MACD.iloc[len(df)-i])
            a2.bar(df.index[len(df)-i],df.MACD[len(df)-i],color=colour_hist)
            # (prices.index[i], hist[i], color = '#ef5350')
        
    
      
        for line in a1.get_lines():
            if (line.get_label() == 'Leading_Span_b' or line.get_label() == 'Leading_Span_a'):
                line.set_linewidth(0.01)
            if (line.get_label() == 'Conversion' or line.get_label() == 'Base_Line'):
                line.set_linewidth(0.75)
            if (line.get_label() == 'Lagging_span' or line.get_label() == 'Adj_Close'):
                line.set_linewidth(1.75)
           
        
    

        a1.fill_between(tmp.index, tmp.Leading_Span_a, tmp.Leading_Span_b,alpha=.25,color=Future)
        a1.set_title(f'{Activo}')
        a1.set_ylabel('Price [USD]')   
        plt.subplots_adjust(wspace=0, hspace=0.05)
    
        comparison = [0,0]    
        condicion = [0,0]
        ##### LONG or SHORT signal
        for i in range(0,2):
            
            if i==1: dia = 'ayer'
            if i==0: dia = 'hoy'
            if (df.Lagging_span.iloc[-27-i] > df.Leading_Span_a.iloc[-27-i]) and \
                (df.Lagging_span.iloc[-27-i] > df.Leading_Span_b.iloc[-27-i]) and\
                    (df.Adj_Close.iloc[-1-i] > df.Leading_Span_a.iloc[-1-i]) and \
                (df.Adj_Close.iloc[-1-i] > df.Leading_Span_b.iloc[-1-i]) and\
                    (df.Conversion_Line.iloc[-1-i] > df.Base_Line.iloc[-1-i]) and\
                        ((high_52 + low_52) /2).iloc[-1-i]<((df['Conversion_Line'] + df['Base_Line']) / 2).iloc[-1-i]: 
                # print(f'Condicion {dia}: LONG')
                comparison[i]='Long'
                condicion[i]= 'Long'
            elif (df.Lagging_span.iloc[-27-i] < df.Leading_Span_a.iloc[-27-i]) and \
                (df.Lagging_span.iloc[-27-i] < df.Leading_Span_b.iloc[-27-i]) and\
                    (df.Adj_Close.iloc[-1-i] < df.Leading_Span_a.iloc[-1-i]) and \
                (df.Adj_Close.iloc[-1-i] < df.Leading_Span_b.iloc[-1-i]) and\
                    (df.Conversion_Line.iloc[-1-i] < df.Base_Line.iloc[-1-i]) and\
                        ((high_52 + low_52) /2).iloc[-1-i] > ((df['Conversion_Line'] + df['Base_Line']) / 2).iloc[-1-i]: 
                condicion[i]= 'Short'        
                comparison[i]='Short'
            else:
                # print(f'El día de {dia} sin condicion definida')
                condicion[i]= 'Sin definir'
                comparison[i]='SinDefinir'
            
        
        if (comparison[0] != comparison[1]):# or (comparison[0]=='Long' and comparison[1]=='Long'):
            print('Mensaje de Telegram!')
            plt.savefig(f'{Activo}_ichi.png',bbox_inches='tight')
            condicion = 'De '+condicion[1]+' a '+condicion[0]
            
            import requests
            TOKEN = '5823078266:AAFwcY-uswXhoOMmSLRzyK0wyI-0-Rw3nss'
            chat_id = "891176226"
            message = f"Cambio para {Activo} \n"+f"{Name}\n\n"+\
                f"{condicion}"
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}&"
            requests.get(url).json() # this sends the message
            
            img = open(f'C:\\Users\\ibaldoni\\Desktop\\Bot\\{Activo}_ichi.png', 'rb')
            url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto?chat_id={chat_id}'
            requests.get(url, files={'photo': img}).json()                     
        time.sleep(0.5)
                
        print(comparison)
        print('------------------------------------------------------------------')    
           
 
# If today is Sunday (aka 6 of 6), then do not run the report
TOKEN = '5823078266:AAFwcY-uswXhoOMmSLRzyK0wyI-0-Rw3nss'
chat_id = "891176226"

if date.today().weekday() != 6:
    run_report()

message = "Script executed"
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}&"
requests.get(url).json() # this sends the message