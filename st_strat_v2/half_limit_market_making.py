
from pi42 import Pi42API
import os
from helpers import get_current_price
from dotenv import load_dotenv
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

load_dotenv()

secret_key = os.getenv('API_SECRET_PI42')
api_key = os.getenv('API_KEY_PI42')
symbol = os.getenv('SYMBOL')
pct = float(os.getenv('PCT'))
qty = float(os.getenv('QTY'))

api_trading_client = Pi42API(secret_key, api_key)

status = 0


if __name__ == "__main__":

    while True:

        time.sleep(2)

        open_orders = api_trading_client.get_open_orders()
        current_price = get_current_price(symbol)
        thresh_points = current_price * pct

        logger.info(f"Thresh points for {symbol} is {thresh_points}")
        
        if status == 0 and len(open_orders) == 1:
            api_trading_client.cancel_all_orders()

            api_trading_client.place_order(symbol, 'SELL', 'LIMIT', qty, current_price + thresh_points)
            time.sleep(1)
            api_trading_client.place_order(symbol, 'BUY', 'LIMIT', qty, current_price - thresh_points)

            status = 1
        
        if status == 1 and len(open_orders) == 1:
            api_trading_client.cancel_all_orders()
            side = open_orders[0]['side']

            if side == 'BUY':
                api_trading_client.place_order(symbol, 'BUY', 'LIMIT', qty, current_price - thresh_points)
                time.sleep(1)
                api_trading_client.place_order(symbol, 'BUY', 'STOP_MARKET', qty, current_price + thresh_points)

            elif side == 'SELL':
                api_trading_client.place_order(symbol, 'SELL', 'LIMIT', qty, current_price + thresh_points)
                time.sleep(1)
                api_trading_client.place_order(symbol, 'SELL', 'STOP_MARKET', qty, current_price - thresh_points)

            status = 0
        
        if len(open_orders) == 0:
            status = 0


