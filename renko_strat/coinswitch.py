
from cryptography.hazmat.primitives.asymmetric import ed25519
import urllib
from urllib.parse import urlencode, urlparse
import json
import requests
import json
import os
import time
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


load_dotenv()

def generate_signature(method, endpoint, params, payload, secret_key):
    if method == "GET" and len(params) != 0:
        endpoint_with_params = endpoint + '?' + urlencode(params)
    else:
        endpoint_with_params = endpoint

    signature_msg = method + endpoint_with_params + json.dumps(payload, separators=(',', ':'), sort_keys=True)

    request_string = bytes(signature_msg, 'utf-8')
    secret_key_bytes = bytes.fromhex(secret_key)
    secret_key_obj = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
    
    signature_bytes = secret_key_obj.sign(request_string)
    signature = signature_bytes.hex()

    return signature

def get_signature(method, endpoint, params, epoch_time):
    global secret_key
    unquote_endpoint = endpoint
    if method == "GET" and len(params) != 0:
        endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
        unquote_endpoint = urllib.parse.unquote_plus(endpoint)

    signature_msg = method + unquote_endpoint + epoch_time

    request_string = bytes(signature_msg, 'utf-8')
    secret_key_bytes = bytes.fromhex(secret_key)
    secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
    signature_bytes = secret_key.sign(request_string)
    signature = signature_bytes.hex()
    return signature

def place_order(api_key, secret_key, symbol, side, order_type, qty, price = "95000"):

    logger.info(f"Placing order: Symbol={symbol}, Side={side}, OrderType={order_type}, Qty={qty}, Price={price}")

    if order_type == 'STOP_MARKET':
        reduce_only = True
    else:
        reduce_only = False

    url = "https://coinswitch.co/trade/api/v2/futures/order"

    payload = {
        "symbol": symbol,          
        "exchange": "EXCHANGE_2",     
        "price": price,                
        "side": side,                
        "order_type": order_type,        
        "quantity": qty,               
        "trigger_price": price,        
        "reduce_only": reduce_only         
    }

    #print(payload)

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': generate_signature( 
            "POST", 
            "/trade/api/v2/futures/order", 
            {}, 
            payload, 
            secret_key
        ),
        'X-AUTH-APIKEY': api_key  
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  

        logger.info(f"Order placed successfully")

        return [(json.dumps(response.json(), indent=4)), response.status_code]
    
    except Exception as e:
        logger.debug(f"An error occurred in placing orders: {e}")


def cancel_all_orders_all_symbols(api_key, secret_key):

    try:
        url = "https://coinswitch.co/trade/api/v2/futures/cancel_all"

        payload = {
            "exchange" : "EXCHANGE_2",
        }

        headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE':generate_signature( 
                "POST", 
                "/trade/api/v2/futures/cancel_all", 
                {}, 
                payload, 
                secret_key
            ),
        'X-AUTH-APIKEY': api_key
        }

        response = requests.request("POST", url, headers=headers, json=payload)

        logger.info(f"Cancelled All orders for ALL symbols")

        #print(response.text)
        return response

    except Exception as e:
        logger.error(f"Error in Cancelling All orders: {e}")


def cancel_order_by_id(api_key, secret_key, order_id):
    
    url = "https://coinswitch.co/trade/api/v2/futures/order"

    payload = {
        "exchange": "EXCHANGE_2",
        "order_id": order_id
    }

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': generate_signature( 
            "DELETE", 
            "/trade/api/v2/futures/order", 
            {}, 
            payload, 
            secret_key
        ), 
        'X-AUTH-APIKEY': api_key
        }
    
    try:
        response = requests.request("DELETE", url, headers=headers, json=payload)

        logger.info(f"Cancelled Order of order id: {order_id}")
        #print("Response JSON:", response.json())

    except Exception as e:
        logger.error(f"An error while cancelling order by ID: {e}")

def cancel_orders_for_a_symbol(api_key, secret_key, symbol, order_type):

    payload = {
        "exchange": "EXCHANGE_2",
        "symbol" : symbol
    }

    url = "https://coinswitch.co/trade/api/v2/futures/orders/open"

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': generate_signature( 
            "POST", 
            "/trade/api/v2/futures/orders/open", 
            {}, 
            payload, 
            secret_key
        ),
        'X-AUTH-APIKEY': api_key
    }

    try:
        response = requests.request("POST", url, headers=headers, json=payload)
        response = response.json()
        response = response['data']['orders']

        #print(response)

        response_dict = {}

        for open_orders in response:

            if order_type == open_orders['order_type'] == 'LIMIT':
                cancel_order_by_id(api_key, secret_key, open_orders['order_id'])
                response_dict['LIMIT_QTY'] = open_orders['quantity']
                logger.info(f"Cancelled LIMIT order for {symbol}")
            
            if order_type == open_orders['order_type'] == 'STOP_MARKET':
                cancel_order_by_id(api_key, secret_key, open_orders['order_id'])
                response_dict['STOP_MARKET_QTY'] = open_orders['quantity']
                logger.info(f"Cancelled STOP_MARKET order for {symbol}")

        return response_dict
    
    except Exception as e:
        logger.error(f"An error occurred while Cancelling Orders: {e}")

def update_leverage(api_key, secret_key, symbol, leverage):

    try:

        url = "https://coinswitch.co/trade/api/v2/futures/leverage"

        payload = {
            "symbol": symbol,
            "exchange" : "EXCHANGE_2",
            "leverage": int(leverage)
        }

        headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE':generate_signature( 
                "POST", 
                "/trade/api/v2/futures/leverage", 
                {}, 
                payload, 
                secret_key
            ),
        'X-AUTH-APIKEY': api_key
        }

        response = requests.request("POST", url, headers=headers, json=payload)
        logger.info(f"Updated Leverage for {symbol} to leverage: {leverage}")

        #print(response.text)
        return response

    except Exception as e:
        logger.error(f"Error while updating the leverage: {e}")


def get_instrument_info(api_key, secret_key, symbol):
    params = {"exchange": "EXCHANGE_2"}
    endpoint = "/trade/api/v2/futures/instrument_info"

    query_string = urlencode(params)
    url = f"https://coinswitch.co{endpoint}?{query_string}"

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': generate_signature("GET", endpoint, params, {}, secret_key),
        'X-AUTH-APIKEY': api_key
    }

    try:
        response = requests.get(url, headers=headers)
        response = response.json()
        response = response['data']
        #print(response[symbol])
        min_qty = response[symbol]['min_base_quantity']
        max_leverage = response[symbol]['max_leverage']
        #print(min_qty)

        logger.info(f"Fetched MIN QTY and MAX Leverage")
        return float(min_qty), float(max_leverage)
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error to get instrument info: {e}")


def get_wallet_balance(api_key, secret_key):
    endpoint = "/trade/api/v2/futures/wallet_balance"
    url = f"https://coinswitch.co{endpoint}"

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-SIGNATURE': generate_signature("GET", endpoint, {}, {}, secret_key),
        'X-AUTH-APIKEY': api_key
    }

    try:
        response = requests.get(url, headers=headers)
        response = response.json()

        base_asset_balance = response['data']['base_asset_balances']

        for asset in base_asset_balance:
            if asset['base_asset'] == 'USDT':
                usdt_wallet_balance = asset['balances']['total_balance']
        
        #print(usdt_wallet_balance)
        logger.info("Successfully fetched Wallet Balance")
        return usdt_wallet_balance
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error while fetching Wallet Balance: {e}")

def get_24hr_ticker_update(contract_pair):

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

def position_size_calc(api_key, secret_key, risk_pct, sl_pct, symbol):
    
    try:
        # $1000
        usdt_balance = float(get_wallet_balance(api_key, secret_key))

        # $10
        risk_capital = usdt_balance * risk_pct
        #print("Risk Capital: ", risk_capital)

        # $500
        position_size_usdt = (risk_capital / sl_pct) 
        #print("Position Size USDT: ", position_size_usdt)

        current_market_price_ticker = get_current_price(symbol)

        min_qty_symbol, max_leverage_coinswitch = get_instrument_info(api_key, secret_key, symbol)
        #print("Min Qty Symbol: ", min_qty_symbol)
        #print("Max Leverage from Coinswitch: ", max_leverage_coinswitch)

        qty = max(position_size_usdt / current_market_price_ticker, min_qty_symbol)
        
        max_leverage = min(float(position_size_usdt) / float(risk_capital), float(max_leverage_coinswitch))

        logger.info(f"Calculated position size as: {qty} and Levarage as {max_leverage}")
        return qty, max_leverage

    except Exception as e:
        logger.error(f"Error in fetching position size calculation: {e}")



def get_positions(api_key, secret_key, symbol):
    """Fetches open futures positions from Coinswitch API."""
    
    base_url = "https://coinswitch.co"
    endpoint = "/trade/api/v2/futures/positions"

    params = {
        "exchange": "EXCHANGE_2",
        "symbol": symbol
    }

    # Generate signature correctly
    signature = generate_signature("GET", endpoint, params, {}, secret_key)

    headers = {
        "Content-Type": "application/json",
        "X-AUTH-SIGNATURE": signature,  
        "X-AUTH-APIKEY": api_key
    }

    try:
        # Corrected request: Use `params=params` for GET request
        response = requests.get(base_url + endpoint, headers=headers, params=params)
        response = response.json()
        response = response['data']

        response_json = []

        for pos in response:
            if pos['status'] == 'OPEN':
                pos_symbol = pos['symbol']
                pos_side = pos['position_side']
                pos_size = pos['position_size']

                response_json.append({ 
                    'symbol': pos_symbol,
                    'side': pos_side,
                    'size': pos_size
                })

        return response_json

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


def close_all_open_positions_for_symbol(api_key, secret_key, symbol):

    positions = get_positions(api_key, secret_key, symbol)
    positions = positions.get('data', None)

    if positions:
        for pos in positions:
            position_side = pos['position_side']
            position_size = pos['position_size']

            if position_side == "LONG":
                place_order(api_key, secret_key, symbol, 'SELL', 'MARKET', position_size)
            
            elif position_side == "SHORT":
                place_order(api_key, secret_key, symbol, 'BUY', 'MARKET', position_size)
    
    else:
        logger.info("No positions to close")


def get_ohlc_for_symbol(symbol):

    data = get_24hr_ticker_update(symbol)['data']
    symbol_open = float(data['o'])
    symbol_high = float(data['h'])
    symbol_low = float(data['l'])
    symbol_close = float(data['c'])

    return (symbol_open, symbol_high, symbol_low, symbol_close)
    