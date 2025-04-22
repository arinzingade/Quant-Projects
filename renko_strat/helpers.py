

import logging
import time
import requests
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def get_kline_data(pair, interval = "1m", limit = 1):
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


def make_init_data(contract_pair, time = "1m"):
    
    try:
        logger.info(f"Fetching kline data for contract pair: {contract_pair}")
        info = get_kline_data(contract_pair, interval=time, limit=2000)
        
        data = []

        for i in info:
            high = float(i['high'])
            low = float(i['low'])
            close = float(i['close'])
            open = float(i['open'])
            
            timestamp = pd.to_datetime(int(i['startTime']), unit='ms')
            
            data.append({'date': timestamp, 'high': high, 'low': low, 'close': close, 'open': open})
        
        # Create the DataFrame
        df = pd.DataFrame(data)
        #df.set_index('Timestamp')
        #df.index = pd.to_datetime(df.index)
        
        logger.info("DataFrame created successfully.")
        return df
    
    except Exception as e:
        logger.error(f"Error while making initial data: {e}")
        raise


def calculate_transition_probs(states):
    transitions = {
        (True, True): 0,
        (True, False): 0,
        (False, True): 0,
        (False, False): 0
    }
    total = {
        True: 0,
        False: 0
    }

    for i in range(1, len(states)):
        prev = states[i - 1]
        curr = states[i]
        transitions[(prev, curr)] += 1
        total[prev] += 1

    probs = {k: transitions[k] / total[k[0]] if total[k[0]] > 0 else 0 for k in transitions}
    return probs



if __name__ == "__main__":
    print(get_kline_data("BTCUSDT"))