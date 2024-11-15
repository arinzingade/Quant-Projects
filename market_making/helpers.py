
import time
import hmac
import hashlib
import json
import requests

base_url = "https://fapi.pi42.com/"

def info_account_1():
    api_key_account_1 = "539bc7c95f5fb7fd9509d431d22f94f7"
    api_secret_account_1 = "925700449fd74875d6104c8ff1c170f2"

    return api_key_account_1, api_secret_account_1

def info_account_2():
    api_key_account_2 = "ae4f424a012d650177741f79fbadc7d7"
    api_secret_account_2 = "39144059929d190db460d373b4cf7aa9"

    return api_key_account_2, api_secret_account_2

def generate_signature(api_secret, data_to_sign):
    return hmac.new(api_secret.encode('utf-8'), data_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

def place_order(account_number, symbol, limit_price, order_type, quantity, side):

    if account_number == 1:
        api_key, api_secret = info_account_1()
    elif account_number == 2:
        api_key, api_secret = info_account_2()
    else:
        return "Error: Invalid Account Number, please try again!"
    
    timestamp = str(int(time.time() * 1000))

    params = {
        'timestamp': timestamp,       
        'placeType': 'ORDER_FORM',   
        'quantity': quantity,            
        'side': side,                
        'symbol': symbol,          
        'type': order_type,             
        'reduceOnly': False,          
        'marginAsset': 'INR',          
        'deviceType': 'WEB',          
        'userCategory': 'EXTERNAL',    
        'price': limit_price,         
    }

    data_to_sign = json.dumps(params, separators=(',', ':'))
    signature = generate_signature(api_secret, data_to_sign)

    headers = {
        'api-key': api_key,
        'signature': signature,
    }

    try:
        response = requests.post(f'{base_url}/v1/order/place-order', json=params, headers=headers)

        response.raise_for_status()

        response_data = response.json()
        return response_data

    except requests.exceptions.HTTPError as err:
        print(f"Error: {err.response.text if err.response else err}")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def get_24hr_ticker_update(contract_pair):

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

def get_current_price(ticker):
    return float(get_24hr_ticker_update(ticker)['data']["c"])

def get_open_orders(account_number):
# Generate the current timestamp

    if account_number == 1:
        api_key, api_secret = info_account_1()

    elif account_number == 2:
        api_key, api_secret = info_account_2()

    else:
        print("Error: Wrong account number, try again")
        return

    timestamp = str(int(time.time() * 1000))

    # Prepare parameters with the current timestamp
    params = f"timestamp={timestamp}"

    # Generate the signature using the current timestamp
    signature = generate_signature(api_secret, params)

    # Prepare headers
    headers = {
    'api-key': api_key,
    'signature': signature,
    }
    open_orders_url = f"{base_url}/v1/order/open-orders"
    try:
        # Send GET request to fetch open orders with the timestamp parameter
        response = requests.get(open_orders_url, headers=headers, params={'timestamp': timestamp})
        response.raise_for_status() # Raises an error for bad HTTP responses
        response_data = response.json()
        print('Open orders fetched successfully:', json.dumps(response_data, indent=4))
    except requests.exceptions.HTTPError as err:
        print(f"Failed {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def cancel_all_orders(account_number):
    
    if account_number == 1:
        api_key, api_secret = info_account_1()

    elif account_number == 2:
        api_key, api_secret = info_account_2()

    else:
        print("Error: Wrong account number, try again")
        return
    
    endpoint = "/v1/order/cancel-all-orders"

    # Generate the current timestamp
    timestamp = str(int(time.time() * 1000))

    # Prepare the request payload
    params = {
        'timestamp': timestamp
    }

    # Convert the request body to a JSON string for signing
    data_to_sign = json.dumps(params, separators=(',', ':'))

    # Generate the signature (ensure `generate_signature` is properly defined)
    signature = generate_signature(api_secret, data_to_sign)

    # Headers for the DELETE request
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json',
        'signature': signature
    }

    # Construct the full URL
    cancel_orders_url = f"{base_url}{endpoint}"

    try:
        # Send the DELETE request to cancel all orders
        response = requests.delete(cancel_orders_url, json=params, headers=headers)
        response.raise_for_status()  # Raises an error for 4xx/5xx responses
        response_data = response.json()
        print('All orders canceled successfully:', json.dumps(response_data, indent=4))
    except requests.exceptions.HTTPError as err:
        print(f"Failed {response.status_code}: {response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


def delete_order(account_number, client_order_id):
    
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
