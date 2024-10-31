import json
import redis
from logger import logger
from trade_service import send_trade_to_balance_service
from publish_order_state import publish_order_state
from config import Config
from linked_list import SortedDoublyLinkedList  # Import linked list classes

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
        self.bids = SortedDoublyLinkedList(descending=True)  # Buy orders sorted in descending order
        self.asks = SortedDoublyLinkedList(descending=False)  # Sell orders sorted in ascending order

    def add_order(self, order):
        """Add an order to the order book and merge if price level exists."""
        logger.debug(f"Adding order: {order.to_dict()}")

        # Insert or merge order in bids or asks
        if order.order_type == 'buy':
            self.bids.insert_or_merge(order.price, order.quantity)
        elif order.order_type == 'sell':
            self.asks.insert_or_merge(order.price, order.quantity)

        # Publish the updated order book after adding the order
        self.publish_order_book()

    def match_orders(self):
        """Match orders in the order book and notify clients of changes."""
        trades = []

        # Traverse bids and asks to match highest bid with lowest ask
        while self.bids.head and self.asks.head and self.bids.head.price >= self.asks.head.price:
            bid = self.bids.head
            ask = self.asks.head

            trade_quantity = min(bid.quantity, ask.quantity)
            trade_price = ask.price  # Use ask price for trade execution

            # Create trade record
            trade = {
                'price': trade_price,
                'quantity': trade_quantity,
                'asset': ask.order_type  # Placeholder
            }
            trades.append(trade)
            send_trade_to_balance_service(trade)  # Send trade to balance service
            logger.info(f"Trade created: {trade}")

            # Update quantities or remove fully filled orders
            bid.quantity -= trade_quantity
            ask.quantity -= trade_quantity
            if bid.quantity == 0:
                self.bids.remove_node(bid)
            if ask.quantity == 0:
                self.asks.remove_node(ask)

            # Publish state changes
            publish_order_state(bid)
            publish_order_state(ask)

        # Publish the order book after matching
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
            "bids": self.bids.to_list(),
            "asks": self.asks.to_list()
        }
        logger.debug(f"Order book snapshot: {snapshot_data}")
        return snapshot_data
