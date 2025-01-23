import time
from datetime import datetime
from supertrend import get_supertrend
import warnings
import os
from coinswitch import place_order, cancel_all_orders
from coin_class import ApiTradingClient
from helpers import (
    make_init_data,
    call_every_one_minute,
    thresh_points,
    append_to_df,
    get_open_orders_count,
    is_buy_signal,
    is_sell_signal,
    usdt_cs_account_balance
)
from state import StateManager
import logging
from datetime import datetime, time as dt_time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')

status = StateManager()

qty = float(os.getenv('QTY'))
fees_pct = float(os.getenv('FEES_PCT'))
fees_mult = int(os.getenv('FEES_MULT'))
symbol = str(os.getenv('SYMBOL'))
secret_key = os.getenv('SECRET')
api_key = os.getenv('API_KEY')
time_interval = int(os.getenv('TIME_FRAME_MIN'))
thresh_pct = float(os.getenv('THRESH_PCT'))

api_trading_client = ApiTradingClient(secret_key, api_key)

init_price = 0

thresh_value_updated = False

if __name__ == "__main__":

    while True:
        df = make_init_data(symbol.upper(), time = str(time_interval) + "m")
        logger.info("Initial DataFrame:")
        logger.info(df.to_string())
        logger.info(f"Qty: {qty}")

        current_balance = usdt_cs_account_balance()
        logger.info(f"Current Balance: {current_balance}")

        target_profit = thresh_pct * current_balance
        logger.info(f"Target Profit: {target_profit}")

        df['st'], df['st_upt'], df['st_dt'], df['atr'] = get_supertrend(df['High'], df['Low'], df['Close'], 10, 3)

        thresh_value_updated = True

        while True:
            if datetime.now().second == 5 and datetime.now().minute % time_interval == 0:

                current_balance_instance_dff = usdt_cs_account_balance() - current_balance
                logger.info(f"Current Balance Instance Difference: {current_balance_instance_dff}")

                if current_balance_instance_dff >= target_profit:
                    logger.info(f"Total Profit Achieved: {current_balance_instance_dff}")
                    logger.info("Target Profit Achieved. Exiting...")
                    break
                
                for attempt in range(3):
                    try:
                        high, low, close = call_every_one_minute(symbol.upper(), time = str(time_interval) + "m")
                        break
                    except:
                        print(f"Retrying... ({attempt + 1})")
                        time.sleep(10)  
                    
                df = append_to_df(df, high, low, close)
                
                df['st'], df['st_upt'], df['st_dt'], df['atr'] = get_supertrend(df['High'], df['Low'], df['Close'], 10, 3)
                
                current_price = list(df['Close'])[len(df['Close']) - 1]
                thresh = thresh_points(current_price, qty, fees_pct, fees_mult)

                logger.info(df.to_string())
                logger.info(f"Init Price: {init_price}")
                logger.info(f"Current Price is: {current_price}")
                logger.info(f"Thresh Points are: {thresh}")
                logger.info(f"Status: {status}")
                logger.info(f"Current Balance Instance Difference: {current_balance_instance_dff}")

                open_orders_count = get_open_orders_count(symbol)

                if open_orders_count == 0 or open_orders_count == 1:
                    cancel_all_orders()
                    status.set_status("neutral")
                    print("STATUS updated to Neutral")

                if status.get_status() == "neutral":
                    if is_buy_signal(df):
                        cancel_all_orders()
                        time.sleep(1)
                        place_order(symbol, "BUY", "MARKET", qty)
                        time.sleep(1)
                        place_order(symbol, 'SELL', 'LIMIT', qty, current_price + thresh)
                        time.sleep(1)
                        place_order(symbol, 'SELL', 'STOP_MARKET', qty, current_price - 2 * thresh)
                        status.set_status("long")

                    elif is_sell_signal(df):
                        cancel_all_orders()
                        time.sleep(1)
                        place_order(symbol, "SELL", "MARKET", qty)
                        time.sleep(1)
                        place_order(symbol, 'BUY', 'LIMIT', qty, current_price - thresh)
                        time.sleep(1)
                        place_order(symbol, 'BUY', 'STOP_MARKET', qty, current_price + 2 * thresh)
                        status.set_status("short")

                elif status.get_status() == "short":
                    if is_buy_signal(df):
                        place_order(symbol, "BUY", "MARKET", qty)
                        time.sleep(1)
                        place_order(symbol, "BUY", "MARKET", qty)
                        time.sleep(1)
                        cancel_all_orders()
                        time.sleep(1)
                        place_order(symbol, 'SELL', 'LIMIT', qty, current_price + thresh)
                        time.sleep(1)
                        place_order(symbol, 'SELL', 'STOP_MARKET', qty, current_price - 2 * thresh)
                        status.set_status("long")

                elif status.get_status() == "long":
                    if is_sell_signal(df):
                        place_order(symbol, "SELL", "MARKET", qty)
                        time.sleep(1)
                        place_order(symbol, "SELL", "MARKET", qty)
                        time.sleep(1)
                        cancel_all_orders()
                        time.sleep(1)
                        place_order(symbol, 'BUY', 'LIMIT', qty, current_price - thresh)
                        time.sleep(1)
                        place_order(symbol, 'BUY', 'STOP_MARKET', qty, current_price + 2 * thresh)
                        status.set_status("short")
                
                time.sleep(time_interval * 60 - 10)
        
        while datetime.now().time() >= dt_time(18, 30, 0, 0) and datetime.now().time() >= dt_time(18, 31, 0, 0):
            logger.info("Day Closed as THRESH reached. Waiting for the next day to start...")
            time.sleep(1)
            continue
        