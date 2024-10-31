import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://admin:admin@balance-postgres:5432/balance_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis-balance')
    REDIS_PORT = os.getenv('REDIS_PORT', 6379)
