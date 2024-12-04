import time
from datetime import datetime
import pandas as pd
from public_endpoints import get_kline_data
from supertrend import get_supertrend
import numpy as np

def append_to_df(df, high, low, close):
    # Get the current timestamp for the new row
    timestamp = pd.to_datetime('now')  # You can change this to a specific timestamp if needed
    
    # Prepare the new data to append
    data = {'High': float(high), 'Low': float(low), 'Close': float(close)}
    
    # Create a new DataFrame with the new row and correct timestamp
    new_row = pd.DataFrame([data], index=[timestamp])
    
    # Append the new row to the existing DataFrame
    df = pd.concat([df, new_row])
    
    # Ensure the DataFrame is sorted by the Timestamp index (ascending order)
    df.reset_index(drop=True, inplace=True)
    
    return df

def make_init_data(contract_pair):
    # Fetching the kline data
    info = get_kline_data(contract_pair, limit=25)
    
    data = []
    
    # Looping through the fetched data
    for i in info:
        high = float(i['high'])
        low = float(i['low'])
        close = float(i['close'])
        data.append({'High': high, 'Low': low, 'Close': close})
    
    # Create the DataFrame
    df = pd.DataFrame(data)
    
    # Reset the index to 0, 1, 2, 3, ... (default integer index)
    df.reset_index(drop=True, inplace=True)
    
    return df


def call_every_one_minute(contract_pair):
    info = get_kline_data(contract_pair)
    
    print(f"Data fetched at: {datetime.now()}")

    list_return = [float(info[0]['high']), float(info[0]['low']), float(info[0]['close'])]
    print(list_return)
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
        df = df.iloc[rows_to_delete:].reset_index(drop=True)  # Delete top rows and reset index
    return df

if __name__ == "__main__":
    ticker = 'BTCUSDT'
    df = make_init_data(ticker)
    print("Initial DataFrame:")
    
    print(df)

    df['st'], df['s_upt'], df['st_dt'], df['atr'] = get_supertrend(df['High'], df['Low'], df['Close'], 10, 3)
    print(df)
            

