
import datetime
import time
import concurrent.futures
from cryptography.hazmat.primitives.asymmetric import ed25519
import json
import requests
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv('API_KEY')


class ApiTradingClient:
    secret_key = None,
    api_key = None

    def __init__(self, secret_key: str, api_key: str):
        self.secret_key = secret_key
        self.api_key = api_key
        self.base_url = "https://coinswitch.co"
        self.headers = {
            "Content-Type": "application/json"
        }

    def call_api(self, url: str, method: str, headers: dict = None, payload: dict = {}):
        '''
        make an API call on webserver and return response

        Args:
          url (str): The API url to be called
          method (str): The API method
          headers (dict): required headers for API call
          payload (dict): payload for API call

        Returns:
          json: The response of the request
        '''
        final_headers = self.headers.copy()
        if headers is not None:
            final_headers.update(headers)

        response = requests.request(method, url, headers=headers, json=payload)
        print("STATUS CODE", response.status_code)
        if response.status_code == 429:
            print("rate limiting")
        # print(response.text)
        return response.json()

    def signatureMessage(self, method: str, url: str, payload: dict, epoch_time=""):
        '''
          Generate signature message to be signed for given request

          Args:
            url (str): The API url to be called
            method (str): The API method
            epoch_time (str): epochTime for the API call

          Returns:
            json: The signature message for corresponding API call
        '''
        message = method + url + epoch_time
        return message

    def get_signature_of_request(self, secret_key: str, request_string: str) -> str:
        '''
          Returns the signature of the request

          Args:
            secret_key (str): The secret key used to sign the request.
            request_string (str): The string representation of the request.

          Returns:
            str: The signature of the request.
        '''
        try:
            request_string = bytes(request_string, 'utf-8')
            secret_key_bytes = bytes.fromhex(secret_key)
            secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
            signature_bytes = secret_key.sign(request_string)
            signature = signature_bytes.hex()
        except ValueError:
            return False
        return signature

    def make_request(self, method: str, endpoint: str, payload: dict = {}, params: dict = {}):
        '''
        Make the request to :
          a. generate signature message
          b. generate signature signed by secret key
          c. send an API call with the encoded URL

        Args:
            method (str): The method to call API
            endpoint (str): The request endpoint to make API call
            payload (dict): The payload to make API call for POST request
            params (dict): The params to make GET request

          Returns:
            dict: The response of the request.

        '''
        decoded_endpoint = endpoint
        if method == "GET" and len(params) != 0:
            endpoint += '?' + '&'.join([f"{key}={value}" for key, value in params.items()])

            decoded_string = endpoint.replace('+', ' ')
            decoded_endpoint = requests.utils.unquote(decoded_string)


        epoch_time = str(int(datetime.datetime.now().timestamp() * 1000))

        signature_msg = self.signatureMessage(method, decoded_endpoint, payload, epoch_time)
        signature = self.get_signature_of_request(self.secret_key, signature_msg)
        if not signature:
            return {"message": "Please Enter Valid Keys"}
        headers = {
            "X-AUTH-SIGNATURE": signature,
            "X-AUTH-APIKEY": api_key,
            "X-AUTH-EPOCH": epoch_time,
        }

        url = f"{self.base_url}{endpoint}"
        # print(payload)
        response = self.call_api(url, method, headers=headers, payload=payload)
        # print(response)
        return response
    
    def remove_trailing_zeros(self, dictionary):
        for key, value in dictionary.items():
            print(key, type(value))
            print(key, isinstance(value, (int, float)))
            if isinstance(value, (int, float)) and dictionary[key] == int(dictionary[key]):
                dictionary[key] = int(dictionary[key])
                # print(int(dictionary[key]), key)
        return dictionary

    def ping(self):
        return self.make_request("GET", "/trade/api/v2/ping")

    def validate_keys(self):
        return self.make_request("GET", "/trade/api/v2/validate/keys")

    # Rates
    def get_24h_all_pairs_data(self, params: dict = {}):
        return self.make_request("GET", "/trade/api/v2/futures/all-pairs/ticker", params=params)

    def get_24h_coin_pair_data(self, params: dict = {}):
        return self.make_request("GET", "/trade/api/v2/futures/ticker", params=params)

    def get_depth(self, params: dict = {}):
        return self.make_request("GET", "/trade/api/v2/futures/order_book", params=params)

    def get_trades(self, params: dict = {}):
        return self.make_request("GET", "/trade/api/v2/futures/trades", params=params)

    # Candles
    def futures_get_candlestick_data(self, params: dict = {}):
        return self.make_request("GET", "/trade/api/v2/futures/klines", params=params)

    def futures_get_assets(self, params: dict = {}):
        return self.make_request("GET", "/trade/api/v2/futures/instrument_info", params=params)

    # Orders
    def futures_create_order(self, payload: dict = {}):
        # payload = self.remove_trailing_zeros(payload)
        print(payload)
        return self.make_request("POST", "/trade/api/v2/futures/order", payload=payload)

    def futures_cancel_order(self, payload: dict = {}):
        return self.make_request("DELETE", "/trade/api/v2/futures/order", payload=payload)

    def futures_get_leverage(self, params: dict = {}):
        return self.make_request("GET", "/trade/api/v2/futures/leverage", params=params)

    def futures_update_leverage(self, payload: dict = {}):
        return self.make_request("POST", "/trade/api/v2/futures/leverage", payload=payload)

    def futures_get_order_by_id(self, params: dict = {}):
        return self.make_request("GET", "/trade/api/v2/futures/order", params=params)

    def futures_open_orders(self, payload: dict = {}):
        return self.make_request("POST", "/trade/api/v2/futures/orders/open", payload=payload)

    def futures_closed_orders(self, payload: dict = {}):
        return self.make_request("POST", "/trade/api/v2/futures/orders/closed", payload=payload)

    def futures_get_position(self, params: dict = {}):
        return self.make_request("GET", "/trade/api/v2/futures/positions", params=params)

    def futures_get_transactions(self, params: dict = {}):
        return self.make_request("GET", "/trade/api/v2/futures/transactions", params=params)

    def futures_add_margin(self, payload: dict = {}):
        return self.make_request("POST", "/trade/api/v2/futures/add_margin", payload=payload)

    def futures_cancel_all(self, payload: dict = {}):
        return self.make_request("POST", "/trade/api/v2/futures/cancel_all", payload=payload)

    def futures_wallet_balance(self, params: dict = {}):
        return self.make_request("GET", "/trade/api/v2/futures/wallet_balance", params=params)