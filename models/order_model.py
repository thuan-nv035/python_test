from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)

    # Quan hệ 1-nhiều với bảng OrderProduct
    products = db.relationship('OrderProduct', backref='order', lazy=True)

    amount = db.Column(db.Float, nullable=False)

    # Lưu địa chỉ dạng JSON (phù hợp với {type: Object} trong Mongoose)
    address = db.Column(db.JSON, nullable=False)

    status = db.Column(db.String(50), default='pending')

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
