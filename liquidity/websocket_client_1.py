import socketio
from dotenv import load_dotenv
import os
from coin_class import ApiTradingClient
from helpers import get_open_orders_count, place_order, cancel_all_orders, get_open_orders, place_limit_bracket_orders
import time

load_dotenv()

api_key_1 = os.getenv('API_KEY_1')
secret_key_1 = os.getenv('API_SECRET_1')
api_key_2 = os.getenv('API_KEY_2')
secret_key_2 = os.getenv('API_SECRET_2')
symbol = os.getenv('SYMBOL')
qty = float(os.getenv('QTY'))
upper_pct = float(os.getenv('UPPER_PCT'))
lower_pct = float(os.getenv('LOWER_PCT'))

if not api_key_1 or api_key_2:
    raise ValueError("API key is missing. Check your environment configuration.")

while True:

    if get_open_orders_count(1, symbol) == 1:
        
        side = get_open_orders(account_number=1, symbol=symbol)['data']['orders']['side']

        cancel_all_orders(account_number = 1)
        cancel_all_orders(account_number = 2)

        if side == 'BUY':
            place_order(2, symbol, 95000, 'MARKET', qty, 'SELL')
            place_limit_bracket_orders(2, symbol, qty, upper_pct, lower_pct, 'SELL')
            place_limit_bracket_orders(1, symbol, qty, upper_pct, lower_pct, 'BUY')
        
        elif side == 'SELL':
            place_order(2, symbol, 95000, 'MARKET', qty, 'BUY')
            place_limit_bracket_orders(2, symbol, qty, upper_pct, lower_pct, 'BUY')
            place_limit_bracket_orders(1, symbol, qty, upper_pct, lower_pct, 'SELL')

    time.sleep(1)

        
