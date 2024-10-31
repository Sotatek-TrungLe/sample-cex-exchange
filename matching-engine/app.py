from flask import Flask
from flask_socketio import SocketIO
# from flask_cors import CORS
import redis
import json
import threading
import logging
import os
from config import Config
import eventlet

# Set up Flask and Flask-SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_need_change'


# Initialize SocketIO with Redis as the message queue
eventlet.monkey_patch()  # Apply monkey patching

socketio = SocketIO(
    app,
    message_queue=f'redis://{Config.REDIS_OB_WS_HOST}:{Config.REDIS_OB_WS_PORT}',
    async_mode='eventlet',
    cors_allowed_origins="*" 
)

# Initialize Redis client and logger
redis_client = redis.StrictRedis(host=Config.REDIS_OB_WS_HOST, port=Config.REDIS_OB_WS_PORT, db=0)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('socket_order_book')

def redis_listener():
    """Listen for messages from Redis and emit them to clients."""
    pubsub = redis_client.pubsub()
    pubsub.subscribe('order_book_channel')

    last_emitted_snapshot = None  # Track the last emitted snapshot

    for message in pubsub.listen():
        if message['type'] == 'message':
            # Decode the new order book snapshot from Redis
            new_snapshot = message['data'].decode('utf-8')
            
            # Only emit if the new snapshot is different from the last emitted snapshot
            if new_snapshot != last_emitted_snapshot:
                socketio.emit('order_book_update', new_snapshot)
                last_emitted_snapshot = new_snapshot 

@app.route('/')
def index():
    return "Flask-SocketIO Server Running"

if __name__ == '__main__':
    # Start Redis listener in a background thread
    listener_thread = threading.Thread(target=redis_listener)
    listener_thread.daemon = True
    listener_thread.start()

    # Start Flask-SocketIO server
    logger.info("Starting Flask-SocketIO server...")
    socketio.run(app, host='0.0.0.0', port=int(os.getenv("FLASK_RUN_PORT", 5000)),debug=True)
