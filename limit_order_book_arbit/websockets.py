

import socketio
import json
server_url = 'https://fawss.pi42.com/'

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to WebSocket server')
    subscribe_to_topics()

@sio.event
def disconnect():
    print('Disconnected from WebSocket server')

@sio.event
def connect_error(data):
    print('Socket.IO connection error:', data)

@sio.on('error')
def handle_error(data):
    print('Socket.IO error:', data)

def subscribe_to_topics():
    topics = ['btcusdt@depth_0.1', 'btcusdt@kline_1m']  

    sio.emit('subscribe', {
        'params': topics  
    })

    @sio.on('depthUpdate')
    def on_depth_update(data):
        try:
            best_bid = data.get('b', [])[-1] if data.get('b') else None  # Last bid
            best_ask = data.get('a', [])[0] if data.get('a') else None  # First ask

            if not best_bid or not best_ask:
                raise ValueError("Bids or asks data is missing or incomplete.")

            result = {
                "best_bid": {
                    "price": float(best_bid[0]),
                    "quantity": float(best_bid[1])
                },
                "best_ask": {
                    "price": float(best_ask[0]),
                    "quantity": float(best_ask[1])
                }
            }
            print(result)
            return result
        except Exception as e:
            print(f"Error processing depth update: {e}")
            return {"error": str(e)}

    @sio.on('kline')
    def on_kline(data):
        print('kline:', data)

    @sio.on('markPriceUpdate')
    def on_mark_price_update(data):
        print('markPriceUpdate:', data)

sio.connect(server_url)
sio.wait()