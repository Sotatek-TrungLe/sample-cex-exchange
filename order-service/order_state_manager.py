from kafka import KafkaConsumer
import json
from config import Config
from models import db, Order
from utils import cache_order_status
from logger import logger
from app import app  # Import the Flask app

# Initialize Kafka consumer for order state updates
consumer = KafkaConsumer(
    Config.ORDER_STATE_TOPIC,
    bootstrap_servers=[Config.KAFKA_BROKER],
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def update_order_in_db(order_id, status, filled_quantity):
    """Update the order status in the database."""
    db_order = Order.query.get(order_id)
    if db_order:
        db_order.status = status
        db_order.filled_quantity = filled_quantity
        db.session.commit()
        logger.info(f"Order {order_id} updated in database to status {status} with filled quantity {filled_quantity}")

def process_order_state_updates():
    """Listen for order state changes from Kafka and update Redis and database."""
    logger.info("Order state manager started listening for order state changes.")
    for message in consumer:
        order_state = message.value
        order_id = order_state['order_id']
        status = order_state['status']
        filled_quantity = order_state['filled_quantity']

        # Update in Redis cache with full order data
        cache_order_status(order_state)
        logger.info(f"Order {order_id} updated in Redis to status {status}")

        # Update in the database
        update_order_in_db(order_id, status, filled_quantity)


if __name__ == "__main__":
    with app.app_context():
        process_order_state_updates()