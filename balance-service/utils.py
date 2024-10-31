from redis import Redis
from config import Config

# Initialize Redis client
redis_client = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

def cache_balance(user_id, asset, amount):
    """Cache user balance in Redis"""
    redis_client.hset(f"user:{user_id}:balance", asset, amount)

def get_cached_balance(user_id, asset):
    """Retrieve cached balance from Redis"""
    balance = redis_client.hget(f"user:{user_id}:balance", asset)
    if balance:
        return float(balance)
    return None

def invalidate_balance_cache(user_id):
    """Invalidate balance cache for a specific user"""
    redis_client.delete(f"user:{user_id}:balance")
