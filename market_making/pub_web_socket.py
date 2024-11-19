import socketio
import asyncio
from helpers import place_order, get_current_price, delete_order
from generate_listen import create_or_update_listen_key, update_listen_key_expiry
from redis.asyncio import Redis

# Redis client setup
redis_client = Redis(host='localhost', port=6379, decode_responses=False)

# WebSocket server URL
server_url = 'https://fawss.pi42.com/'

# Namespace path (you can customize this if needed)
listen_key = create_or_update_listen_key(1)
namespace_path = '/auth-stream/' + listen_key

# Create a new asynchronous Socket.IO client
sio = socketio.AsyncClient()

# Event listener for a successful connection to the server
@sio.event
async def connect():
    print('Connected to WebSocket server')
    await subscribe_to_topics()  # Await the subscribe_to_topics function

# Event listener for when the connection to the server is closed
@sio.event
async def disconnect():
    print('Disconnected from WebSocket server')

# Function to subscribe to various WebSocket topics
async def subscribe_to_topics():
    topics = ['btcusdt@markPrice']  # Topics to subscribe to
    
    # Subscribe to each topic
    await sio.emit('subscribe', {'params': topics})

    # Event listeners for updates on various data topics
    @sio.on('depthUpdate')
    async def on_depth_update(data):
        print('depthUpdate:', data)

    @sio.on('kline')
    async def on_kline(data):
        print('kline:', data)

    @sio.on('markPriceUpdate')
    async def on_mark_price_update(data):
        print('markPriceUpdate:', data)

    @sio.on('aggTrade')
    async def on_agg_trade(data):
        print('aggTrade:', data)

    @sio.on('24hrTicker')
    async def on_24hr_ticker(data):
        print('24hrTicker:', data)

    @sio.on('marketInfo')
    async def on_market_info(data):
        print('marketInfo:', data)

    @sio.on('markPriceArr')
    async def on_mark_price_arr(data):
        print('markPriceArr:', data)

    @sio.on('tickerArr')
    async def on_ticker_arr(data):
        print('tickerArr:', data)

    @sio.on('marginRate')
    async def on_margin_rate(data):
        print('marginRate:', data)

# Event listener for connection errors
@sio.event
async def connect_error(data):
    print('Failed to connect to WebSocket server:', data)

# Main function to initiate and maintain the WebSocket connection
async def main():
    try:
        # Attempt to connect to the server
        await sio.connect(server_url, transports=["websocket"])
        await sio.wait()  # Keeps the connection open to listen for events
    except Exception as e:
        print("Connection error:", e)

if __name__ == '__main__':
    asyncio.run(main())
