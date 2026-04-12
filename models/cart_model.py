from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)  # Tương đương String, required: true

    # Quan hệ 1-nhiều với bảng Product (vì SQL không lưu mảng trực tiếp như MongoDB)
    products = db.relationship('CartProduct', backref='cart', lazy=True)

    # Tương đương {timestamps: true}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
