
# Required installations:
# pip install python-socketio

import socketio

# WebSocket server URL
server_url = 'https://fawss.pi42.com/'

# Create a new Socket.IO client
sio = socketio.Client()

# Event listener for when the connection is open
@sio.event
def connect():
    print('Connected to WebSocket server')
    subscribe_to_topics()

# Event listener for when the connection is closed
@sio.event
def disconnect():
    print('Disconnected from WebSocket server')

# Event listener for errors
@sio.event
def connect_error(data):
    print('Socket.IO connection error:', data)

# Event listener for general errors
@sio.on('error')
def handle_error(data):
    print('Socket.IO error:', data)

# Function to subscribe to various WebSocket topics
def subscribe_to_topics():
    topics = ['btcinr@depth_0.1', 'btcinr@markPrice']  # List of topics to subscribe to

    # Subscribe to each topic
    sio.emit('subscribe', {
        'params': topics  # Sends the topics array to the WebSocket server
    })

    # Event listeners for updates on various data topics
    @sio.on('depthUpdate')
    def on_depth_update(data):
        print('depthUpdate:', data)

    @sio.on('kline')
    def on_kline(data):
        print('kline:', data)

    @sio.on('markPriceUpdate')
    def on_mark_price_update(data):
        print('markPriceUpdate:', data)

    @sio.on('aggTrade')
    def on_agg_trade(data):
        print('aggTrade:', data)

    @sio.on('24hrTicker')
    def on_24hr_ticker(data):
        print('24hrTicker:', data)

    @sio.on('marketInfo')
    def on_market_info(data):
        print('marketInfo:', data)

    @sio.on('markPriceArr')
    def on_mark_price_arr(data):
        print('markPriceArr:', data)

    @sio.on('tickerArr')
    def on_ticker_arr(data):
        print('tickerArr:', data)

    @sio.on('marginRate')
    def on_margin_rate(data):
        print('marginRate:', data)

# Connect to the WebSocket server
sio.connect(server_url)

# Keep the connection open
sio.wait()