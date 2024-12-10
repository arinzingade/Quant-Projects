import socketio
from dotenv import load_dotenv
import os
from coin_class import ApiTradingClient
from helpers import get_open_orders_count

load_dotenv()

api_key = os.getenv('API_KEY_1')
secret_key = os.getenv('API_SECRET_1')

client = ApiTradingClient(api_key=api_key, secret_key=secret_key)


if not api_key:
    raise ValueError("API key is missing. Check your environment configuration.")


while True:

    if get_open_orders_count(1, 'BTCUSDT') == 1:
        client.futures_cancel_all()

        
