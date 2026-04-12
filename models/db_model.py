from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user_model import User
from .score_model import Score
from .cart_model import Cart
from .cart_product_model import CartProduct
from .products_model import Products
from .order_model import Order
from .order_product_model import OrderProduct
