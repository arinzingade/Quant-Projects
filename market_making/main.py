
import redis
from helpers import (place_order, get_current_price, 
                    get_open_orders, cancel_all_orders, fetch_positions, 
                    close_all_positions, custom_round_to_10_not_5)



redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

upper_pct = 0.001
lower_pct = 0.001
qty = 0.002
symbol = 'BTCUSDT'

def place_bracket_limit_orders(account_number, symbol, qty, upper_pct, lower_pct, side):

    current_price = get_current_price(symbol)
    upper_limit_price = custom_round_to_10_not_5(int(current_price * (1 + upper_pct)))
    lower_limit_price = custom_round_to_10_not_5(int(current_price * (1 - lower_pct)))

    if (upper_limit_price - lower_limit_price < 10):
        return f'Error: Spread has become too narrow {upper_limit_price} and {lower_limit_price} are same'

    print(f'Spread is accepted at the value: {upper_limit_price - lower_limit_price}')

    if side == 'NEUTRAL':
        order_1_info = place_order(account_number, symbol, upper_limit_price, 'LIMIT', qty, 'SELL', False)
        order_2_info = place_order(account_number, symbol, lower_limit_price, 'LIMIT', qty, 'BUY', False)

    elif side == 'BUY':
        order_1_info = place_order(account_number, symbol, upper_limit_price, 'LIMIT', qty, 'SELL', False)
        order_2_info = place_order(account_number, symbol, lower_limit_price, 'STOP_MARKET', qty, 'SELL', False)
    
    elif side == 'SELL':
        order_1_info = place_order(account_number, symbol, upper_limit_price, 'STOP_MARKET', qty, 'BUY', False)
        order_2_info = place_order(account_number, symbol, lower_limit_price, 'LIMIT', qty, 'BUY', False)

    client_order_id_1 = order_1_info['clientOrderId']
    client_order_id_2 = order_2_info['clientOrderId']

    redis_client.set(client_order_id_1, client_order_id_2)
    redis_client.set(client_order_id_2, client_order_id_1)

if __name__ == "__main__":
    #place_bracket_limit_orders(1, symbol, qty, upper_pct, lower_pct, 'NEUTRAL')
    get_open_orders(1)
    get_open_orders(2)
    
    fetch_positions(1, 'BTCUSDT', 'OPEN')
    fetch_positions(2, 'BTCUSDT', 'OPEN')