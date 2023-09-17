# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 10:52:26 2023

@author: ibaldoni

Backtesting strategy for a company stock using Relative Strength Index (RSI) as
the main indicator. 
It defines a function called "RSI_normalized" that calculates the RSI indicator 
of a series. It also defines a function called "test_strategy" that takes a 
dataframe of financial data and runs a backtesting strategy.

The "test_strategy" function calculates a buy and hold strategy's performance 
and a long strategy's performance based on the RSI values. The function then 
plots several graphs showing buy and sell signals, the entry and exit points, 
and the strategy's performance.

At the end, we calculate the total profit and number of trades based on this 
given strategy.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from itertools import cycle, islice
plt.close('all')
plt.style.use('seaborn-dark') # plt.style.use('default')
pd.core.common.is_list_like = pd.api.types.is_list_like
import yfinance as yf
from datetime import date
import warnings
warnings.filterwarnings('ignore')

TAIL = 365
plot_MACD = False


def RSI_normalized(series, period):
    delta = series.diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[period-1]] = np.mean( u[:period] ) #first value is sum of avg gains
    u = u.drop(u.index[:(period-1)])
    d[d.index[period-1]] = np.mean( d[:period] ) #first value is sum of avg losses
    d = d.drop(d.index[:(period-1)])
    rs = pd.DataFrame.ewm(u, com=period-1, adjust=False).mean() / \
         pd.DataFrame.ewm(d, com=period-1, adjust=False).mean()
    return (100 - 100 / (1 + rs))/100




def test_strategy(df, estrategia,criterio,fig,axs,last_year,plots,prints):
    
    ################################################
    ################# BUY AND HOLD #################
    BnH = 100*(df.Adj_Close.iloc[-1]-df.Adj_Close.iloc[26])/df.Adj_Close.iloc[26]
    
    print(BnH,'%')
    
    df_strategy = df[[estrategia,'Adj_Close']].copy()
    df_strategy['Long'] = np.nan

    df_strategy['Buy Signal'] = np.nan
    df_strategy['Sell Signal'] = np.nan
    df_strategy['Buy'] = np.nan
    df_strategy['Sell'] = np.nan
    df_strategy['Strategy'] = np.nan

    ## Calculate the buy & sell signals for the entire period or only the last year
    if last_year == True: begin=len(df)-365
    if last_year == False: begin=26
    for x in range(begin, len(df)): 
              
        if np.isnan(df_strategy[estrategia][x]):
            df_strategy[estrategia][x]=df_strategy[estrategia][x-1]
            
        if ((df_strategy[estrategia][x] >= criterio) & (df_strategy[estrategia][x-1]< criterio) ):
            df_strategy['Long'][x] = 100
        elif ((df_strategy['Long'][x-1] == 100) & (df_strategy[estrategia][x] >= criterio)):
            df_strategy['Long'][x] = 100
        else:
            df_strategy['Long'][x] = 0   
            
        
   
        
            
        # Calculate "Buy Signal" column
        if ((df_strategy['Long'][x] == 100) & (df_strategy['Long'][x-1] == 0)):
            df_strategy['Buy Signal'][x] = df_strategy['Adj_Close'][x]
            df_strategy['Buy'][x] = df_strategy[estrategia][x]
            
        # Calculate "Sell Signal" column
        if ((df_strategy['Long'][x] == 0) & (df_strategy['Long'][x-1] == 100)):
            df_strategy['Sell Signal'][x] = df_strategy['Adj_Close'][x]
            df_strategy['Sell'][x] = df_strategy[estrategia][x]
            
    ## Calculate strategy performance
    df_strategy['Strategy'][26] = df_strategy['Adj_Close'][26]

    for x in range(27, len(df)):
        if df_strategy['Long'][x-1] == 100:
            df_strategy['Strategy'][x] = df_strategy['Strategy'][x-1]* (df_strategy['Adj_Close'][x] / df_strategy['Adj_Close'][x-1])
        else:
            df_strategy['Strategy'][x] = df_strategy['Strategy'][x-1]

    Ganancia_acumulada = (df_strategy['Strategy'][-1]-df_strategy['Strategy'][26])/df_strategy['Strategy'][26]
    if plots:

        axs[0].scatter(df.index, df_strategy['Buy Signal'],  color = 'green',  marker = '^', alpha = 1)
        axs[0].scatter(df.index, df_strategy['Sell Signal'],  color = 'red',  marker = 'v', alpha = 1)
        axs[1].scatter(df.index, df_strategy['Buy'],  color = 'green', marker = '^', alpha = 1)
        axs[1].scatter(df.index, df_strategy['Sell'],  color = 'red', marker = 'v', alpha = 1)

        try: 
            axs[2].scatter(df.index, df_strategy['Buy Signal'].mul(0.0),  color = 'green',  marker = '^', alpha = 1)
            axs[2].scatter(df.index, df_strategy['Sell Signal'].mul(0.0),  color = 'red',  marker = 'v', alpha = 1)
        except:
            print('No third axis')
        
    av_profit = 1500
    try:
        ## Number of trades
        trade_count = df_strategy['Buy Signal'].count()
        # print(trade_count)
        ## Average Profit per/trade:
        average_profit = ((df_strategy['Strategy'][-1] / df_strategy['Strategy'][26])**(1/trade_count))-1
        ## Number of days per/trade
        # print(df_strategy['Strategy'][-1] )
        # print(df_strategy['Strategy'][26])
        # print(trade_count)    
        
        # print(average_profit)
        total_days = df_strategy['Long'].count()
        # print(total_days)
        average_days = int(total_days / trade_count)
        # print(average_days)
        
        if prints:
            print('Strategy yielded ', trade_count, ' trades')
            print('Average trade lasted', average_days, ' days per trade')
            print('Average profit per trade: ', average_profit*100, '%')
        
        av_profit = average_profit*100
        # print(av_profit)
    except Exception:
      print('no trades done')
      
    return av_profit, df_strategy.Long, Ganancia_acumulada*100
    
    # return df_strategy
    
    
    
    


Cartera = ['GOOG']
#,'GOLD','NFLX','META','DIS','TSLA','AMZN','ABNB','MELI',
                # 'BKNG','MCD','ADS.DE','SBUX','NKE','KO','BMW.DE',
                # 'CTRA','PXD','OXY','MPC','V','PYPL','BRK-B','MA',
                # 'JNJ','AIR.DE','LHA.DE','DE','BA','GLOB','AMD','AAPL',
                # 'TSM','MU','INTC','ZM','MSFT','ASML','CSCO','ADBE','CRM',
                # 'NA9.DE','MOH.DE','BMW.DE','^IXIC','^GSPC','^DJI','^GDAXI']
     

def run_report(Ichimoku=False):   
    resultado = pd.DataFrame(columns=['Ticker','Profit']) 
    for Activo in Cartera:
        print(Activo)
        df = yf.download(Activo,period='4y')#,start='2019-09-26')
        
        name = yf.Ticker(Activo).info
        Name = name['shortName']
        # print(Name)
        df.rename(columns={'Adj Close':'Adj_Close'}, inplace=True) 
        
        high_9 = df['High'].rolling(window= 9).max()
        low_9 = df['Low'].rolling(window= 9).min()
        
        df['ema12']         = df.Adj_Close.ewm(span=12, adjust=False).mean()
        df['ema26']         = df.Adj_Close.ewm(span=26, adjust=False).mean()
        df['MACD_1']        = (df.ema12 - df.ema26)#/df.ema12
        df['Signal_line']   = df.MACD_1.ewm(span=9,adjust=False).mean()
        df['MACD']          = (df.MACD_1-df.Signal_line)
        
        df['RSI']           = RSI_normalized(df.Adj_Close, 14)
        
        df['LogReturn']     = np.log(df['Adj_Close'] / df['Adj_Close'].shift(1))
        
        
        
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
        tmp = df[['Base_Line','Conversion_Line','Lagging_span','Adj_Close','Leading_Span_a','Leading_Span_b']].tail(TAIL)
        
        my_colors = list(islice(cycle(['m', 'orange','red','b', 'g', 'r']), None, len(df)))
        
        my_style = list(islice(cycle(['-', '-', '--', '-', '-','-']), None, len(df)))
                

        
        fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, gridspec_kw={'height_ratios': [1,1]})
        a1 = tmp.plot(figsize=(8,8),color=my_colors,style=my_style,ax=axes[0])
        a1.legend(["Base Line","Conversion line","Lagging"]);
        # a2 = df.MACD.tail(TAIL).plot(ax=axes[1],alpha=0.01)
        # a2 = df.RSI.tail(TAIL).plot(ax=axes[1])
        # a2.set_ylabel('MACD')
        # a2.axhline(y=0.002,linewidth=0.5,color='k')
        a2 = df.LogReturn.tail(TAIL).plot(ax=axes[1],alpha=0.5)

        
        if plot_MACD:
            for i in range(TAIL,0,-1):
                
                if df.MACD[len(df)-i]>0: colour_hist = 'g'
                if df.MACD[len(df)-i]<0: colour_hist = 'r'
                a2.bar(df.index[len(df)-i],df.MACD[len(df)-i],color=colour_hist)

        
    
      
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

    


        df['Posicion'] = df.Adj_Close
        
        for i in range(0,len(df)-26):
            cond1 = (df.Lagging_span.iloc[-27-i] > df.Leading_Span_a.iloc[-27-i])
            cond2 = (df.Lagging_span.iloc[-27-i] > df.Leading_Span_b.iloc[-27-i])
            cond3 = (df.Adj_Close.iloc[-1-i] > df.Leading_Span_a.iloc[-1-i])
            cond4 = (df.Adj_Close.iloc[-1-i] > df.Leading_Span_b.iloc[-1-i])
            cond5 = (df.Conversion_Line.iloc[-1-i] > df.Base_Line.iloc[-1-i])
            cond6 = ((high_52 + low_52) /2).iloc[-1-i]<((df['Conversion_Line'] + df['Base_Line']) / 2).iloc[-1-i]
            
            cond7 = (df.Lagging_span.iloc[-27-i] < df.Leading_Span_a.iloc[-27-i])
            cond8 = (df.Lagging_span.iloc[-27-i] < df.Leading_Span_b.iloc[-27-i])
            cond9 = (df.Adj_Close.iloc[-1-i] < df.Leading_Span_a.iloc[-1-i]) 
            con10 = (df.Adj_Close.iloc[-1-i] < df.Leading_Span_b.iloc[-1-i])
            con11 = (df.Conversion_Line.iloc[-1-i] < df.Base_Line.iloc[-1-i])
            con12 = ((high_52 + low_52) /2).iloc[-1-i] > ((df['Conversion_Line'] + df['Base_Line']) / 2).iloc[-1-i]
            
            cond_MACD = ((df.MACD[-1-i]>0))
            
            cond_RSI  = (df.RSI[-1-i]>0.29 and df.RSI[-1-i]<0.71) 
            
            if Ichimoku:
                if cond1 and cond2 and cond6:
                #and cond2 and cond3 and cond4 and cond5 and cond6: 
                    comparison='Long'
                    condicion = 'Long'
                    df['Posicion'].iloc[-i-1] = 1
                    
                elif cond7 and cond8 and cond9 and con10 and con11 and con12: 
                    condicion = 'Short'  
                    comparison='Short'
                    df['Posicion'].iloc[-i-1] = -1
                    
                else:
                    comparison='SinDefinir'
                    df['Posicion'].iloc[-i-1] = 0
            
            if cond_RSI:
                # print(df.RSI[-1-i])
            #and cond2 and cond3 and cond4 and cond5 and cond6: 
                comparison='Long'
                condicion = 'Long'
                df['Posicion'].iloc[-i-1] = 1
            else:
                df['Posicion'].iloc[-i-1] = 0
                
                 
        
        
        #### BUY AND HOLD TEST
        for i in range(0,len(df)-26):    
            if 1==1:
                comparison='Long'
                condicion = 'Long'
                df['Posicion'].iloc[-i-1] = 1
                
        df.Posicion.iloc[0:26] = 0


        
        strategy = 'Posicion'
        criteria = 0.5
        avg_profit_ref, strat, ganancia = test_strategy(df, strategy,criteria,fig,axes,last_year = False,
                                   plots=False,prints=False)
        
        strat.tail(TAIL).plot(ax=axes[0])
        
        df2 = pd.DataFrame([[Activo, ganancia]],columns=list(resultado))
        
        resultado = resultado.append(df2)
    print(resultado)

if date.today().weekday() != 6:
    run_report()



