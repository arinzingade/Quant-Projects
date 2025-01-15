import asyncio
import time
import json
import requests
from redis.asyncio import Redis

from helpers import info_account_1, info_account_2, generate_signature

base_url = "https://fapi.pi42.com/"
redis_client = Redis(host='localhost', port=6379, decode_responses=False)

async def place_order(account_number, symbol, limit_price, order_type, quantity, side, reduce_only):
    # Fetch API keys based on account number
    if account_number == 1:
        api_key, api_secret = info_account_1()
    elif account_number == 2:
        api_key, api_secret = info_account_2()
    else:
        return "Error: Invalid Account Number, please try again!"
    
    # Current timestamp for the API request
    timestamp = str(int(time.time() * 1000))

    params = {
        'timestamp': timestamp,
        'placeType': 'ORDER_FORM',
        'quantity': quantity,
        'side': side,
        'symbol': symbol,
        'type': order_type,
        'reduceOnly': reduce_only,
        'marginAsset': 'INR',
        'deviceType': 'WEB',
        'userCategory': 'EXTERNAL',
        'price': limit_price,
        'stopPrice': limit_price, 
    }

    # Prepare the data to sign for authentication
    data_to_sign = json.dumps(params, separators=(',', ':'))
    signature = generate_signature(api_secret, data_to_sign)

    # Set up the headers for authentication
    headers = {
        'api-key': api_key,
        'signature': signature,
    }

    try:
        # Send the POST request to place the order
        response = requests.post(f'{base_url}v1/order/place-order', json=params, headers=headers)
        response.raise_for_status()  # Will raise HTTPError for bad responses (4xx, 5xx)

        # Parse and return the response
        response_data = response.json()
        
        order_type = response_data['type']
        order_side = response_data['side']
        price = response_data['price']

        print(" ", account_number, " | ", "Placed", order_side, order_type, "at: ", price )

        return response_data

    except requests.exceptions.HTTPError as err:
        # Handle HTTP errors
        print(f"Error: {err.response.text if err.response else err}")

    except Exception as e:
        # Handle unexpected errors
        print(f"An unexpected error occurred: {str(e)}")

async def place_bracket_limit_orders(account_number, symbol, qty, upper_pct, lower_pct, side):

    current_price = await get_current_price(symbol)
    upper_limit_price = await custom_round_to_10_not_5(int(current_price * (1 + upper_pct)))
    lower_limit_price = await custom_round_to_10_not_5(int(current_price * (1 - lower_pct)))

    if side == 'NEUTRAL':
        order_1_info = await place_order(account_number, symbol, upper_limit_price, 'LIMIT', qty, 'SELL', False)
        order_2_info = await place_order(account_number, symbol, lower_limit_price, 'LIMIT', qty, 'BUY', False)

    elif side == 'BUY':
        order_1_info = await place_order(account_number, symbol, upper_limit_price, 'LIMIT', qty, 'SELL', False)
        order_2_info = await place_order(account_number, symbol, lower_limit_price, 'STOP_MARKET', qty, 'SELL', False)
    
    elif side == 'SELL':
        order_1_info = await place_order(account_number, symbol, upper_limit_price, 'STOP_MARKET', qty, 'BUY', False)
        order_2_info = await place_order(account_number, symbol, lower_limit_price, 'LIMIT', qty, 'BUY', False)

    client_order_id_1 = order_1_info['clientOrderId']
    client_order_id_2 = order_2_info['clientOrderId']

    await redis_client.set(client_order_id_1, client_order_id_2)
    await redis_client.set(client_order_id_2, client_order_id_1)

async def cancel_counter_order(account_number, client_order_id):
    counter_order_id = await redis_client.get(client_order_id)

    if counter_order_id:
        counter_order_id = counter_order_id.decode('utf-8')
        print(f"Counter order {counter_order_id} found. Cancelling it.")
        await delete_order(account_number, counter_order_id)

        await redis_client.delete(client_order_id)
        await redis_client.delete(counter_order_id)

        print("-------------------------------------------------------------------------------")
    else:
        print("No counter order found.")

async def delete_order(account_number, client_order_id):
    
    if account_number == 1:
        api_key, api_secret = info_account_1()

    elif account_number == 2:
        api_key, api_secret = info_account_2()

    else:
        print("Error: Wrong account number, try again")
        return

    client_order_id = client_order_id
    delete_order_url = "https://fapi.pi42.com/v1/order/delete-order"

    timestamp = str(int(time.time() * 1000))

    params = {
        'clientOrderId': client_order_id,
        'timestamp': timestamp
    }

    data_to_sign = json.dumps(params, separators=(',', ':'))
    signature = generate_signature(api_secret, data_to_sign)

    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json',
        'signature': signature,
    }

    try:
        response = requests.delete(delete_order_url, json=params, headers=headers)
        response.raise_for_status()
        print(f"Order with clientOrderId {client_order_id} deleted successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Failed {response.status_code}: {response.text}")


async def get_24hr_ticker_update(contract_pair):

    # Validate the input
    if not contract_pair:
        print("Invalid contract pair. Please enter a valid contract pair (e.g., btc, eth).")
        return

    # Construct the full URL for the API request using the provided contract pair
    full_url = f"https://api.pi42.com/v1/market/ticker24Hr/{contract_pair}"

    try:
        # Send the GET request to the API
        response = requests.get(full_url)
        response.raise_for_status()  # Raise an error for HTTP 4xx/5xx responses

        # Parse the JSON response data
        response_data = response.json()

        return response_data
    
    except requests.exceptions.HTTPError as err:
        # Handle HTTP errors specifically
        print(f"Error: {err.response.text if err.response else err}")
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {str(e)}")

async def get_current_price(ticker):
    ticker_data = await get_24hr_ticker_update(ticker)
    current_price = float(ticker_data['data']["c"])
    return current_price

async def custom_round_to_10_not_5(number):
    rem = number % 10

    if rem == 5:
        return number
    if rem < 5:
        number -= rem
        return number
    if rem > 5:
        number += (10- rem)
        return number