#Coded by Rajandran R - www.marketcalls.in / www.openalgo.in

import yfinance as yf
import pandas as pd
import numpy as np
import time
import threading
import os


def Supertrend(df, atr_period, multiplier):
    high = df['high']
    low = df['low']
    close = df['close']
    
    # calculate ATR
    price_diffs = [high - low, high - close.shift(), close.shift() - low]
    true_range = pd.concat(price_diffs, axis=1)
    true_range = true_range.abs().max(axis=1)
    atr = true_range.ewm(alpha=1/atr_period, min_periods=atr_period).mean()
    
    hl2 = (high + low) / 2
    final_upperband = upperband = hl2 + (multiplier * atr)
    final_lowerband = lowerband = hl2 - (multiplier * atr)
    
    supertrend = [True] * len(df)
    
    for i in range(1, len(df.index)):
        curr, prev = i, i-1
        
        if close.iloc[curr] > final_upperband.iloc[prev]:
            supertrend[curr] = True
        elif close.iloc[curr] < final_lowerband.iloc[prev]:
            supertrend[curr] = False
        else:
            supertrend[curr] = supertrend[prev]
            
            if supertrend[curr] == True and final_lowerband.iloc[curr] < final_lowerband.iloc[prev]:
                final_lowerband.iat[curr] = final_lowerband.iat[prev]
            if supertrend[curr] == False and final_upperband.iloc[curr] > final_upperband.iloc[prev]:
                final_upperband.iat[curr] = final_upperband.iat[prev]

        if supertrend[curr] == True:
            final_upperband.iat[curr] = np.nan
        else:
            final_lowerband.iat[curr] = np.nan
    
    return pd.DataFrame({
        'Supertrend': supertrend,
        'Final Lowerband': final_lowerband,
        'Final Upperband': final_upperband
    }, index=df.index)

