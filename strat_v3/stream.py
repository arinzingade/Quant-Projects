
import time
import pandas as pd
import requests
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


def get_kline_data(pair, interval = "5m", limit = 1):
    try:
        # User inputs
        # Prepare the request body (JSON)
        params = {
            'pair': pair,
            'interval': interval,
            'limit': limit
        }

        # Headers for the POST request (no API key or signature required)
        headers = {
            'Content-Type': 'application/json'
        }

        
        kline_url = "https://api.pi42.com/v1/market/klines"

        for attempt in range(3):
            try:
                response = requests.post(kline_url, json=params, headers=headers)
                response.raise_for_status() # Raises an error for 4xx/5xx responses
                response_data = response.json()
                break  

            except requests.exceptions.RequestException:
                print(f"Retrying... ({attempt + 1})")
                time.sleep(10)  
        
        return response_data

    except ValueError:
        print("Please enter valid inputs for pair, interval.")
    except requests.exceptions.HTTPError as err:
        print(f"Error: {err.response.text if err.response else err}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def make_init_data(contract_pair, time = "1m", limit = 100):
    
    try:
        logger.info(f"Fetching kline data for contract pair: {contract_pair}")
        info = get_kline_data(contract_pair, interval=time, limit=limit)
        
        data = []

        for i in info:
            high = float(i['high'])
            low = float(i['low'])
            close = float(i['close'])
            volume = float(i['volume'])
            
            timestamp = pd.to_datetime(int(i['startTime']), unit='ms')
            
            data.append({'Timestamp': timestamp, 'High': high, 'Low': low, 'Close': close, 'Volume': volume})
        
        # Create the DataFrame
        df = pd.DataFrame(data)
        df.set_index('Timestamp')
        df.index = pd.to_datetime(df.index)
        
        logger.info("DataFrame created successfully.")
        return df
    
    except Exception as e:
        logger.error(f"Error while making initial data: {e}")
        raise


def append_to_dataframe(df, contract_pair, interval="1h"):
    """
    Appends the latest kline data to the existing DataFrame.
    
    Args:
        df (pd.DataFrame): Existing DataFrame.
        contract_pair (str): Trading pair symbol (e.g., BTCUSDT).
        interval (str): Time interval for kline data (e.g., "1h").
    
    Returns:
        pd.DataFrame: Updated DataFrame with the latest data.
    """
    try:
        logger.info("Fetching the latest kline data to append.")
        new_data = get_kline_data(contract_pair, interval=interval, limit=1)
        
        if not new_data:
            logger.warning("No new data received to append.")
            return df
        
        entry = new_data[0]
        timestamp = pd.to_datetime(int(entry['startTime']), unit='ms')
        open_price = float(entry['open'])
        high = float(entry['high'])
        low = float(entry['low'])
        close = float(entry['close'])
        volume = float(entry['volume'])
        
        new_row = pd.DataFrame([{
            'Timestamp': timestamp,
            'Open': open_price,
            'High': high,
            'Low': low,
            'Close': close,
            'Volume': volume
        }])
        
        df = pd.concat([df, new_row], ignore_index=True)
        df.set_index('Timestamp', inplace=True)
        
        logger.info(f"Appended new data. DataFrame size: {len(df)} rows.")
        
        return df
    
    except Exception as e:
        logger.error(f"Error appending data: {e}")
        raise


def interval_to_seconds(interval):
    """
    Converts the interval string (e.g., '1m', '1h') to seconds.

    Args:
        interval (str): Time interval (e.g., "1m", "1h").

    Returns:
        int: Time interval in seconds.
    """
    time_units = {'m': 60, 'h': 3600, 'd': 86400}

    unit = interval[-1]  # Get last character which indicates the unit (m, h, d)
    value = int(interval[:-1])  # Get the numeric value part

    if unit not in time_units:
        raise ValueError(f"Invalid interval unit: {unit}")

    return value * time_units[unit]


def stream_data(contract_pair, interval):
    contract_pair = contract_pair
    interval = interval
    
    # Step 1: Create initial DataFrame
    df = make_init_data(contract_pair, interval, limit=1000)
    
    if df is None:
        logger.error("Failed to create initial DataFrame. Exiting.")
        return
    
    logger.info("Starting the data appending loop...")
    
    while True:

        df = append_to_dataframe(df, contract_pair, interval)
        sleep_time = interval_to_seconds(interval)
        logger.info(f"Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)  

        print(df)