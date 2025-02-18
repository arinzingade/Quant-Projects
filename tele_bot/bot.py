import json
import logging
import re
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
import asyncio
from dotenv import load_dotenv
import os
from coinswitch import (place_order, position_size_calc, 
                        update_leverage, get_current_price, 
                        cancel_orders_for_a_symbol)
import logging


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_URL = os.getenv('API_URL')

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Define regex patterns
ORDER_PATTERN = re.compile(
    r"tag:\s*(\w+)\s*"                   # Extract tag type (Required)
    r"symbol:\s*(\S+)\s*"                 # Extract symbol (Required)
    r"(?:side:\s*(\S+))?\s*"              # Extract side (Optional)
    r"(?:order_type:\s*(\S+))?\s*"        # Extract order_type (Optional)
    r"(?:price:\s*(\d+\.?\d*))?\s*"       # Extract price (Optional)
    r"(?:risk_pct:\s*(\d+\.?\d*))?\s*"    # Extract risk_pct (Optional)
    r"(?:sl_pct:\s*(\d+\.?\d*))?\s*"      # Extract sl_pct (Optional)
    r"(?:tp_pct:\s*(\d+\.?\d*))?\s*"      # Extract tp_pct (Optional)
    r"(?:qty:\s*(\d+\.?\d*))?\s*",        # Extract qty (Optional)
    re.DOTALL  # Allow matching across multiple lines
)

@dp.message()
async def handle_message(message: Message):
    """Parse incoming trade messages and execute orders."""
    match = ORDER_PATTERN.search(message.text)
    if not match:
        await message.reply("Invalid order format. Please check your input.")
        return

    tag, symbol, side, order_type, price, risk_pct, sl_pct, tp_pct, qty = match.groups()

    logger.info(f"tag: {tag}")
    logger.info(f"symbol: {symbol}")
    logger.info(f"side: {side}")
    logger.info(f"order_type: {order_type}")
    logger.info(f"price: {price}")
    logger.info(f"risk_pct: {risk_pct}")
    logger.info(f"sl_pct: {sl_pct}")
    logger.info(f"tp_pct: {tp_pct}")
    logger.info(f"Qty: {qty}")

    price = float(price) if price else None
    risk_pct = float(risk_pct) if risk_pct else None
    sl_pct = float(sl_pct) if sl_pct else None
    tp_pct = float(tp_pct) if tp_pct else None

    with open('env.json', 'r') as file:
        credentials = json.load(file).get("credentials", [])
    
    account_no = 0

    if tag == "init":

        for creds in credentials:
            account_no += 1
            api_key = creds['API_KEY']
            secret_key = creds['API_SECRET']

            #print(api_key)
            #print(secret_key)
        
            try:
                qty, leverage = position_size_calc(api_key, secret_key, risk_pct, sl_pct, symbol)
                update_leverage(api_key, secret_key, symbol, leverage)
                current_price = get_current_price(symbol)
                # Place Market Order
                place_order(api_key, secret_key, symbol, side, 'MARKET', qty)

                # Calculate TP/SL prices
                if tp_pct and side.upper() == 'BUY':
                    tp_price = current_price * (1 + tp_pct)
                    sl_price = current_price * (1 - sl_pct)
                    
                    tp_price = str(tp_price)
                    sl_price = str(sl_price)
                    qty = str(qty)

                    place_order(api_key, secret_key, symbol, 'SELL', 'LIMIT', qty, tp_price)
                    place_order(api_key, secret_key, symbol, 'SELL', 'STOP_MARKET', 0, sl_price)

                elif sl_pct and side.upper() == 'SELL':
                    tp_price = current_price * (1 - tp_pct)
                    sl_price = current_price * (1 + sl_pct)

                    tp_price = str(tp_price)
                    sl_price = str(sl_price)
                    qty = str(qty)

                    place_order(api_key, secret_key, symbol, 'BUY', 'LIMIT', qty, tp_price)
                    place_order(api_key, secret_key, symbol, 'BUY', 'STOP_MARKET', 0, sl_price)

                response_msg = f"For account {account_no} Market Order, TP & SL placed successfully for {symbol}."
                await message.reply(response_msg)
            
            except:
                response_msg = f"For account {account_no}, There was an error in the message!"
                await message.reply(response_msg)
    
    elif tag == "modify_tp":

        for creds in credentials:
            account_no += 1
            api_key = creds['API_KEY']
            secret_key = creds['API_SECRET']

            try:
                response_dict = cancel_orders_for_a_symbol(api_key, secret_key, symbol, 'LIMIT')

                qty = response_dict['LIMIT_QTY']
                tp_price = str(price)
                qty = str(qty)

                place_order(api_key, secret_key, symbol, side, 'LIMIT', qty, tp_price)
                
                response_msg = f"For account {account_no}, TP on {side} side for {symbol} modified to {price}."
                await message.reply(response_msg)

            except Exception as e:
                response_msg = f"For account {account_no}, There was an error! {e}"
                await message.reply(response_msg)
    
    elif tag == "place_tp":

        for creds in credentials:
            account_no += 1
            api_key = creds['API_KEY']
            secret_key = creds['API_SECRET']

            tp_price = str(price)
            qty = str(qty)

            try:
                place_order(api_key, secret_key, symbol, side, 'LIMIT', qty, tp_price)
                response_msg = f"For account {account_no}, TP on {side} side for {symbol} placed AT {price}."
                await message.reply(response_msg)
            
            except Exception as e:
                response_msg = f"For account {account_no}, There was an error! {e}"
                await message.reply(response_msg)
    
    elif tag == "place_sl":

        for creds in credentials:
            account_no += 1
            api_key = creds['API_KEY']
            secret_key = creds['API_SECRET']

            sl_price = str(price)
            side = str(side)
            
            if qty:
                qty = str(qty)
            else:
                qty = 0

            try:
                place_order(api_key, secret_key, symbol, side, 'STOP_MARKET', qty, sl_price)
                response_msg = f"For account {account_no}, SL on {side} side for {symbol} placed AT {price}."
                await message.reply(response_msg)
            
            except Exception as e:
                response_msg = f"For account {account_no}, There was an error! {e}"
                await message.reply(response_msg)

    elif tag == "trail_sl":

        for creds in credentials:
            account_no += 1
            api_key = creds['API_KEY']
            secret_key = creds['API_SECRET']

            try:
                response_dict = cancel_orders_for_a_symbol(api_key, secret_key, symbol, 'STOP_MARKET')
                qty = float(response_dict['STOP_MARKET_QTY'])
                print("Stop Market Qty: ", qty)

                sl_price = str(price)
                qty = str(qty)

                place_order(api_key, secret_key, symbol, side, 'STOP_MARKET', 0, sl_price)
                
                response_msg = f"For account {account_no}, Stop Loss Market on {side} side for {symbol} modified to {price}."
                await message.reply(response_msg)

            except Exception as e:
                response_msg = f"For account {account_no}, There was an error!"
                await message.reply(response_msg)

    elif tag == "cancel_all_open_orders":

        for creds in credentials:
            account_no += 1
            api_key = creds['API_KEY']
            secret_key = creds['API_SECRET']

            try:
                cancel_orders_for_a_symbol(api_key, secret_key, symbol, 'LIMIT')
                cancel_orders_for_a_symbol(api_key, secret_key, symbol, 'STOP_MARKET')
                response_msg = f"For account {account_no}, Cancelled all LIMIT and STOP MARKET orders for {symbol}."
                await message.reply(response_msg)
            except Exception as e:
                response_msg = f"For account {account_no}, There was an error!"
                await message.reply(response_msg)

    elif tag == "close_positions_for_symbol":

        for creds in credentials:
            account_no += 1
            api_key = creds['API_KEY']
            secret_key = creds['API_SECRET']

            try:
                
                qty = str(qty)

                place_order(api_key, secret_key, symbol, side, 'MARKET', qty)
                cancel_orders_for_a_symbol(api_key, secret_key, symbol, 'LIMIT')
                cancel_orders_for_a_symbol(api_key, secret_key, symbol, 'STOP_MARKET')
                response_msg = f"For account {account_no}, Closed all Positions and Cancelled All Open Orders for {symbol}."
                await message.reply(response_msg)

            except Exception as e:
                response_msg = f"There was an error! {e}"
                await message.reply(response_msg)
            
    else:
        message.reply(f"Unknown tag: {tag}")
        return

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
