from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


db = SQLAlchemy()

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    asset = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    filled_quantity = db.Column(db.Float, default=0.0)  # Track partially filled quantity
    price = db.Column(db.Float, nullable=False)
    order_type = db.Column(db.String(10), nullable=False)  # e.g., 'buy' or 'sell'
    status = db.Column(db.String(20), nullable=False, default='pending')  # e.g., 'pending', 'partially filled', 'filled'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz=timezone.utc))  # Updated to timezone-aware UTC
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'asset': self.asset,
            'quantity': self.quantity,
            'filled_quantity': self.filled_quantity,
            'price': self.price,
            'order_type': self.order_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
