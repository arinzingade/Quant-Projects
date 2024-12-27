
import time
from datetime import datetime
import pandas as pd
from public_endpoints import get_kline_data
import logging
from coin_class import ApiTradingClient
from dotenv import load_dotenv
import os
from state import StateManager
import requests

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


def make_init_data(contract_pair, time = "1m"):
    
    try:
        logger.info(f"Fetching kline data for contract pair: {contract_pair}")
        info = get_kline_data(contract_pair, interval=time, limit=100)
        
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


def call_every_one_minute(contract_pair, time = "1m"):
    try:
        logger.info(f"Fetching kline data for contract pair: {contract_pair}")
        info = get_kline_data(contract_pair, interval=time)
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


def get_closed_orders(symbol):
    try:
        logger.info(f"Fetching closed orders count for symbol: {symbol}")
        payload = {
            'symbol': symbol,
            'exchange': "EXCHANGE_2"
        }

        response = api_trading_client.futures_closed_orders(payload=payload)
        count = len(response['data']['orders'])
        logger.info(f"Closed orders count for {symbol} : {count}")

        return count
    
    except Exception as e:
        logger.info(f"Error in 'get_closed_orders_count' : {e} ")
        
def get_24hr_ticker_update(contract_pair):
    """
    Fetch 24-hour ticker update for the given contract pair.
    
    Parameters:
        contract_pair (str): The contract pair (e.g., 'btc', 'eth').
    
    Returns:
        dict: Parsed JSON response from the API.
    """
    if not contract_pair:
        logging.error("Invalid contract pair. Please enter a valid contract pair (e.g., 'btc', 'eth').")
        return None

    full_url = f"https://api.pi42.com/v1/market/ticker24Hr/{contract_pair}"
    logging.info(f"Constructed URL: {full_url}")

    try:
        response = requests.get(full_url)
        response.raise_for_status()
        logging.info(f"Successfully fetched data for contract pair: {contract_pair}")
        
        response_data = response.json()
        return response_data

    except requests.exceptions.HTTPError as err:
        if err.response:
            logging.error(f"HTTPError for contract pair {contract_pair}: {err.response.text}")
        else:
            logging.error(f"HTTPError: {err}")
    except Exception as e:
        logging.exception(f"An unexpected error occurred for contract pair {contract_pair}: {str(e)}")

    return None

def get_current_price(ticker):
    """
    Fetch the current price for the given ticker.
    
    Parameters:
        ticker (str): The ticker to fetch the price for (e.g., 'btc').
    
    Returns:
        float: The current price.
    """
    try:
        data = get_24hr_ticker_update(ticker)
        if data and "data" in data and "c" in data["data"]:
            current_price = float(data["data"]["c"])
            logging.info(f"Current price for {ticker}: {current_price}")
            return current_price
        else:
            logging.warning(f"Price data not found for ticker: {ticker}")
            return None
    except Exception as e:
        logging.exception(f"An error occurred while fetching the current price for {ticker}: {str(e)}")
        return None

