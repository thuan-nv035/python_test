from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import validates

from utils import format_date

db = SQLAlchemy()


class Products(db.Model):
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
