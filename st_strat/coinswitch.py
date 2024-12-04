
from cryptography.hazmat.primitives.asymmetric import ed25519
from urllib.parse import urlencode
import json
import requests
import json
import os
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

def place_order(symbol, side, order_type, qty, price):

    url = "https://coinswitch.co/trade/api/v2/futures/order"

    payload = {
        "symbol": symbol,          
        "exchange": "EXCHANGE_2",     
        "price": price,                
        "side": side,                
        "order_type": order_type,        
        "quantity": qty,               
        "trigger_price": price,        
        "reduce_only": False         
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
        print(json.dumps(response.json(), indent=4))  
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        if response is not None:
            print(f"Response Content: {response.text}")



