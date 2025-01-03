
import pandas as pd
import numpy as np
from public_endpoints import get_kline_data
from datetime import datetime
import time

def append_to_df(df, high, low, close):
    timestamp = pd.to_datetime('now')    
    data = {'Timestamp': timestamp, 'High': float(high), 'Low': float(low), 'Close': float(close)}
    
    new_row = pd.DataFrame([data])
    
    df = pd.concat([df, new_row], ignore_index=True)
    
    df.set_index('Timestamp')
    df.index = pd.to_datetime(df.index)
    
    return df

def make_init_data(contract_pair):
    # Fetching the kline data
    info = get_kline_data(contract_pair, limit=20)
    
    data = []

    for i in info:
        high = float(i['high'])
        low = float(i['low'])
        close = float(i['close'])
        
        timestamp = pd.to_datetime(int(i['startTime']), unit='ms')
        
        data.append({'Timestamp': timestamp, 'High': high, 'Low': low, 'Close': close})
    
    # Create the DataFrame
    df = pd.DataFrame(data)
    df.set_index('Timestamp')
    df.index = pd.to_datetime(df.index)
    
    return df

def call_every_one_minute(contract_pair):
    info = get_kline_data(contract_pair)
    
    print(f"Data fetched at: {datetime.now()}")

    list_return = [float(info[0]['high']), float(info[0]['low']), float(info[0]['close'])]

    return list_return

def run_scheduled_task(contract_pair):
    while True:
        now = datetime.now()
        if now.second == 5:
            return call_every_one_minute(contract_pair)
        while datetime.now().second == 5:
            time.sleep(1)

def manage_dataframe_size(df, max_size = 30, rows_to_delete = 15):
    if len(df) > max_size:
        df = df.iloc[rows_to_delete:]
    return df

def is_buy_signal(df):
    global STATUS

    st_upt = list(df['st_upt'])
    length = len(st_upt)

    curr = st_upt[length-1]
    prev = st_upt[length-2]

    if pd.isna(prev) and curr > 0:
        print("BUY SIGNAL")
        STATUS = "long"
        return True

def is_sell_signal(df):
    global STATUS

    st_dt = list(df['st_dt'])
    length = len(st_dt)

    curr = st_dt[length-1]
    prev = st_dt[length-2]

    if pd.isna(prev) and curr > 0:
        print("SELL SIGNAL")
        STATUS = "short"
        return True