from datetime import datetime, timezone
from email.policy import default
from functools import wraps

import jwt
from flask import current_app, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import validates

from utils import format_date

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)


class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    points = db.Column(db.Integer)


class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    desc = db.Column(db.Text, nullable=False)
    img = db.Column(ARRAY(db.String(500)))
    categories = db.Column(db.JSON)
    size = db.Column(ARRAY(db.String(50)))
    color = db.Column(ARRAY(db.String(50)))
    price = db.Column(db.Float, nullable=False)
    # Tương đương { timestamps: true }
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref='products')

    def __init__(self, **kwargs):
        super(Products, self).__init__(**kwargs)

    def to_dict(self):
        # Lấy thông tin cơ bản của sản phẩm
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # 2. ĐỊNH DẠNG LẠI NGÀY THÁNG
        data['created_at'] = format_date(self.created_at) if self.created_at else None
        data['updated_at'] = format_date(self.created_at) if self.created_at else None

        # Giả sử bạn có mối quan hệ (relationship) tên là 'author' trỏ đến bảng User
        if hasattr(self, 'author') and self.author:
            data['user_created'] = {
                "user_id": self.author.id,
                "username": self.author.username
            }
        return data

    @validates('price')
    def validate_price(self, key, value):
        if value is None or float(value) <= 0:
            raise ValueError('gia san pham phai lon hon 0')
        return value


class OrderProduct(db.Model):
    __tablename__ = 'order_products'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=1)


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


class CartProduct(db.Model):
    __tablename__ = 'cart_products'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.String(100), nullable=False)  # Tương đương productId
    quantity = db.Column(db.Integer, default=1)


class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    product_id = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity
        }


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
