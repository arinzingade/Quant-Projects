import time
from datetime import datetime
import pandas as pd
from public_endpoints import get_kline_data
from supertrend import get_supertrend
import numpy as np
import warnings
import os
from coinswitch import place_order, cancel_all_orders
from coin_class import ApiTradingClient

warnings.filterwarnings('ignore')

STATUS = "neutral"
qty = float(os.getenv('QTY'))
fees_pct = float(os.getenv('FEES_PCT'))
fees_mult = int(os.getenv('FEES_MULT'))
symbol = str(os.getenv('SYMBOL'))
secret_key = os.getenv('SECRET')
api_key = os.getenv('API_KEY')

api_trading_client = ApiTradingClient(secret_key, api_key)

init_price = 0

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


def thresh_points(current_price, qty, fees_pct, mult):
    fees_taker = fees_pct * current_price * 2 * qty
    profit_target = fees_taker * mult
    profit_target_pct = profit_target / (current_price * qty)

    points = current_price * profit_target_pct

    return points

def get_open_orders_count(symbol):
    payload = {
        "symbol": symbol,
        "exchange": "EXCHANGE_2",  
    }

    response = (api_trading_client.futures_open_orders(payload=payload))
    count = len(response['data']['orders'])

    return count

if __name__ == "__main__":

    df = make_init_data(symbol.upper())
    print("Initial DataFrame:")
    print(df)

    print("Qty: ", qty)

    df['st'], df['st_upt'], df['st_dt'], df['atr'] = get_supertrend(df['High'], df['Low'], df['Close'], 10, 3)

    while True:
        if datetime.now().second == 5:

            high, low, close = call_every_one_minute(symbol.upper())
            df = append_to_df(df, high, low, close)
            
            df['st'], df['st_upt'], df['st_dt'], df['atr'] = get_supertrend(df['High'], df['Low'], df['Close'], 10, 3)
            
            current_price = list(df['Close'])[len(df['Close']) - 1]
            thresh = thresh_points(current_price, qty, fees_pct, fees_mult)

            print(df)

            print("Init Price: ", init_price)
            print("Current Price is: ", current_price)
            print("Thresh Points are: ", thresh)

            print(STATUS)

            open_orders_count = get_open_orders_count(symbol)

            if open_orders_count == 0:
                STATUS = "neutral"
                print("STATUS updated to Neutral")

            if STATUS == "neutral":
                if is_buy_signal(df):
                    place_order(symbol, "BUY", "MARKET", qty)
                    time.sleep(1)
                    place_order(symbol, 'SELL', 'LIMIT', qty, current_price + thresh)
                    STATUS = "long"

                elif is_sell_signal(df):
                    place_order(symbol, "SELL", "MARKET", qty)
                    time.sleep(1)
                    place_order(symbol, 'BUY', 'LIMIT', qty, current_price - thresh)
                    STATUS = "short"

            elif STATUS == "short":
                if is_buy_signal(df):
                    place_order(symbol, "BUY", "MARKET", qty)

                    time.sleep(1)
                    place_order(symbol, "BUY", "MARKET", qty)
                    cancel_all_orders()
                    time.sleep(1)
                    place_order(symbol, 'SELL', 'LIMIT', qty, current_price + thresh)
                    STATUS = "long"

            elif STATUS == "long":
                if is_sell_signal(df):
                    place_order(symbol, "SELL", "MARKET", qty)

                    time.sleep(1)
                    place_order(symbol, "SELL", "MARKET", qty)
                    cancel_all_orders()

                    time.sleep(1)
                    place_order(symbol, 'BUY', 'LIMIT', qty, current_price - thresh)
                    STATUS = "short"
            
            time.sleep(5)