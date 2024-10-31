import asyncio
import json
from collections import deque
from logger import logger
from trade_service import send_trade_to_balance_service
from publish_order_state import publish_order_state  
import redis
from config import Config

# Initialize Redis order book client
redis_client_ob_ws = redis.StrictRedis(host=Config.REDIS_OB_WS_HOST, port=6379, db=0)

class Order:
    def __init__(self, order_id, user_id, asset, price, quantity, order_type):
        self.order_id = order_id
        self.user_id = user_id
        self.asset = asset
        self.price = price
        self.quantity = quantity
        self.order_type = order_type  # 'buy' or 'sell'
        self.status = 'open'  # Status can be 'open', 'partially filled', 'filled'
        self.filled_quantity = 0  # Track the quantity that has been filled

    def to_dict(self):
        """Convert order to dictionary for easy serialization."""
        return {
            'order_id': self.order_id,
            'user_id': self.user_id,
            'asset': self.asset,
            'price': self.price,
            'quantity': self.quantity,
            'order_type': self.order_type,
            'status': self.status,
            'filled_quantity': self.filled_quantity,
        }

class OrderBook:
    def __init__(self):
        self.bids = deque()  # Buy orders, sorted in descending order
        self.asks = deque()  # Sell orders, sorted in ascending order

    def add_order(self, order):
        """Add an order to the order book and notify clients."""
        logger.debug(f"Adding order: {order.to_dict()}")
        if order.order_type == 'buy':
            index = 0
            while index < len(self.bids) and self.bids[index].price > order.price:
                index += 1
            self.bids.insert(index, order)
        elif order.order_type == 'sell':
            index = 0
            while index < len(self.asks) and self.asks[index].price < order.price:
                index += 1
            self.asks.insert(index, order)

        logger.debug(f"Current Bids: {[bid.to_dict() for bid in self.bids]}")
        logger.debug(f"Current Asks: {[ask.to_dict() for ask in self.asks]}")

        # After add_order, publish the order book
        self.publish_order_book()

    def match_orders(self):
        """Match orders in the order book and notify clients of changes."""
        trades = []
        while self.bids and self.asks and self.bids[0].price >= self.asks[0].price:
            bid = self.bids[0]
            ask = self.asks[0]

            trade_quantity = min(bid.quantity - bid.filled_quantity, ask.quantity - ask.filled_quantity)
            trade_price = ask.price  # Use ask price for trade execution

            # Create trade record
            trade = {
                'buy_order_id': bid.order_id,
                'sell_order_id': ask.order_id,
                'buyer_user_id': bid.user_id,
                'seller_user_id': ask.user_id,
                'price': trade_price,
                'quantity': trade_quantity,
                'asset': bid.asset
            }
            trades.append(trade)
            send_trade_to_balance_service(trade)  # Send trade to balance service
            logger.info(f"Trade created: {trade}")

            # Update filled quantities and statuses
            bid.filled_quantity += trade_quantity
            ask.filled_quantity += trade_quantity

            if bid.filled_quantity == bid.quantity:
                bid.status = 'filled'
                self.bids.popleft()  # Remove fully filled bid
            else:
                bid.status = 'partially filled'

            if ask.filled_quantity == ask.quantity:
                ask.status = 'filled'
                self.asks.popleft()  # Remove fully filled ask
            else:
                ask.status = 'partially filled'

            # Publish state changes
            publish_order_state(bid)
            publish_order_state(ask)

        # After matching, publish the order book
        self.publish_order_book()

        return trades

    def publish_order_book(self):
        """Publish the current order book snapshot to Redis."""
        order_book_snapshot = json.dumps(self.snapshot())
        redis_client_ob_ws.publish('order_book_channel', order_book_snapshot)
        logger.debug(f"Published order book snapshot to Redis: {order_book_snapshot}")

    def snapshot(self):
        """Generate a snapshot of the current order book for real-time updates."""
        snapshot_data = {
            "bids": [order.to_dict() for order in self.bids],
            "asks": [order.to_dict() for order in self.asks]
        }
        logger.debug(f"Order book snapshot: {snapshot_data}")
        return snapshot_data