from kafka import KafkaProducer
import json
from config import Config

producer = KafkaProducer(
    bootstrap_servers=[Config.KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_order_event(order_data):
    producer.send(Config.KAFKA_TOPIC, order_data)
    producer.flush()
