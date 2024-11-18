
import socketio
import asyncio
from generate_listen import create_or_update_listen_key, update_listen_key_expiry
from helpers import place_order, get_current_price, close_all_positions, cancel_all_orders
import redis
from helpers import delete_order

from main import upper_pct, lower_pct, place_bracket_limit_orders, symbol, qty

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# WebSocket server URL (without namespace)
server_url = 'https://fawss.pi42.com/'

# Namespace path for authorized streaming
listen_key = create_or_update_listen_key(1)
namespace_path = '/auth-stream/' + listen_key

SWITCH = 1
CYCLE=1

# Create a new asynchronous Socket.IO client
sio = socketio.AsyncClient()


# Event listener for a successful connection to the server
@sio.event
async def connect():
    print('Successfully connected to the WebSocket server')

# Event listener for when the connection to the server is closed
@sio.event
async def disconnect():
    print('Disconnected from the WebSocket server')

#execution_lock = asyncio.Lock()
# Event handler for receiving an order filled notification
@sio.on('orderFilled', namespace=namespace_path)
async def on_order_filled(data):  # Accept data parameter
    global SWITCH
    global CYCLE

    print("Cycle Number is: ", CYCLE)

    order_side = data.get('side')
    symbol = data.get('symbol')
    qty = data.get('orderAmount')
    type_order = data.get('type')
    
    client_order_id = data.get('clientOrderId')

    print(type_order)

    if client_order_id:
        print(f"Order filled: {client_order_id}")
        counter_order_id = redis_client.get(client_order_id)

        if counter_order_id:
            counter_order_id = counter_order_id.decode('utf-8')
            print(f"Counter order {counter_order_id} found. Cancelling it.")
            delete_order(1, counter_order_id)

            redis_client.delete(client_order_id)
            redis_client.delete(counter_order_id)

            print("-------------------------------------------------------------------------------")
        else:
            print("No counter order found.")

    if SWITCH==1:

        if order_side == 'BUY':
            place_order(2, symbol, 0, 'MARKET', qty, 'SELL', False)
            place_bracket_limit_orders(1, symbol, qty, upper_pct, lower_pct, 'BUY')
            place_bracket_limit_orders(2,symbol, qty, upper_pct, lower_pct, 'SELL')
            print('Opening BUY side positions')
            
        elif order_side == 'SELL':
            place_order(2, symbol, 0, 'MARKET', qty, 'BUY', False)
            place_bracket_limit_orders(1, symbol, qty, upper_pct, lower_pct, 'SELL')
            place_bracket_limit_orders(2,symbol, qty, upper_pct, lower_pct, 'BUY')
            print('Opening SELL side positions')

        SWITCH = 0
    
    else:
        
        place_bracket_limit_orders(1, symbol, qty, upper_pct, lower_pct, 'NEUTRAL')
        print('OPENING LIMIT ORDER POSITIONS')
        CYCLE += 1
        SWITCH = 1


# Event handler for receiving a partially filled order update
@sio.on('orderPartiallyFilled', namespace=namespace_path)
async def on_order_partially_filled(data):
    client_order_id = data.get('clientOrderId')
    print("Order PARTIALLY for ID: ", client_order_id)

# Event handler for receiving a cancelled order notification
@sio.on('orderCancelled', namespace=namespace_path)
async def on_order_cancelled(data):
    client_order_id = data.get('clientOrderId')
    print("Order cancelled for ID: ", client_order_id)

# Event handler for receiving a failed order notification
@sio.on('orderFailed', namespace=namespace_path)
async def on_order_failed(data):
    client_order_id = data.get('clientOrderId')
    print("Order FAILED for ID: ", client_order_id)

    close_all_positions(1)
    cancel_all_orders(1)
    close_all_positions(2)
    cancel_all_orders(2)

    close_all_positions(1)
    cancel_all_orders(1)
    close_all_positions(2)
    cancel_all_orders(2)

    print("ALL POSITIONS CANCELLED AND CLOSED")

    print("RESTARTING THE PROCESS")

    place_bracket_limit_orders(1, symbol, qty, upper_pct, lower_pct, 'NEUTRAL')
    
# Event handler for receiving a new order(TP/SL) notification
@sio.on('newOrder', namespace=namespace_path)
async def on_new_order(data):
    client_order_id = data.get('clientOrderId')
    print("Position Opened for ID: ", client_order_id)

# Event handler for receiving a position update
@sio.on('updatePosition', namespace=namespace_path)
async def on_update_position(data):
    client_order_id = data.get('clientOrderId')
    print("Position Updated for ID: ", client_order_id)

# Event handler for receiving a position close notification
@sio.on('closePosition', namespace=namespace_path)
async def on_close_position(data):
    client_order_id = data.get('clientOrderId')
    print("Position Closed for ID: ", client_order_id)

# Event handler for receiving a new trade notification
@sio.on('newTrade', namespace=namespace_path)
async def on_new_trade(data):
    client_order_id = data.get('clientOrderId')
    print("New Trade for ID: ", client_order_id)

# Event handler for session expiration notifications
@sio.on('sessionExpired', namespace=namespace_path)
async def on_session_expired(data):
        
    print("SEESION FOR WEB SOCKET 1 HAS EXPIRED.")
    
    close_all_positions(1)
    cancel_all_orders(1)
    close_all_positions(2)
    cancel_all_orders(2)

    close_all_positions(1)
    cancel_all_orders(1)
    close_all_positions(2)
    cancel_all_orders(2)

    print("ALL POSITIONS CANCELLED AND CLOSED")

    print("RESTARTING THE PROCESS")

    place_bracket_limit_orders(1, symbol, qty, upper_pct, lower_pct, 'NEUTRAL')
    
    print("-------------------------------------")
    print("Process Restarted.")
    print("-------------------------------------")

# Event listener for connection errors
@sio.event
async def connect_error(data):
    print('Failed to connect to the WebSocket server:', data)

# Main function to initiate and maintain the WebSocket connection
async def main():
    try:
        # Attempt to connect to the server with specified transports
        await sio.connect(server_url, transports=["websocket"])
        await sio.wait()  # Keeps the connection open to listen for events
    except Exception as e:
        print("Connection error:", e)

if __name__ == '__main__':
    asyncio.run(main())

