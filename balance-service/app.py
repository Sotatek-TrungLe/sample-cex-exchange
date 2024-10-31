import os, redis
from flask import Flask, jsonify, request
from models import db, Balance
from utils import cache_balance, get_cached_balance, invalidate_balance_cache
from config import Config
from logger import logger  # Import logger

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Redis client
redis_client = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)


# Initialize database
db.init_app(app)

# Initialize the database with the app context
with app.app_context():
    db.create_all()  # Creates tables if they don't exist


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Balance Service is running"}), 200

@app.route('/balance/<int:user_id>', methods=['GET'])
def get_balance(user_id):
    """Get the user's balance for all assets"""
    balances = Balance.query.filter_by(user_id=user_id).all()
    if not balances:
        return jsonify({'error': 'No balance found for this user'}), 404

    # Fetch from the database and cache in Redis
    print(balances)
    balance_data = {}
    for balance in balances:
        balance_data[balance.asset] = balance.amount
        cache_balance(user_id, balance.asset, balance.amount)

    return jsonify(balance_data), 200

@app.route('/balance/<int:user_id>/<asset>', methods=['GET'])
def get_balance_for_asset(user_id, asset):
    """Get the user's balance for a specific asset"""
    # Check Redis cache first
    cached_balance = get_cached_balance(user_id, asset)
    if cached_balance is not None:
        return jsonify({asset: float(cached_balance)}), 200

    # If not in cache, fetch from the database
    balance = Balance.query.filter_by(user_id=user_id, asset=asset).first()
    if not balance:
        return jsonify({'error': 'No balance found for this asset'}), 404

    # Cache the balance in Redis
    cache_balance(user_id, asset, balance.amount)

    return jsonify({asset: balance.amount}), 200

@app.route('/balance/update', methods=['POST'])
def update_balance():
    trade = request.json
    """Update the buyer's and seller's balance based on the trade."""
    try:
        # Extract trade details
        buyer_user_id = trade['buyer_user_id']
        seller_user_id = trade['seller_user_id']
        asset = trade['asset']  # e.g., 'ADA'
        quantity = trade['quantity']
        price = trade['price']  # Price per unit in USDT

        # Calculate the total USDT cost for the buyer
        total_cost_usdt = quantity * price

        # Step 1: Update balances in Redis for fast access
        redis_client.hincrbyfloat(f"user:{buyer_user_id}:balance", asset, quantity)    # Buyer gains asset
        redis_client.hincrbyfloat(f"user:{buyer_user_id}:balance", 'USDT', -total_cost_usdt)  # Buyer loses USDT

        redis_client.hincrbyfloat(f"user:{seller_user_id}:balance", asset, -quantity)  # Seller loses asset
        redis_client.hincrbyfloat(f"user:{seller_user_id}:balance", 'USDT', total_cost_usdt)  # Seller gains USDT

        # Step 2: Update balances in PostgreSQL for persistence
        # Update buyer's asset balance in PostgreSQL
        buyer_asset_balance = Balance.query.filter_by(user_id=buyer_user_id, asset=asset).first()
        if not buyer_asset_balance:
            buyer_asset_balance = Balance(user_id=buyer_user_id, asset=asset, amount=0)
            db.session.add(buyer_asset_balance)
        buyer_asset_balance.amount += quantity

        # Update buyer's USDT balance in PostgreSQL
        buyer_usdt_balance = Balance.query.filter_by(user_id=buyer_user_id, asset='USDT').first()
        if not buyer_usdt_balance:
            buyer_usdt_balance = Balance(user_id=buyer_user_id, asset='USDT', amount=0)
            db.session.add(buyer_usdt_balance)
        buyer_usdt_balance.amount -= total_cost_usdt

        # Update seller's asset balance in PostgreSQL
        seller_asset_balance = Balance.query.filter_by(user_id=seller_user_id, asset=asset).first()
        if not seller_asset_balance:
            seller_asset_balance = Balance(user_id=seller_user_id, asset=asset, amount=0)
            db.session.add(seller_asset_balance)
        seller_asset_balance.amount -= quantity

        # Update seller's USDT balance in PostgreSQL
        seller_usdt_balance = Balance.query.filter_by(user_id=seller_user_id, asset='USDT').first()
        if not seller_usdt_balance:
            seller_usdt_balance = Balance(user_id=seller_user_id, asset='USDT', amount=0)
            db.session.add(seller_usdt_balance)
        seller_usdt_balance.amount += total_cost_usdt

        # Commit changes to PostgreSQL atomically
        db.session.commit()

        # Step 3: Cache updated balances in Redis for fast reads
        cache_balance(buyer_user_id, asset, buyer_asset_balance.amount)
        cache_balance(buyer_user_id, 'USDT', buyer_usdt_balance.amount)
        cache_balance(seller_user_id, asset, seller_asset_balance.amount)
        cache_balance(seller_user_id, 'USDT', seller_usdt_balance.amount)

        logger.info(f"Balance updated in both Redis and PostgreSQL for trade: {trade}")
        return jsonify({"status": "success", "message": "Balance updated"}), 200


    except Exception as e:
        db.session.rollback()  # Rollback PostgreSQL transaction if any error occurs
        logger.error(f"Error updating balance for trade: {trade} - {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("FLASK_RUN_PORT", 5000)))

