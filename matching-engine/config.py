import os

class Config:
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
    ORDER_TOPIC = os.getenv('ORDER_TOPIC', 'order-events')
    TRADE_TOPIC = os.getenv('TRADE_TOPIC', 'trade-events')
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis-balance')
    REDIS_OB_WS_HOST = os.getenv('REDIS_OB_WS_HOST', 'redis-balance')
    REDIS_PORT = os.getenv('REDIS_PORT', 6379)
    BALANCE_SERVICE_API = os.getenv("BALANCE_SERVICE_API", "http://balance-service:5001/balance/update")
    ORDER_STATE_TOPIC = os.getenv("ORDER_STATE_TOPIC", "order_state_updates")  # Name of the Kafka topic for order states
    REDIS_OB_WS_HOST = os.getenv('REDIS_OB_WS_HOST', 'redis-balance')
    REDIS_OB_WS_PORT = os.getenv('REDIS_OB_WS_PORT', 6379)