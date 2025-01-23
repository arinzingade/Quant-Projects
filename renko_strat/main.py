

from renko import Renko
from helpers import make_init_data
from dotenv import load_dotenv
import os
from coinswitch import place_order, cancel_all_orders
from coin_class import ApiTradingClient
from datetime import datetime
import mplfinance as mpf

load_dotenv()

symbol = os.getenv('SYMBOL')
time_interval = int(os.getenv('TIME_INTERVAL'))
qty = float(os.getenv('QTY'))

if __name__ == "__main__":

    df = make_init_data(symbol.upper(), time = str(time_interval) + "m")
    
    renko = Renko(atr_period=14)
    renko.transform(df)
    renko_df = renko.renko_df

    brick_color = (renko_df.iloc[len(renko_df)-1])['Brick_Color']

    if brick_color == 'Green':
        #place_order(symbol, 'BUY', 'MARKET', qty)
        pass
    elif brick_color == 'Red':
        #place_order(symbol, 'SELL', 'MARKET', qty)
        pass

    while True:
        if datetime.now().second == 5 and datetime.now().minute % time_interval == 0:

            df = make_init_data(symbol.upper(), time = str(time_interval) + "m")

            renko = Renko(atr_period=14)
            renko.transform(df)
            renko_df = renko.renko_df

            print(df)
            print(renko_df)

            brick_color_last = brick_color = (renko_df.iloc[len(renko_df)-1])['Brick_Color']
            brick_color_second_last = brick_color = (renko_df.iloc[len(renko_df)-2])['Brick_Color']

            if brick_color_second_last == 'Red' and brick_color_last == 'Green':
                #place_order(symbol, 'BUY', 'MARKET', qty * 2)
                pass

            elif brick_color_second_last == 'Green' and brick_color_last == 'Red':
                #place_order(symbol, 'SELL', 'MARKET', qty * 2)
                pass

            renko_params = {'brick_size': df['ATR'].iloc[len(df)-1]}  # Set the brick size in the renko_params
            mpf.plot(df, type='renko', renko_params=renko_params, style='yahoo', title="Renko Chart", ylabel="Price")
            
    
