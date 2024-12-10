

from helpers import place_limit_bracket_orders, get_open_orders_count, cancel_all_orders, get_open_orders
from dotenv import load_dotenv
import os
import time

load_dotenv()

symbol = os.getenv('SYMBOL')

if __name__ == "__main__":
    place_limit_bracket_orders(1, 'BTCUSDT', 0.002, 0.005, 0.005, 'NEUTRAL')
    time.sleep(1)
    info = get_open_orders(account_number=1, symbol = symbol)
    time.sleep(1)

    print(get_open_orders(account_number=1, symbol=symbol)['data']['orders']['side'])

    cancel_all_orders(account_number=1)
    time.sleep(1)
    get_open_orders_count(account_number=1, symbol=symbol)