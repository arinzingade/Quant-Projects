
import time
import hmac
import hashlib
import json
import requests
import redis

from helpers import place_order, get_current_price, get_open_orders, cancel_all_orders

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def place_bracket_limit_orders(upper_pct, lower_pct):

    current_price = get_current_price('BTCUSDT')
    upper_limit_price = int(current_price * (1 + upper_pct))
    lower_limit_price = int(current_price * (1 - lower_pct))

    order_1_info = place_order(1, 'BTCUSDT', upper_limit_price, 'LIMIT', 0.002, 'SELL')
    order_2_info = place_order(1, 'BTCUSDT', lower_limit_price, 'LIMIT', 0.002, 'BUY')

    client_order_id_1 = order_1_info['clientOrderId']
    client_order_id_2 = order_2_info['clientOrderId']

    redis_client.set(client_order_id_1, client_order_id_2)
    redis_client.set(client_order_id_2, client_order_id_1)


if __name__ == "__main__":
    #place_bracket_limit_orders(0.002, 0.002)
    get_open_orders(1)
    #cancel_all_orders(1)