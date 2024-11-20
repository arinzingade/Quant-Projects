
import socketio
import asyncio
from generate_listen import create_or_update_listen_key, update_listen_key_expiry
from redis.asyncio import Redis
from async_helpers import place_order, place_bracket_limit_orders, cancel_counter_order
from main import upper_pct, lower_pct, place_bracket_limit_orders, symbol, qty
from helpers import place_order, get_current_price, close_all_positions, cancel_all_orders
import winsound

redis_client = Redis(host='localhost', port=6379, decode_responses=False)

# WebSocket server URL (without namespace)
server_url = 'https://fawss.pi42.com/'

lock = asyncio.Lock()
# Namespace path for authorized streaming
listen_key = create_or_update_listen_key(2)
namespace_path = '/auth-stream/' + listen_key

# Create a new asynchronous Socket.IO client
sio = socketio.AsyncClient()

# Event listener for a successful connection to the server
@sio.event
async def connect():
    print('Successfully connected to the WebSocket server')

# Event listener for when the connection to the server is closed
@sio.event
async def disconnect():
    
    frequency = 500 
    duration = 750    
    winsound.Beep(frequency, duration)
    print('Disconnected from the WebSocket server')


# Event handler for receiving an order filled notification
@sio.on('orderFilled', namespace=namespace_path)
async def on_order_filled(data):  # Accept data parameter
    async with lock:
        client_order_id = data.get('clientOrderId')
        await cancel_counter_order(2, client_order_id)


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

execution_lock = asyncio.Lock()
# Event handler for receiving a failed order notification
@sio.on('orderFailed', namespace=namespace_path)
async def on_order_failed(data):
    client_order_id = data.get('clientOrderId')
    print("Order FAILED for ID: ", client_order_id)

    frequency = 500 
    duration = 750    
    winsound.Beep(frequency, duration)

    await close_all_positions(1)
    await cancel_all_orders(1)
    await close_all_positions(2)
    await cancel_all_orders(2)

    await close_all_positions(1)
    await cancel_all_orders(1)
    await close_all_positions(2)
    await cancel_all_orders(2)

    print("ALL POSITIONS CANCELLED AND CLOSED")
    await restart_process()
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
    
    print("SEESION FOR WEB SOCKET 2 HAS EXPIRED.")

    frequency = 500 
    duration = 750    
    winsound.Beep(frequency, duration)
    
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
    await restart_process()
    place_bracket_limit_orders(1, symbol, qty, upper_pct, lower_pct, 'NEUTRAL')
    
    print("-------------------------------------")
    print("Process Restarted.")
    print("-------------------------------------")

# Event listener for connection errors
@sio.event
async def connect_error(data):
    print('Failed to connect to the WebSocket server:', data)

async def restart_process():
    print("Restarting the WebSocket connection...")
    await sio.disconnect()  # Disconnect the current session
    await connect_to_server()  # Reconnect to the server

async def connect_to_server():
    try:
        print("Attempting to connect to the WebSocket server...")
        await sio.connect(server_url, transports=["websocket"])
        await sio.wait()  # Keeps the connection open to listen for events
    except Exception as e:
        print("Connection error:", e)

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

