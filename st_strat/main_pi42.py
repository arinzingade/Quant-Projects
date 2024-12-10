
import time
from datetime import datetime
import pandas as pd
import numpy as np
import warnings
import os
from dotenv import load_dotenv
from pi42 import Pi42API

from helpers import make_init_data, is_buy_signal, is_sell_signal, append_to_df, call_every_one_minute
from supertrend import get_supertrend

load_dotenv()


warnings.filterwarnings('ignore')
STATUS = "neutral"

qty = int(os.getenv('QTY'))
symbol = os.getenv('SYMBOL')
api_secret = os.getenv('API_SECRET_PI42')
api_key = os.getenv('API_KEY_PI42')

print(api_secret)
print(api_key)
print(qty)

frequency = 750
duration = 300

client = Pi42API(api_secret, api_key)
print(client)

if __name__ == "__main__":
    
    symbol = symbol.upper()
    print("Symbol: ", symbol)
    ticker = symbol.upper()
    print("Ticker: ", ticker)

    df = make_init_data(ticker.upper())
    print("Initial DataFrame:")
    print(df)

    while True:
        if datetime.now().second == 5:

            high, low, close = call_every_one_minute(ticker)
            df = append_to_df(df, high, low, close)

            df['st'], df['st_upt'], df['st_dt'], df['atr'] = get_supertrend(df['High'], df['Low'], df['Close'], 10, 3)

            print(df)

            print(STATUS)

            if STATUS == "neutral":
                if is_buy_signal(df):
                    client.place_order(symbol, 'MARKET', qty, 'BUY')
                    STATUS = "long"


                elif is_sell_signal(df):
                    client.place_order(symbol, 'MARKET', qty, 'SELL')
                    STATUS = "short"

                elif STATUS == "short":
                    if is_buy_signal(df):
                        client.place_order(symbol, 'MARKET', qty, 'BUY')
                        time.sleep(2)
                        client.place_order(symbol, 'MARKET', qty, 'BUY')
                        STATUS = "long"
                
                elif STATUS == "long":
                    if is_sell_signal(df):
                        client.place_order(symbol, 'MARKET', qty, 'SELL')
                        time.sleep(2)
                        client.place_order(symbol, 'MARKET', qty, 'SELL')
                        STATUS = "short"
                
            time.sleep(55)
