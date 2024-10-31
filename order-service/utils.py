import json
import redis
from config import Config
from logger import logger

# Initialize Redis client
redis_client = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)


def check_user_balance(user_id, asset, quantity, order_type):
    """Checks if the user has sufficient balance for the order directly from Redis"""
    # Retrieve balance data from Redis
    balance_data = redis_client.hgetall(f"user:{user_id}:balance")
    if not balance_data:
        return False, "Balance information not found"

    # Parse balances from Redis data (Redis stores as bytes, so decoding is necessary)
    balance_data = {k: float(v) for k, v in balance_data.items()}  # Removed decode


    if order_type == 'buy':
        # For a buy order, check if the user has enough USDT (or other stablecoin)
        if balance_data.get('USDT', 0) < quantity:
            return False, "Insufficient balance for buy order"
    elif order_type == 'sell':
        # For a sell order, check if the user has enough of the specified asset
        if balance_data.get(asset, 0) < quantity:
            return False, f"Insufficient balance for selling {asset}"
    return True, None


def cache_order_status(order):
    """Cache the entire order status in Redis."""
    redis_key = f"order:{order['order_id']}"
    redis_data = {
        "order_id": order["order_id"],
        "user_id": order["user_id"],
        "asset": order["asset"],
        "price": order["price"],
        "quantity": order["quantity"],
        "filled_quantity": order["filled_quantity"],
        "status": order["status"]
    }
    redis_client.set(redis_key, json.dumps(redis_data))
    logger.info(f"Cached order {order['order_id']} status in Redis: {redis_data}")
