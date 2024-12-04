
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import csv
import warnings

warnings.filterwarnings("ignore")

start = "2024-11-25"
end = "2024-11-26"
qty = 0.01
fees = 0.0002

try:
    df = yf.download("BTC-USD", start = start, end = end, interval='1m')
except:
    print("Data not Going")

def get_supertrend(high, low, close, lookback, multiplier):
    
    # ATR
    
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)

    print(tr)
    atr = tr.ewm(lookback).mean()
    
    # H/L AVG AND BASIC UPPER & LOWER BAND
    
    hl_avg = (high + low) / 2
    upper_band = (hl_avg + multiplier * atr).dropna()
    lower_band = (hl_avg - multiplier * atr).dropna()
    
    # FINAL UPPER BAND
    final_bands = pd.DataFrame(columns = ['upper', 'lower'])
    final_bands.iloc[:,0] = [x for x in upper_band - upper_band]
    final_bands.iloc[:,1] = final_bands.iloc[:,0]
    for i in range(len(final_bands)):
        if i == 0:
            final_bands.iloc[i,0] = 0
        else:
            if (upper_band[i] < final_bands.iloc[i-1,0]) | (close[i-1] > final_bands.iloc[i-1,0]):
                final_bands.iloc[i,0] = upper_band[i]
            else:
                final_bands.iloc[i,0] = final_bands.iloc[i-1,0]
    
    # FINAL LOWER BAND
    
    for i in range(len(final_bands)):
        if i == 0:
            final_bands.iloc[i, 1] = 0
        else:
            if (lower_band[i] > final_bands.iloc[i-1,1]) | (close[i-1] < final_bands.iloc[i-1,1]):
                final_bands.iloc[i,1] = lower_band[i]
            else:
                final_bands.iloc[i,1] = final_bands.iloc[i-1,1]
    
    # SUPERTREND
    
    supertrend = pd.DataFrame(columns = [f'supertrend_{lookback}'])
    supertrend.iloc[:,0] = [x for x in final_bands['upper'] - final_bands['upper']]
    
    for i in range(len(supertrend)):
        if i == 0:
            supertrend.iloc[i, 0] = 0
        elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 0] and close[i] < final_bands.iloc[i, 0]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 0]
        elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 0] and close[i] > final_bands.iloc[i, 0]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 1]
        elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 1] and close[i] > final_bands.iloc[i, 1]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 1]
        elif supertrend.iloc[i-1, 0] == final_bands.iloc[i-1, 1] and close[i] < final_bands.iloc[i, 1]:
            supertrend.iloc[i, 0] = final_bands.iloc[i, 0]
    
    supertrend = supertrend.set_index(upper_band.index)
    supertrend = supertrend.dropna()[1:]
    
    # ST UPTREND/DOWNTREND
    
    upt = []
    dt = []
    close = close.iloc[len(close) - len(supertrend):]

    for i in range(len(supertrend)):
        if close[i] > supertrend.iloc[i, 0]:
            upt.append(supertrend.iloc[i, 0])
            dt.append(np.nan)
        elif close[i] < supertrend.iloc[i, 0]:
            upt.append(np.nan)
            dt.append(supertrend.iloc[i, 0])
        else:
            upt.append(np.nan)
            dt.append(np.nan)
            
    st, upt, dt = pd.Series(supertrend.iloc[:, 0]), pd.Series(upt), pd.Series(dt)
    upt.index, dt.index = supertrend.index, supertrend.index
    
    return st, upt, dt


df['st'], df['s_upt'], df['st_dt'] = get_supertrend(df['High']['BTC-USD'], df['Low']['BTC-USD'], df['Close']['BTC-USD'], 10, 3)


st = list(df['st'])
st_upt = list(df['s_upt'])
st_dt = list(df['st_dt'])

signal = [0]
for i in range(1, len(st_upt)):
    prev = st_upt[i - 1]
    curr = st_upt[i]

    if np.isnan(prev) and not np.isnan(curr):  # Transition from NaN to a number
        signal.append(1)
    elif not np.isnan(prev) and np.isnan(curr):  # Transition from a number to NaN
        signal.append(-1)
    else:
        signal.append(0)

close = list(df['Close']['BTC-USD'])

pnl = []
def buy_side_testing(signal, close):
    buy_price = 0
    close_price = 0
    status = 0

    for i in range(len(signal)):
        close_price = close[i]
        if signal[i] == 1:
            buy_price = close[i]
            status = 1

        elif signal[i] == -1 and status == 1:
            close_price = st_upt[i-1]
            trade_pnl = (close_price - buy_price) * qty
            status = 0
            print("Time: ", df.index[i])
            print("Buy Price: ", buy_price)
            print("Close Price: ", close_price)
            print("Profit: ", trade_pnl)
            print("-------------------------------------------")
            pnl.append(trade_pnl)



def sell_side_testing(signal, close):
    sell_price = 0
    close_price = 0
    status = 0
    for i in range(len(signal)):
        close_price = close[i]
        if signal[i] == -1:
            sell_price = close[i]
            status = 1
        elif signal[i] == 1 and status == 1:
            close_price = st_dt[i-1]
            trade_pnl = (sell_price - close_price) * qty

            print("Time: ", df.index[i])
            print("Sell Price: ", sell_price)
            print("Close Price: ", close_price)
            print("Profit: ", trade_pnl)
            print("-------------------------------------------")
            pnl.append(trade_pnl)
        
     
buy_side_testing(signal, close)
sell_side_testing(signal, close)


def volume_and_fees(price, qty, fees):
    return [price * qty * len(pnl) * 2, price * qty * len(pnl) * 2 * fees]


gross_pnl = sum(pnl)
fees_given = volume_and_fees(100000, qty, fees)[1]
net_pnl = gross_pnl - fees_given
trades_taken = len(pnl)
volume = volume_and_fees(100000, qty, fees)[0]

def insert_into_csv(start, gross_pnl, fees_given, net_pnl, trades_taken, volume):

    data = [
        ["Day", "Gross PNL", "Fees", "Net PNL", "Trades Taken", "Volume"],
        [start, gross_pnl, fees_given, net_pnl, trades_taken, volume]  
    ]

    csv_file = "trade_summary.csv"

    # Check if the file exists, and if not, create it with header
    file_exists = False
    try:
        with open(csv_file, 'r'):
            file_exists = True
    except FileNotFoundError:
        pass

    # Append data to the CSV file
    with open(csv_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            # Write the header only if the file doesn't exist
            writer.writerow(data[0])
        writer.writerow(data[1])

    # Optional: Print confirmation or results
    print(f"Data written to {csv_file}")

#insert_into_csv(start, gross_pnl, fees_given, net_pnl, trades_taken, volume)

print("Day: ", start)
print("Gross PNL: ", gross_pnl)
print("Fees: ", fees_given)
print("Net PNL: ", net_pnl)
print("Trades Taken: ", trades_taken)
print("Volume: ", volume)