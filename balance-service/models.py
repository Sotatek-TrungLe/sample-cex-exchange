from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Balance(db.Model):
    __tablename__ = 'balances'

    user_id = db.Column(db.Integer, primary_key=True)
    asset = db.Column(db.String(10), primary_key=True)
    amount = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'asset': self.asset,
            'amount': self.amount
        }
