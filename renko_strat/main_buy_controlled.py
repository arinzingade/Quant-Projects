
from helpers import make_init_data, calculate_transition_probs
from matplotlib import pyplot as plt
import numpy as np    
from dotenv import load_dotenv
from renko import build_renko_with_stocktrends
import os
from supertrend import calculate_supertrend
import pandas as pd
import logging
import time
from datetime import datetime
from coinswitch import get_current_price

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
    with open("buy_controlled.csv", "a") as f:
        f.write(f"{datetime.now()}, {position}, {price}\n")

if __name__ == "__main__":


    while (True):

        if datetime.now().second == 0:
            
            df_init = make_init_data("BTCUSDT", time="1m")
            logger.info(df_init)
        
            renko_df = (build_renko_with_stocktrends(df_init, int(os.getenv("BRICK_SIZE"))))
            logger.info(renko_df)

            third_last = renko_df['uptrend'].iloc[-3]
            second_last = renko_df['uptrend'].iloc[-2]
            last = renko_df['uptrend'].iloc[-1]
            logger.info(f"Second last: {second_last}, Last: {last}")

            if pos == "NEUTRAL":
                if second_last == False and last == True:
                    pos = "LONG"
                    print("BUY")
                    sym_price = get_current_price(os.getenv('SYMBOL'))    

                    save_trade(pos, sym_price)
            
            if pos == "LONG":
                if second_last == True and last == False:
                    pos = "NEUTRAL"
                    logger.info("SELL")
                    #sym_price = get_current_price(os.getenv('SYMBOL')) 
                    #save_trade(pos, sym_price)
            
                if third_last == True and second_last == True and last == True:
                    pos = "NEUTRAL"
                    logger.info("SELL")
                    sym_price = get_current_price(os.getenv('SYMBOL')) 
                    save_trade(pos, sym_price)
            

            time.sleep(time_interval - 10)
