import json
import logging
import re
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_URL = os.getenv('API_URL')
DEFAULT_QTY = "0.002" 

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# Regex pattern to extract trade order details
ORDER_PATTERN = re.compile(
    r"symbol:\s*(\S+)\s*"
    r"side:\s*(\S+)\s*"
    r"order_type:\s*(\S+)\s*"
    r"price:\s*(\d+\.?\d*)"
)

async def send_order(data: dict):
    """Send order data as a POST request."""
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=data) as response:
            return await response.text()

@dp.message()
async def handle_message(message: Message):
    """Parse message and send trade order."""
    match = ORDER_PATTERN.search(message.text)
    if match:
        symbol, side, order_type, price = match.groups()

        with open('env.json', 'r') as file:
            credentials = json.load(file).get("credentials", [])
        
        for creds in credentials:
    
            order_data = {
                "api_key": creds['API_KEY'],
                "api_secret": creds['API_SECRET'],
                "symbol": symbol,
                "side": side.upper(),
                "order_type": order_type.upper(),
                "price": float(price),
                "qty": DEFAULT_QTY,
            }
            
            response = await send_order(order_data)
            response_msg = "Success"

            display_order_data = {
                "symbol": symbol,
                "side": side.upper(),
                "order_type": order_type.upper(),
                "price": float(price),
                "qty": DEFAULT_QTY,
            }

            await message.reply(f"Order Sent:\n{json.dumps(display_order_data, indent=4)}\nResponse: {response_msg}")
    else:
        await message.reply("Invalid order format. Please use the format:\n\n"
                          "symbol: BTCUSDT\nside: BUY\norder_type: MARKET\nprice: 95000")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())