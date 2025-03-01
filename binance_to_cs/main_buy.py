
import asyncio
from binance_buy import BinanceOrderBook
import logging
from dotenv import load_dotenv
from coinswitch import cancel_all_orders_all_symbols, close_all_open_positions_for_symbol
import os
import sys
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

async def trading_strategy():
    order_book = BinanceOrderBook()
    await order_book.listen_order_book()


async def shutdown():
    order_book = BinanceOrderBook()
    await order_book.shutdown()

async def main():

    while True:
        logger.info("Starting trading strategy for 2 minutes...")
        task = asyncio.create_task(trading_strategy())

        await asyncio.sleep(120)

        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            logger.info("Trading strategy stopped.")
        
        await shutdown()

        await asyncio.sleep(10)

        logger.info("Restarting trading strategy...")
        os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    asyncio.run(main())
