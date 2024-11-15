
import time
from helpers import generate_signature, info_account_1, info_account_2
import requests
import json

listen_key_url = "https://fapi.pi42.com/" + '/v1/retail/listen-key'

def create_or_update_listen_key(account_number):
  
    if account_number == 1:
        api_key, api_secret = info_account_1()

    elif account_number == 2:
        api_key, api_secret = info_account_2()

    else:
        print("Error: Wrong account number, try again")
        return
    
    timestamp = str(int(time.time() * 1000))

    params = {
        'timestamp': timestamp
    }

    # Convert the parameters to a query string (if signing a query string)
    data_to_sign = json.dumps(params, separators=(',', ':'))
    signature = generate_signature(api_secret, data_to_sign)

    # Headers for the request
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json',
        'signature': signature,
    }

    try:
        # Send the POST request to create or update a listen key
        response = requests.post(f'{listen_key_url}', json=params, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        return response_data['listenKey']

    except requests.exceptions.HTTPError as err:
        print(f"Failed {response.status_code}: {response.text}")

