
from helpers import get_open_orders, fetch_positions


if __name__ == "__main__":
    get_open_orders(1)
    get_open_orders(2)
    
    fetch_positions(1, 'BTCUSDT', 'OPEN')
    fetch_positions(2, 'BTCUSDT', 'OPEN')