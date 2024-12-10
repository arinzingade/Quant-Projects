
import time
from datetime import datetime
import pandas as pd
from public_endpoints import get_kline_data
import logging
from coin_class import ApiTradingClient
from dotenv import load_dotenv
import os
from state import StateManager

status = StateManager()

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

secret_key = os.getenv('SECRET')
api_key = os.getenv('API_KEY')

api_trading_client = ApiTradingClient(secret_key, api_key)

def append_to_df(df, high, low, close):

    try:
        logger.info(f"Appending new data: High={high}, Low={low}, Close={close}")
        timestamp = pd.to_datetime('now')    
        data = {'Timestamp': timestamp, 'High': float(high), 'Low': float(low), 'Close': float(close)}
        
        new_row = pd.DataFrame([data])
        
        df = pd.concat([df, new_row], ignore_index=True)
        
        df.set_index('Timestamp')
        df.index = pd.to_datetime(df.index)

        logger.info("Data appended successfully")   
        return df

    except Exception as e:
        logger.error(f"Error while appending data: {e}")
        raise


def make_init_data(contract_pair):
    
    try:
        logger.info(f"Fetching kline data for contract pair: {contract_pair}")
        info = get_kline_data(contract_pair, limit=100)
        
        data = []

        for i in info:
            high = float(i['high'])
            low = float(i['low'])
            close = float(i['close'])
            
            timestamp = pd.to_datetime(int(i['startTime']), unit='ms')
            
            data.append({'Timestamp': timestamp, 'High': high, 'Low': low, 'Close': close})
        
        # Create the DataFrame
        df = pd.DataFrame(data)
        df.set_index('Timestamp')
        df.index = pd.to_datetime(df.index)
        
        logger.info("DataFrame created successfully.")
        return df
    
    except Exception as e:
        logger.error(f"Error while making initial data: {e}")
        raise


def call_every_one_minute(contract_pair):
    try:
        logger.info(f"Fetching kline data for contract pair: {contract_pair}")
        info = get_kline_data(contract_pair)
        logger.info(f"Data fetched successfully at: {datetime.now()}")

        list_return = [float(info[0]['high']), float(info[0]['low']), float(info[0]['close'])]
        logger.info(f"Processed data: High={list_return[0]}, Low={list_return[1]}, Close={list_return[2]}")

        return list_return
    except Exception as e:
        logger.error(f"Error in `call_every_one_minute`: {e}")
        raise

def run_scheduled_task(contract_pair):
    try:
        logger.info("Starting scheduled task...")
        while True:
            now = datetime.now()
            if now.second == 5:
                logger.info("Triggering `call_every_one_minute`...")
                return call_every_one_minute(contract_pair)
            while datetime.now().second == 5:
                time.sleep(1)
    except Exception as e:
        logger.error(f"Error in `run_scheduled_task`: {e}")
        raise

def manage_dataframe_size(df, max_size = 30, rows_to_delete = 15):
    try:
        logger.info(f"Managing DataFrame size. Current size: {len(df)}")
        if len(df) > max_size:
            logger.info(f"Trimming DataFrame: Removing {rows_to_delete} rows.")
            df = df.iloc[rows_to_delete:]
        return df
    except Exception as e:
        logger.error(f"Error in `manage_dataframe_size`: {e}")
        raise

def is_buy_signal(df):
    try:
        st_upt = list(df['st_upt'])
        length = len(st_upt)

        curr = st_upt[length - 1]
        prev = st_upt[length - 2]

        if pd.isna(prev) and curr > 0:
            logger.info("BUY SIGNAL detected.")
            status.set_status("long")
            return True
        else:
            logger.info("No BUY SIGNAL detected.")
            return False
    except Exception as e:
        logger.error(f"Error in `is_buy_signal`: {e}")
        raise

def is_sell_signal(df):
    try:
        st_dt = list(df['st_dt'])
        length = len(st_dt)

        curr = st_dt[length - 1]
        prev = st_dt[length - 2]

        if pd.isna(prev) and curr > 0:
            logger.info("SELL SIGNAL detected.")
            status.set_status("short")
            return True
        else:
            logger.info("No SELL SIGNAL detected.")
            return False
    except Exception as e:
        logger.error(f"Error in `is_sell_signal`: {e}")
        raise


def thresh_points(current_price, qty, fees_pct, mult):
    try:
        logger.info(f"Calculating threshold points for: price={current_price}, qty={qty}, fees_pct={fees_pct}, mult={mult}")
        fees_taker = fees_pct * current_price * 2 * qty
        profit_target = fees_taker * mult
        profit_target_pct = profit_target / (current_price * qty)

        points = current_price * profit_target_pct
        logger.info(f"Threshold points calculated: {points}")
        return points
    except Exception as e:
        logger.error(f"Error in `thresh_points`: {e}")
        raise

def get_open_orders_count(symbol):
    try:
        logger.info(f"Fetching open orders count for symbol: {symbol}")
        payload = {
            "symbol": symbol,
            "exchange": "EXCHANGE_2",
        }

        response = api_trading_client.futures_open_orders(payload=payload)
        count = len(response['data']['orders'])
        logger.info(f"Open orders count for {symbol}: {count}")
        return count
    except Exception as e:
        logger.error(f"Error in `get_open_orders_count`: {e}")
        raise