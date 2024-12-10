

from coin_class import ApiTradingClient
import os
from dotenv import load_dotenv
from redis import Redis

redis_client = Redis(host='localhost', port=6379, decode_responses=False)
load_dotenv()


def get_current_price(symbol):

    api_key_1 = os.getenv('API_KEY_1')
    api_secret_1 = os.getenv('API_SECRET_1')
    client = ApiTradingClient(api_key=api_key_1, secret_key=api_secret_1)
    params = {
        "symbol": symbol,
        "exchange": "EXCHANGE_2"
        }   
    
    last_price = float(client.get_24h_coin_pair_data(params)['data']['EXCHANGE_2']['last_price'])
    return last_price

def custom_round_to_10_not_5(number):
    rem = number % 10

    if rem == 5:
        return number
    if rem < 5:
        number -= rem
        return number
    if rem > 5:
        number += (10- rem)
        return number


def place_order(account_number, symbol, price, order_type, qty, order_side):

    if account_number == 1:
        api_key = os.getenv('API_KEY_1')
        api_secret = os.getenv('API_SECRET_1')

    elif account_number == 2:
        api_key = os.getenv('API_KEY_2')
        api_secret = os.getenv('API_SECRET_2')

    else:
        print("Please input a valid account number.")

    client = ApiTradingClient(api_key=api_key, secret_key=api_secret)

    payload = {
        "symbol" : symbol,
        "exchange" : "EXCHANGE_2",
        "price" : price,
        "side" : order_side,
        "order_type" : order_type,
        "quantity" : qty,
        "trigger_price" : price
    }

    info = client.futures_create_order(payload)

    print(info)
    return info

def get_open_orders_count(account_number, symbol):
    try:
        if account_number == 1:
            api_key = os.getenv('API_KEY_1')
            secret_key = os.getenv('API_SECRET_1')
            api_trading_client = ApiTradingClient(api_key=api_key, secret_key=secret_key)

        payload = {
            "symbol": symbol,
            "exchange": "EXCHANGE_2",
        }

        response = api_trading_client.futures_open_orders(payload=payload)
        count = len(response['data']['orders'])
        print(f"Open orders count for {symbol}: {count}")
        return count
    
    except Exception as e:
        print(f"Error in `get_open_orders_count`: {e}")
        raise

def place_limit_bracket_orders(account_number, symbol, qty, upper_pct, lower_pct, side):
        
        current_price = get_current_price(symbol)
        upper_limit_price = custom_round_to_10_not_5(int(current_price * (1 + upper_pct)))
        lower_limit_price = custom_round_to_10_not_5(int(current_price * (1 - lower_pct)))

        if side == 'NEUTRAL':
            order_1_info = place_order(account_number, symbol, upper_limit_price, 'LIMIT', qty, 'SELL', False)
            order_2_info = place_order(account_number, symbol, lower_limit_price, 'LIMIT', qty, 'BUY', False)

        elif side == 'BUY':
            order_1_info = place_order(account_number, symbol, upper_limit_price, 'LIMIT', qty, 'SELL', False)
            order_2_info = place_order(account_number, symbol, lower_limit_price, 'STOP_MARKET', qty, 'SELL', False)
        
        elif side == 'SELL':
            order_1_info = place_order(account_number, symbol, upper_limit_price, 'STOP_MARKET', qty, 'BUY', False)
            order_2_info = place_order(account_number, symbol, lower_limit_price, 'LIMIT', qty, 'BUY', False)

        client_order_id_1 = order_1_info['clientOrderId']
        client_order_id_2 = order_2_info['clientOrderId']

        redis_client.set(client_order_id_1, client_order_id_2)
        redis_client.set(client_order_id_2, client_order_id_1)


place_order(1, 'BTCUSDT', 97600, 'LIMIT', 0.002, 'BUY')