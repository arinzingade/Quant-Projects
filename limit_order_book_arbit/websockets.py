

import socketio
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


        last_bid = data['b'][-1]  
        first_ask = data['a'][0]  

        # Print the extracted values
        print(f"Last Bid Price: {last_bid}")
        print(f"First Ask Price: {first_ask}")
        print("-------------------------------------")

    @sio.on('kline')
    def on_kline(data):
        print('kline:', data)

    @sio.on('markPriceUpdate')
    def on_mark_price_update(data):
        print('markPriceUpdate:', data)

sio.connect(server_url)
sio.wait()