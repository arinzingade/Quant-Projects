
from coinswitch import place_order
import json
from dotenv import load_dotenv
import os
import logging

load_dotenv()

qty = os.getenv('QTY')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


def clone_orders(file_path, symbol, side, order_type, qty):
    qty = 0.002
    try:
        with open(file_path, 'r') as file:
            credentials = json.load(file).get("credentials", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading credentials: {e}")
        return
    
    # Loop through each API key and secret
    for index, credential in enumerate(credentials):
        api_key = credential.get("API_KEY")
        api_secret = credential.get("API_SECRET")

        if not api_key or not api_secret:
            print(f"Skipping invalid credential entry at index {index}")
            continue

        # Place order for each credential
        try:
            response = place_order(
                api_key=api_key,
                secret_key=api_secret,
                symbol=symbol,
                side=side,
                order_type=order_type,
                qty=qty
            )
            logger.info(f"Order placed successfully for API_KEY {api_key[:4]}...: {response}")
        except Exception as e:
            logger.error(f"Error placing order for API_KEY {api_key[:4]}...: {e}")