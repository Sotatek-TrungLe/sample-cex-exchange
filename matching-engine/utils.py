from kafka import KafkaProducer, KafkaConsumer
from config import Config
import json
import redis
from logger import logger  # Import logger
from order_book import Order

# Initialize Kafka producer for publishing trade events
producer = KafkaProducer(
    bootstrap_servers=[Config.KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Initialize Redis for balance check
redis_client = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

def check_user_balance(user_id, asset, required_quantity, order_type):
    """Check the user's balance from Redis before placing or matching an order."""
    balance = float(redis_client.hget(f"user:{user_id}:balance", asset) or 0)
    if order_type == 'buy' and balance >= required_quantity:
        return True
    elif order_type == 'sell' and balance >= required_quantity:
        return True
    logger.warning(f"Insufficient balance for user {user_id} on {asset} for {order_type} order")
    return False

def publish_trade(trade_data):
    """Publishes a trade event to Kafka."""
    producer.send(Config.TRADE_TOPIC, trade_data)
    producer.flush()
    logger.info(f"Trade event published: {trade_data}")

def consume_orders(order_book):
    """Consumes order events from Kafka and checks balance before adding to the order book."""
    consumer = KafkaConsumer(
        Config.ORDER_TOPIC,
        bootstrap_servers=[Config.KAFKA_BROKER],
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    logger.info("Waiting for messages from order_events topic...")
    for message in consumer:
        order_data = message.value

        logger.debug(f"Received order data: {order_data}")
        # Check balance before adding to order book
        if check_user_balance(order_data['user_id'], order_data['asset'], order_data['quantity'], order_data['order_type']):
            order = Order(
                order_id=order_data['id'],
                user_id=order_data['user_id'],
                asset=order_data['asset'],
                price=order_data['price'],
                quantity=order_data['quantity'],
                order_type=order_data['order_type']
            )
            order_book.add_order(order)
            logger.info(f"Order added to book: {order_data}")
        else:
            logger.warning(f"Insufficient balance for order: {order_data}")

