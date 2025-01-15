
from cryptography.hazmat.primitives.asymmetric import ed25519
import urllib
from urllib.parse import urlencode, urlparse
import json
import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

api_key=os.getenv('API_KEY')
secret_key=os.getenv('SECRET')

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

def place_order(api_key, secret_key, symbol, side, order_type, qty, price = 95000):

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

        print(f"Response Status Code: {response.status_code}")
        print("Response Body:")
        return (json.dumps(response.json(), indent=4))  
    
    except requests.exceptions.RequestException as e:
        return (f"An error occurred: {e}")


def cancel_all_orders():

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

    print(response.text)
    return response