
import time
import hmac
import hashlib
import json
import requests
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()


class Pi42API:

    def __init__(self, api_secret: str, api_key: str):
        self.api_secret = api_secret
        self.api_key = api_key
        self.base_url = "https://fapi.pi42.com/"
        logging.debug(f"Initialized Pi42API with api_key: {self.api_key}")

    def generate_signature(self, data_to_sign):
        """
        Generate HMAC SHA256 signature.
        """
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            data_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        logging.debug(f"Generated signature: {signature} for data: {data_to_sign}")
        return signature

    def place_order(self, symbol, side, order_type, quantity, limit_price = 95000, reduce_only = False):
        """
        Place a new order.
        """
        logging.info("Placing order...")
        timestamp = str(int(time.time() * 1000))
        params = {
            'timestamp': timestamp,
            'placeType': 'ORDER_FORM',
            'quantity': quantity,
            'side': side,
            'symbol': symbol.upper(),
            'type': order_type,
            'reduceOnly': reduce_only,
            'marginAsset': 'INR',
            'deviceType': 'WEB',
            'userCategory': 'EXTERNAL',
            'price': int(limit_price),
            'stopPrice': int(limit_price),
        }
        data_to_sign = json.dumps(params, separators=(',', ':'))
        signature = self.generate_signature(data_to_sign)

        headers = {
            'api-key': self.api_key,
            'signature': signature,
        }

        logging.debug(f"Order params: {params}")
        logging.debug(f"Order headers: {headers}")
        print(f"{self.base_url}v1/order/place-order")

        try:
            response = requests.post(
                f"{self.base_url}v1/order/place-order",
                json=params,
                headers=headers
            )
            response.raise_for_status()
            response_data = response.json()

            order_type = response_data.get('type')
            order_side = response_data.get('side')
            price = response_data.get('price')

            logging.info(f"Placed {order_side} {order_type} order at: {price}")
            return response_data
            
        except Exception as e:
            logging.error(f"An unexpected error occurred while placing order: {str(e)}")

    def get_open_orders(self):
        """
        Retrieve all open orders.
        """
        logging.info("Fetching open orders...")
        timestamp = str(int(time.time() * 1000))
        params = f"timestamp={timestamp}"
        signature = self.generate_signature(params)

        headers = {
            'api-key': self.api_key,
            'signature': signature,
        }
        try:
            response = requests.get(
                f"{self.base_url}v1/order/open-orders",
                headers=headers,
                params={'timestamp': timestamp}
            )
            response.raise_for_status()
            response_data = response.json()

            logging.info(f"Fetched open orders: {response_data}")
            return response_data
        except requests.exceptions.HTTPError as err:
            logging.error(f"HTTP Error while fetching open orders: {err.response.text if err.response else err}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while fetching open orders: {str(e)}")

    def cancel_all_orders(self):
        """
        Cancel all open orders.
        """
        logging.info("Canceling all orders...")
        endpoint = "v1/order/cancel-all-orders"
        timestamp = str(int(time.time() * 1000))
        params = {'timestamp': timestamp}
        data_to_sign = json.dumps(params, separators=(',', ':'))
        signature = self.generate_signature(data_to_sign)

        headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json',
            'signature': signature
        }

        try:
            response = requests.delete(
                f"{self.base_url}{endpoint}",
                json=params,
                headers=headers
            )
            response.raise_for_status()
            response_data = response.json()

            logging.info(f"All orders canceled successfully: {json.dumps(response_data, indent=4)}")
            
        except requests.exceptions.HTTPError as err:
            logging.error(f"HTTP Error while canceling orders: {err.response.text if err.response else err}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while canceling orders: {str(e)}")

def test():
    api_secret = os.getenv('API_SECRET_PI42')
    api_key = os.getenv('API_KEY_PI42')

    print(api_key)
    print(api_secret)

    client = Pi42API(api_secret, api_key)
    print(client)

    print(len(client.get_open_orders()))