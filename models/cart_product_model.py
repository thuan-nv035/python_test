from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class CartProduct(db.Model):
    __tablename__ = 'cart_products'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.String(100), nullable=False)  # Tương đương productId
    quantity = db.Column(db.Integer, default=1)
