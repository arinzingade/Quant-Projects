

from helpers import place_limit_bracket_orders, get_open_orders_count, cancel_all_orders, get_open_orders
from dotenv import load_dotenv
import os
import time
from state import StateManager

load_dotenv()

symbol = os.getenv('SYMBOL')
symbol = os.getenv('SYMBOL')
qty = float(os.getenv('QTY'))
upper_pct = float(os.getenv('UPPER_PCT'))
lower_pct = float(os.getenv('LOWER_PCT'))

if __name__ == "__main__":
    status = StateManager()
    place_limit_bracket_orders(1, symbol, qty, upper_pct, lower_pct, 'NEUTRAL')