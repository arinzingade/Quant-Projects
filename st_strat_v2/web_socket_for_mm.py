 
import socketio
import asyncio
from generate_listen import create_or_update_listen_key
from async_helpers import place_order, place_bracket_limit_orders, cancel_counter_order
import redis
from helpers import cancel_all_orders, close_all_positions, insert_csv, set_switch, get_switch, toggle_switch
import time
from main import upper_pct, lower_pct, symbol, qty
from redis.asyncio import Redis
import winsound
import subprocess
import pyttsx3

redis_client = Redis(host='localhost', port=6379, decode_responses=False)

# WebSocket server URL (without namespace)
server_url = 'https://fawss.pi42.com/'

# Namespace path for authorized streaming
lock = asyncio.Lock()
listen_key = create_or_update_listen_key(1)
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
    pyttsx3.speak("WebSocket 1 Disconnected.")

    for _ in range(3):  
        subprocess.run(["python", "close.py"], check=True)

    pyttsx3.speak("All Positions Closed")
    subprocess.run(["python", "web_socket_1.py"], check=True)
    pyttsx3.speak("Web Socket 1 started again")

set_switch(1)

@sio.on('orderFilled', namespace=namespace_path)
async def on_order_filled(data):  # Accept data parameter
    
    SWITCH = get_switch()

    async with lock:
        client_order_id = data.get('clientOrderId')
        await cancel_counter_order(1, client_order_id)

        order_side = data.get('side')

        if SWITCH == 1:
            if order_side == 'BUY':
                # Execute the two functions concurrently
                start_time = time.time() 
                await asyncio.gather(
                    place_order(2, symbol, 0, 'MARKET', qty, 'SELL', False),
                    place_bracket_limit_orders(1, symbol, qty, upper_pct, lower_pct, 'BUY'),
                    place_bracket_limit_orders(2, symbol, qty, upper_pct, lower_pct, 'SELL')
                )
                end_time = time.time()  # Capture the end time
        
                time_taken = end_time - start_time  # Calculate the time taken
                print(f"Time taken to complete the orders: {time_taken:.2f} seconds")

            elif order_side == 'SELL':
                # Execute the two functions concurrently
                start_time = time.time() 
                await asyncio.gather(
                    place_order(2, symbol, 0, 'MARKET', qty, 'BUY', False),
                    place_bracket_limit_orders(1, symbol, qty, upper_pct, lower_pct, 'SELL'),
                    place_bracket_limit_orders(2, symbol, qty, upper_pct, lower_pct, 'BUY')
                )
                end_time = time.time()
                time_taken = end_time - start_time  # Calculate the time taken
                print(f"Time taken to complete the orders: {time_taken:.2f} seconds")

            set_switch(0)

        else:
            # Execute the bracket limit orders concurrently
            await place_bracket_limit_orders(1, symbol, qty, upper_pct, lower_pct, 'NEUTRAL')
            insert_csv(qty)
            
            set_switch(1)
    
    frequency = 750
    duration = 300
    winsound.Beep(frequency, duration)
    winsound.Beep(frequency, duration)


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

    pyttsx3.speak("Order Failed")

    for _ in range(3):  
        subprocess.run(["python", "close.py"], check=True)

    print("ALL POSITIONS CANCELLED AND CLOSED")
    pyttsx3.speak("All Positions Closed.")

    print("RESTARTING THE PROCESS")
    subprocess.run(["python", "web_socket_1.py"], check=True)
    pyttsx3.speak("Restarted the WebSocket 1.")
    
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
        
    pyttsx3.speak("Session for WebSocket 1 has expired.")

    for _ in range(3):  
        subprocess.run(["python", "close.py"], check=True)

    pyttsx3.speak("All Positions Closed.")

    print("RESTARTING THE PROCESS")

    subprocess.run(["python", "web_socket_1.py"], check=True)
    pyttsx3.speak("WebSocket 1 Restarted.")
    
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

