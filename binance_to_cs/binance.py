import asyncio
import json
import websockets
import logging
from dotenv import load_dotenv
import os

from coinswitch import place_order

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

api_key = os.getenv('API_KEY')
secret_key = os.getenv('SECRET_KEY')
symbol = os.getenv('SYMBOL')
qty = os.getenv('QTY')

class BinanceOrderBook:
    def __init__(self):
        self.best_bid_price = 0
        self.best_bid_qty = 0
        self.best_ask_price = 0
        self.best_ask_qty = 0
        self.state = "NEUTRAL"
        self.vol = 0

    async def listen_order_book(self):
        uri = "wss://stream.binance.com:9443/ws/btcusdt@depth5@100ms"
        async with websockets.connect(uri) as websocket:
            print("Connected to Binance WebSocket")
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    self.process_order_book(data)

                except Exception as e:
                    logger.error(f"Error in Binance WebSocket: {e}")
                    break

    def process_order_book(self, data):
        bids = data.get("bids", [])
        asks = data.get("asks", [])
        if not bids or not asks:
            return
        
        self.best_bid_price, self.best_bid_qty = map(float, bids[0])
        self.best_ask_price, self.best_ask_qty = map(float, asks[0])

        self.bid_ask_ratio = self.best_bid_qty / self.best_ask_qty
        self.ask_bid_ratio = self.best_ask_qty / self.best_bid_qty

        if self.bid_ask_ratio >= int(os.getenv('BUY_THRESH')) and self.state == "NEUTRAL":
            self.state = "BUY"
            logger.info(f"Best Bid: {self.best_bid_qty}")
            logger.info(f"Best Ask: {self.best_ask_qty}")
            logger.info(f"Ratio: {self.bid_ask_ratio}") 
            logger.info("BUY")
            logger.info(f"Buy Price: {self.best_ask_price}")

            place_order(api_key, secret_key, symbol, 'BUY', 'MARKET', qty)
        
        if (self.bid_ask_ratio <= int(os.getenv('BUY_SQUARE_OFF_THRESH')) and self.state == "BUY"):
            self.state = "NEUTRAL"
            logger.info(f"Best Bid: {self.best_bid_qty}")
            logger.info(f"Best Ask: {self.best_ask_qty}")
            logger.info(f"Ratio: {self.bid_ask_ratio}")  
            logger.info("SQUARE OFF")
            logger.info(f"Sell Price: {self.best_bid_price}")

            self.vol += float(qty) * 95000 * 2

            logger.info(f"Volume Generated: {self.vol}")

            place_order(api_key, secret_key, symbol, 'SELL', 'MARKET', qty)

        return self.bid_ask_ratio, self.ask_bid_ratio
