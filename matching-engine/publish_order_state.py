from kafka import KafkaProducer
import json
from config import Config
from logger import logger

# Initialize Kafka producer for order state changes
producer = KafkaProducer(
    bootstrap_servers=[Config.KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_order_state(order):
    """Publish order state changes to Kafka."""
    order_state = {
        "order_id": order.order_id,
        "user_id": order.user_id,
        "status": order.status,
        "filled_quantity": order.filled_quantity,
        "asset": order.asset,
        "quantity": order.quantity,
        "price": order.price
    }
    producer.send(Config.ORDER_STATE_TOPIC, order_state)
    producer.flush()
    logger.info(f"Order state published: {order_state}")
