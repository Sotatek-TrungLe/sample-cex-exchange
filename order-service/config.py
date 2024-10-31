import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://admin:admin@order-postgres:5432/order_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis-balance')
    REDIS_PORT = os.getenv('REDIS_PORT', 6379)
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
    KAFKA_TOPIC = 'order-events'
    ORDER_STATE_TOPIC = os.getenv("ORDER_STATE_TOPIC", "order_state_updates")  