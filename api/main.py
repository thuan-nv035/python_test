from flask import Flask
from models.user_model import db
from models.user_model import User
from models.products_model import Products
from routes.product_routes import product_bp
from routes.user_routes import user_bp
from routes.game_routes import game_bp
from oauth_config import oauth
import os

app = Flask(__name__)

# app.register_blueprint(main_routes)
app.register_blueprint(product_bp, url_prefix='/api/products')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(game_bp, url_prefix='/api/game')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:10052000@localhost:5432/test1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = os.getenv('SECRET_KEY')
oauth.init_app(app)
# Đăng ký các Route từ file routes.py
# Cấu hình
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Kết nối db với app
db.init_app(app)

print("Client ID:", os.getenv('GOOGLE_CLIENT_ID'))

# Đường dẫn đến thư mục 'uploads'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Tạo thư mục nếu chưa có
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Tạo database (nếu chưa có)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app = app
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
