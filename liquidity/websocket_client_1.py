import socketio
from dotenv import load_dotenv
import os
from coin_class import ApiTradingClient
from helpers import get_open_orders_count, place_order, cancel_all_orders, get_open_orders, place_limit_bracket_orders, volume_generated, write_to_csv
import time
from state import StateManager
from datetime import datetime

load_dotenv()

state = StateManager()
api_key_1 = os.getenv('API_KEY_1')
secret_key_1 = os.getenv('API_SECRET_1')

api_key_2 = os.getenv('API_KEY_2')
secret_key_2 = os.getenv('API_SECRET_2')

symbol = os.getenv('SYMBOL')
qty = float(os.getenv('QTY'))
upper_pct = float(os.getenv('UPPER_PCT'))
lower_pct = float(os.getenv('LOWER_PCT'))

if not api_key_1 or not api_key_2:
    raise ValueError("API key is missing. Check your environment configuration.")


while True:
    time.sleep(3)
    place_limit_bracket_orders(1, symbol, qty, upper_pct, lower_pct, 'NEUTRAL')

    while True:
        if get_open_orders_count(1, symbol) == 1 or not get_open_orders_count(1, symbol) == 2:
            
            if get_open_orders_count(account_number=1, symbol=symbol) > 0:
                side = get_open_orders(account_number=1, symbol=symbol)['data']['orders'][0]['side']
                print(side)
            else:       
                break

            cancel_all_orders(account_number = 1)

            if side == 'BUY':
                time.sleep(2)
                place_order(1, symbol, 95000, 'MARKET', qty, 'BUY')
                vol = volume_generated(qty)
                write_to_csv(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, qty, vol)
                break
            
            elif side == 'SELL':
                time.sleep(2)
                place_order(1, symbol, 95000, 'MARKET', qty, 'SELL')
                vol = volume_generated(qty)
                write_to_csv(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, qty, vol)
                break

        time.sleep(10)

        
