import socketio
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('API_KEY_1')

sio = socketio.Client()

@sio.event(namespace='/orderupdates')
def connect():
    print("Connected to the WebSocket server.")
    subscribe_data = {
        'event': 'subscribe',
        'apikey': api_key
    }

    sio.emit('FETCH_ORDER_UPDATES', subscribe_data, namespace='/orderupdates')

@sio.on('ORDER_UPDATE', namespace='/orderupdates')
def order_update(data):
    print("Received an order update:", data)

    if data.get('status') == 'filled':
        print(f"Order {data.get('order_id')} is filled.")

@sio.event(namespace='/orderupdates')
def disconnect():
    print("Disconnected from the WebSocket server.")


@sio.event(namespace='/orderupdates')
def connect_error(data):
    print("Connection failed:", data)

try:
    sio.connect(
        url='wss://ws.coinswitch.co',
        namespaces=['/orderupdates'],
        transports=['websocket'],
        socketio_path='/pro/realtime-rates-socket/spot/order-updates',
        wait=True,
        wait_timeout=3600
    )
    sio.wait() 
except Exception as e:
    print("An error occurred:", e)
