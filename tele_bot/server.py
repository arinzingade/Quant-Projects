

from flask import Flask, request, jsonify
from coin_class import ApiTradingClient
from coinswitch import place_order, update_leverage
import logging
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

@app.route('/api/v1/place_order', methods = ['GET', 'POST'])
def place_order_method():
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        api_key = data.get('api_key')
        secret_key = data.get('api_secret')
        symbol = data.get('symbol')
        side = data.get('side')
        order_type = data.get('order_type')
        qty = data.get('qty')

        leverage = os.getenv('LEVERAGE')
        update_leverage(api_key, secret_key, symbol, leverage)
        status = place_order(api_key, secret_key, symbol, side, order_type, qty)
        
        return jsonify({"message:": status}), 200

    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"Error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port = 5000)