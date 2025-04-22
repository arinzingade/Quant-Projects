
from helpers import make_init_data, calculate_transition_probs
from matplotlib import pyplot as plt
import numpy as np    
from dotenv import load_dotenv
from renko import build_renko_with_stocktrends
import os

import pandas as pd
import logging
import time
from datetime import datetime
from coinswitch import get_current_price, place_order, get_ohlc_for_symbol

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

load_dotenv()

time_interval = int(os.getenv("TIME_INTERVAL")) 

pos = "NEUTRAL"

def save_trade(position, price):
    with open("sell.csv", "a") as f:
        f.write(f"{datetime.now()}, {position}, {price}\n")

api_key = os.getenv("API_KEY")
secret_key = os.getenv("API_SECRET")
symbol = os.getenv("SYMBOL")
qty = float(os.getenv("QTY"))
brick_size = int(os.getenv("BRICK_SIZE"))


if __name__ == "__main__":

    df_init = make_init_data("BTCUSDT", time="1m")
    renko_df = (build_renko_with_stocktrends(df_init, int(os.getenv("BRICK_SIZE"))))
    renko_last_close = renko_df['close'].iloc[-1]

    third_last = renko_df['uptrend'].iloc[-3]
    second_last = renko_df['uptrend'].iloc[-2]
    last = renko_df['uptrend'].iloc[-1]

    renko_last_close = renko_df['close'].iloc[-1]

    logger.info(renko_df)


    while (True):

        df_init = df_init.tail(1000000)

        sym_open, sym_high, sym_low, sym_close = get_ohlc_for_symbol("BTCUSDT") 

        new_row = pd.DataFrame([{
            'open': sym_open,
            'high': sym_high,
            'low': sym_low,
            'close': sym_close,
            'date': datetime.now()
        }])

        df_init = pd.concat([df_init, new_row], ignore_index=True)

        logger.info(df_init.tail(5))
        #print(df_init)

        renko_df = (build_renko_with_stocktrends(df_init, int(os.getenv("BRICK_SIZE"))))
        logger.info(renko_df)

        third_last = renko_df['uptrend'].iloc[-3]
        second_last = renko_df['uptrend'].iloc[-2]
        last = renko_df['uptrend'].iloc[-1]

        renko_last_close = renko_df['close'].iloc[-1]

        logger.info(f"Third Last: {third_last}, Second last: {second_last}, Last: {last}")

        if pos == "NEUTRAL":
            if third_last == True and second_last == False and last == False:
                pos = "SHORT"
                logger.info("SELL")
                sym_price = get_current_price(os.getenv('SYMBOL'))    

                #save_trade(pos, sym_price)

                place_order(api_key, secret_key, symbol, "SELL", "MARKET", qty)
                #place_order(api_key, secret_key, symbol, "BUY", "STOP_MARKET", qty, sym_price + brick_size)

        if pos == "SHORT":
            if last == True:
                pos = "NEUTRAL"
                logger.info("BUY")
                sym_price = get_current_price(os.getenv('SYMBOL')) 
                save_trade(pos, sym_price)

                place_order(api_key, secret_key, symbol, "BUY", "MARKET", qty)
                #cancel_all_orders_all_symbols(api_key, secret_key)

        time.sleep(time_interval)
