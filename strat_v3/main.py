
import numpy as np
import pandas as pd
import warnings
from tqdm import tqdm
from untrade.client import Client
import ta
from ta.trend import ADXIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.trend import EMAIndicator
from ta.volatility import BollingerBands
import uuid
import os
warnings.filterwarnings("ignore")
from helper import *

from urllib.parse import quote

from coinswitch import place_order

# ## Untrade backtesting script
from untrade.client import Client
from pprint import pprint
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def perform_backtest_large_csv(csv_file_path):
     client = Client()
     file_id = str(uuid.uuid4())
     chunk_size = 90 * 1024 * 1024
     total_size = os.path.getsize(csv_file_path)
     total_chunks = (total_size + chunk_size - 1) // chunk_size
     chunk_number = 0
     if total_size <= chunk_size:
         total_chunks = 1
         # Normal Backtest
         result = client.backtest(
             file_path=csv_file_path,
             leverage=1,
             jupyter_id="team22_zelta_hpps",
             # result_type="Q",
         )
         for value in result:
             print(value)

         return result

     with open(csv_file_path, "rb") as f:
         while True:
             chunk_data = f.read(chunk_size)
             if not chunk_data:
                 break
             chunk_file_path = f"/tmp/{file_id}_chunk_{chunk_number}.csv"
             with open(chunk_file_path, "wb") as chunk_file:
                 chunk_file.write(chunk_data)

             # Large CSV Backtest
             result = client.backtest(
                 file_path=chunk_file_path,
                 leverage=1,
                 jupyter_id="team22_zelta_hpps",
                 file_id=file_id,
                 chunk_number=chunk_number,
                 total_chunks=total_chunks,
                 # result_type="Q",
             )

             for value in result:
                 print(value)

             os.remove(chunk_file_path)

             chunk_number += 1

     return result

def perform_backtest(csv_file_path, type=None):
    """
    Perform backtesting using the untrade SDK.

    Parameters:
    - csv_file_path (str): Path to the CSV file containing historical price data and signals.
    - type: type of result

    Returns:
    - result (generator): Result is a generator object that can be iterated over to get the backtest results.
    """
    # Create an instance of the untrade client
    client = Client()

    if type is not None:
    # Perform backtest using the provided CSV file path
        result = client.backtest(
            file_path=csv_file_path,
            leverage=1,  # Adjust leverage as needed
            jupyter_id="team22_zelta_hpps",  # the one you use to login to jupyter.untrade.io
            result_type=type
        )

    else:
        result = client.backtest(
            file_path=csv_file_path,
            leverage=1,  # Adjust leverage as needed
            jupyter_id="team22_zelta_hpps",  # the one you use to login to jupyter.untrade.io
        )

    for i in result:
        print(i)
    return result


def process_data(data):
     """
     Process the input data and return a dataframe with all the necessary indicators and data for making signals.

     Parameters:
     data (pandas.DataFrame): The input data to be processed.

     Returns:
     pandas.DataFrame: The processed dataframe with all the necessary indicators and data.
     """
     stoch = ta.momentum.StochasticOscillator(
     high=data['High'],
     low=data['Low'],
     close=data['Close'],
     window=14,         # Window for %K (typically 14)
     smooth_window=3    # Window for %D (typically 3)
     )
     data['ema_12'] = data['Close'].ewm(span=12, adjust=False).mean()  # 12-period EMA
     data['ema_26'] = data['Close'].ewm(span=26, adjust=False).mean()  # 26-period EMA
     obv_indicator = OnBalanceVolumeIndicator(close=data['Close'], volume=data['Volume'])
     data['obv'] = obv_indicator.on_balance_volume()
     short_ema_length = 20
     ema_obv = EMAIndicator(close=data['obv'], window=short_ema_length)
     data['obv_ema'] = ema_obv.ema_indicator()
     data['obv_osc'] = data['obv'] - data['obv_ema']
     bb = BollingerBands(close=data['Close'], window=20, window_dev=2)
     data['bb_lower'] = bb.bollinger_lband()
     data['bb_upper'] = bb.bollinger_hband()
     data['bbw'] = (bb.bollinger_hband() - bb.bollinger_lband()) / bb.bollinger_mavg()
     bbw_sma_fast = data['bbw'].rolling(window=20).mean()
     bbw_sma_slow = data['bbw'].rolling(window=100).mean()
     bbw_std = data['bbw'].rolling(window=20).std()
     data['vli_fast'] = bbw_sma_fast
     data['vli_slow'] = bbw_sma_slow
     data['log_returns'] = np.log(data['Close'] / data['Close'].shift(1))
     data = add_entropy_to_csv(data, window=14)
     data['entropy_threshold'] = data['log_returns_entropy'].rolling(window=14).mean()
     # Calculate EMAs for trend confirmation
     ema_20 = EMAIndicator(close=data['Close'], window=20)
     ema_50 = EMAIndicator(close=data['Close'], window=50)
     ema_65 = EMAIndicator(close=data['Close'], window=65)
     ema_400 = EMAIndicator(close=data['Close'], window=400)
     data['ema_20'] = ema_20.ema_indicator()
     data['ema_50'] = ema_50.ema_indicator()
     data['ema_65'] = ema_65.ema_indicator()
     data['ema_400'] = ema_400.ema_indicator()
     # Calculate %K and %D
     data['%K'] = stoch.stoch()
     data['%D'] = stoch.stoch_signal()
     data['%D_DEV'] = data['%D'].rolling(window=20).std()
     data['stddev_20'] = data['Close'].rolling(window=20).std()
     # Calculate Supertrend
     data = calculate_supertrend(data)
     data = calculate_dema(data)
     data['std_dema'] = data['DEMA'].rolling(window=20).std()
     data['macd'] = data['ema_12'] - data['ema_26']
     data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
     adx = ADXIndicator(high=data['High'], low=data['Low'], close=data['Close'], window=14)
     data['adx'] = adx.adx()
     return data

def strat(data):
    d = data.copy()
    # Calculate OBV and OBV Oscillator
    data['trade_type'] = 'NONE'
    data['signals'] = 0  # 1 for buy, -1 for sell, 0 for hold
    position_opened = None
    entry_price = None
    tp=None
    sl=None
    bb_count = 0
    bb_count_short = 0
    print("Running signal generation logic")
    for i in tqdm(range(65, len(data))):  # Start after sufficient data for indicators
        # Long Entry Conditions
        if position_opened is None:
            if (
                data['Close'].iloc[i] > data['ema_65'].iloc[i] > data['ema_400'].iloc[i]  # EMA confirmation
                and (
                    data['obv_osc'].iloc[i] > 0 
                    or data['supertrend_signal'].iloc[i]
                )
                and data['adx'].iloc[i] > 20
                and data['vli_fast'].iloc[i]<= data['vli_slow'].iloc[i]# Strong trend confirmation
            ):
                data['signals'].iloc[i] = 1
                data['trade_type'].iloc[i] = 'ENTRY LONG'
                position_opened = 1
                entry_price = data['Close'].iloc[i]
                tp=1.2*entry_price
                sl=0.9*entry_price
                bb_count = 0  
                
            elif(data['Close'][i] < (data['DEMA'][i] - 1.5*data['std_dema'][i]) ) and data['adx'].iloc[i] > 20 and data['macd'][i] < data['macd_signal'][i] and (data['%K'][i]<data['%D'][i]-2*data['%D_DEV'][i]) :
                data['signals'].iloc[i] = -1
                data['trade_type'].iloc[i] = 'ENTRY SHORT'
                position_opened = -1
                entry_price = data['Close'].iloc[i]
                tp=0.8*entry_price
                sl=1.1*entry_price

        elif position_opened == -1:
            data['trade_type'].iloc[i] = 'HOLD SHORT'
            if data['Close'].iloc[i] < data['bb_upper'].iloc[i]:
                bb_count_short = 0
            else:
                bb_count_short += 1
                
            if (
                data['Close'].iloc[i] > data['ema_65'].iloc[i] > data['ema_400'].iloc[i]  # EMA confirmation
                and (
                    data['obv_osc'].iloc[i] > 0 
                    or data['supertrend_signal'].iloc[i]
                )
                and data['adx'].iloc[i] > 20# Strong trend confirmation
            ):
                data['signals'].iloc[i] = 2
                data['trade_type'].iloc[i] = 'EXIT SHORT and ENTRY LONG'
                position_opened = 1
                entry_price = data['Close'].iloc[i]
                tp=1.2*entry_price
                sl=0.9*entry_price
                bb_count = 0
                
            elif (
               data['Close'][i] > data['DEMA'][i]+ 1.5*data['std_dema'][i] or bb_count_short>=5 or abs(data['log_returns_entropy'][i]) > 5*abs(data['entropy_threshold'][i])
            ):
                data['signals'].iloc[i] = 1
                data['trade_type'].iloc[i] = 'EXIT SHORT'
                position_opened = None
                entry_price = None
                tp=None
                sl=None
         
            elif data['Close'].iloc[i]>=sl:
                data['signals'].iloc[i]=1
                data['trade_type'].iloc[i] = 'EXIT SHORT'
                position_opened = None
                entry_price = None
                sl = None
                tp = None
               
            elif data['Close'].iloc[i]<=tp:
                tp=0.9*data['Close'].iloc[i]
                sl=1.05*data['Close'].iloc[i]
                
            
        # Long Exit Conditions
        elif position_opened == 1:
            data['trade_type'].iloc[i] = 'HOLD LONG'
            if data['Close'].iloc[i] > data['bb_lower'].iloc[i]:
                bb_count = 0
            else:
                bb_count += 1
            if ((data['ema_20'].iloc[i]<data['ema_50'].iloc[i] and data['ema_20'].iloc[i-1] > data['ema_50'].iloc[i-1]) or bb_count >= 5 or abs(data['log_returns_entropy'][i]) > 5*abs(data['entropy_threshold'][i])):
                data['signals'].iloc[i] = -1
                data['trade_type'].iloc[i] = 'EXIT LONG'
                position_opened = None
                entry_price = None
                tp=None
                bb_count = 0
               
            elif data['Close'].iloc[i]<=sl:
                data['signals'].iloc[i]=-1
                data['trade_type'].iloc[i] = 'EXIT LONG'
                position_opened = None
                entry_price = None
                sl = None
                tp = None
            elif data['Close'].iloc[i]>=tp:
                tp=1.1*data['Close'].iloc[i]
                sl=0.9*data['Close'].iloc[i]
            
    d['signals'] = data['signals']
    d['trade_type'] = data['trade_type']
    data = d
    return data

from stream import make_init_data, append_to_dataframe, interval_to_seconds
import time
from datetime import datetime

def main():
    #data = pd.read_csv("ETHUSDT_1h.csv")
    
    symbol = os.getenv('SYMBOL')
    qty = float(os.getenv('QTY'))
    time_interval = int(os.getenv('TIME_INTERVAL'))
    interval = str(time_interval) + 'm'
    contract_pair = os.getenv('SYMBOL')
    
    data = make_init_data(contract_pair, interval, limit=100)
    processed_data = process_data(data)
    result_data = strat(processed_data)


    while True:
        if datetime.now().second == 5 and datetime.now().minute % time_interval == 0:
            data = append_to_dataframe(data, contract_pair, interval)
            
            processed_data = process_data(data)
            result_data = strat(processed_data)
            
            print(result_data)

            last_row = data.iloc[-1]
            
            trade_type = last_row['trade_type']
            logger.info(f"Trade Type: {trade_type}")

            if trade_type == 'ENTRY SHORT':
                place_order(symbol = symbol, side = 'SELL', order_type='MARKET', qty = qty)

            elif trade_type == 'EXIT SHORT':
                place_order(symbol = symbol, side = 'BUY', order_type='MARKET', qty = qty)

            elif trade_type == 'ENTRY LONG':
                place_order(symbol = symbol, side = 'BUY', order_type='MARKET', qty = qty)

            elif trade_type == 'EXIT LONG':
                place_order(symbol = symbol, side = 'SELL', order_type='MARKET', qty = qty)

            elif trade_type == 'EXIT SHORT and ENTRY LONG':
                place_order(symbol = symbol, side = 'BUY', order_type='MARKET', qty = 2 * qty)

            elif trade_type == 'ENTRY LONG and EXIT SHORT':
                place_order(symbol = symbol, side = 'SELL', order_type='MARKET', qty = 2 * qty)

            time.sleep(interval_to_seconds(interval) - 5)

    #print(result_data)
    
    #csv_file_path = "resultsETH.csv"
    #result_data = result_data[['Timestamp', 'High', 'Low', 'Close', 'trade_type', 'signals']]
    #result_data.to_csv(csv_file_path, index=False)
    #print(result_data['signals'].value_counts())
    #backtest_result = perform_backtest(csv_file_path)
    #print(backtest_result)
    # No need to use following code if you are using perform_backtest_large_csv
    #for value in backtest_result:
     #   print(value)


if __name__ == "__main__":
     main()



