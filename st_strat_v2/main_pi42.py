import time
from datetime import datetime
from supertrend import get_supertrend
import warnings
import os
from coinswitch import place_order, cancel_all_orders
from pi42 import Pi42API
from helpers import (
    make_init_data,
    call_every_one_minute,
    thresh_points,
    append_to_df,
    get_open_orders_count,
    is_buy_signal,
    is_sell_signal
)
from state import StateManager

warnings.filterwarnings('ignore')

status = StateManager()

qty = float(os.getenv('QTY'))
fees_pct = float(os.getenv('FEES_PCT'))
fees_mult = int(os.getenv('FEES_MULT'))
symbol = str(os.getenv('SYMBOL'))
secret_key = os.getenv('API_SECRET_PI42')
api_key = os.getenv('API_KEY_PI42')

api_trading_client = Pi42API(secret_key, api_key)

init_price = 0

if __name__ == "__main__":
    df = make_init_data(symbol.upper())
    print("Initial DataFrame:")
    print(df)

    print("Qty: ", qty)

    df['st'], df['st_upt'], df['st_dt'], df['atr'] = get_supertrend(df['High'], df['Low'], df['Close'], 10, 3)

    while True:
        if datetime.now().second == 5:
            
            for attempt in range(3):
                try:
                    high, low, close = call_every_one_minute(symbol.upper())
                    break
                except:
                    print(f"Retrying... ({attempt + 1})")
                    time.sleep(10)  

                
            df = append_to_df(df, high, low, close)
            
            df['st'], df['st_upt'], df['st_dt'], df['atr'] = get_supertrend(df['High'], df['Low'], df['Close'], 10, 3)
            
            current_price = list(df['Close'])[len(df['Close']) - 1]
            thresh = thresh_points(current_price, qty, fees_pct, fees_mult)

            print(df)

            print("Init Price: ", init_price)
            print("Current Price is: ", current_price)
            print("Thresh Points are: ", thresh)

            print(status)

            open_orders_count = len(api_trading_client.get_open_orders())

            if open_orders_count == 0 or open_orders_count == 1:
                api_trading_client.cancel_all_orders()
                status.set_status("neutral")
                print("STATUS updated to Neutral")  

            if status.get_status() == "neutral":
                if is_buy_signal(df):
                    api_trading_client.cancel_all_orders()
                    api_trading_client.place_order(symbol, "BUY", "MARKET", qty)
                    time.sleep(2)
                    api_trading_client.place_order(symbol, 'SELL', 'LIMIT', qty, current_price + thresh)
                    api_trading_client.place_order(symbol, 'SELL', 'STOP_MARKET', qty, current_price - thresh)
                    status.set_status("long")

                elif is_sell_signal(df):
                    api_trading_client.cancel_all_orders()
                    api_trading_client.place_order(symbol, "SELL", "MARKET", qty)
                    time.sleep(2)
                    api_trading_client.place_order(symbol, 'BUY', 'LIMIT', qty, current_price - thresh)
                    api_trading_client.place_order(symbol, 'BUY', 'STOP_MARKET', qty, current_price + thresh)
                    status.set_status("short")

            elif status.get_status() == "short":
                if is_buy_signal(df):
                    api_trading_client.place_order(symbol, "BUY", "MARKET", qty)

                    time.sleep(2)
                    api_trading_client.place_order(symbol, "BUY", "MARKET", qty)
                    api_trading_client.cancel_all_orders()
                    time.sleep(2)
                    api_trading_client.place_order(symbol, 'SELL', 'LIMIT', qty, current_price + thresh)
                    api_trading_client.place_order(symbol, 'SELL', 'STOP_MARKET', qty, current_price - thresh)
                    status.set_status("long")

            elif status.get_status() == "long":
                if is_sell_signal(df):
                    api_trading_client.place_order(symbol, "SELL", "MARKET", qty)

                    time.sleep(2)
                    api_trading_client.place_order(symbol, "SELL", "MARKET", qty)
                    api_trading_client.cancel_all_orders()

                    time.sleep(2)
                    api_trading_client.place_order(symbol, 'BUY', 'LIMIT', qty, current_price - thresh)
                    api_trading_client.place_order(symbol, 'BUY', 'STOP_MARKET', qty, current_price + thresh)
                    status.set_status("short")
            
            time.sleep(55)