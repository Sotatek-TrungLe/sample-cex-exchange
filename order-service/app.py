import os
from flask import Flask, jsonify, request
from models import db, Order
from kafka_producer import publish_order_event
from redis import Redis
from config import Config
import json
from utils import check_user_balance, cache_order_status  # Import the balance check utility
from logger import logger  # Import logger

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database and Redis
db.init_app(app)
redis_client = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# Initialize the database with the app context
with app.app_context():

    db.create_all()  # Creates tables if they don't exist

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    user_id = data.get('user_id')
    asset = data.get('asset')
    quantity = data.get('quantity')
    price = data.get('price')
    order_type = data.get('order_type')

    if not all([user_id, asset, quantity, price, order_type]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user has sufficient balance using the imported utility function
    is_balance_sufficient, error_message = check_user_balance(user_id, asset, quantity, order_type)
    if not is_balance_sufficient:
        return jsonify({'error': error_message}), 400

    # Create the order
    order = Order(
        user_id=user_id,
        asset=asset,
        quantity=quantity,
        price=price,
        order_type=order_type
    )
    db.session.add(order)
    db.session.commit()

    # Cache the order in Redis for quick access
    redis_client.set(f"order:{order.id}", json.dumps(order.to_dict()))

    # Publish order event to Kafka
    order_data = order.to_dict()
    publish_order_event(order_data)

    return jsonify(order_data), 201

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    # Try to get the order from Redis cache
    order_data = redis_client.get(f"order:{order_id}")
    if order_data:
        return jsonify(json.loads(order_data)), 200

    # Fall back to database if not in cache (optional)
    db_order = Order.query.get(order_id)
    if db_order:
        # Cache the order data for next time
        cache_order_status(db_order.to_dict())
        return jsonify(db_order.to_dict()), 200

    return jsonify({"error": "Order not found"}), 404


@app.route('/orders', methods=['GET'])
def list_orders():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("FLASK_RUN_PORT", 5000)))

