
import asyncio
from binance import BinanceOrderBook
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

async def trading_strategy():
    order_book = BinanceOrderBook()

    await order_book.listen_order_book()

async def main():
    await trading_strategy()

if __name__ == "__main__":
    asyncio.run(main())
