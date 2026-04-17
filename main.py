from flask import Flask
from flask_socketio import SocketIO, emit, join_room
from celery import Celery
from models import db, Message, Seat
from routes.book_routes import book_bp
from routes.product_routes import product_bp
from routes.user_routes import user_bp
from routes.game_routes import game_bp
from routes.cart_routes import cart_bp
from routes.home_routes import home_bp
from oauth_config import oauth
import os

app = Flask(__name__)

# app.register_blueprint(main_routes)
app.register_blueprint(product_bp, url_prefix='/api/products')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(game_bp, url_prefix='/api/game')
app.register_blueprint(cart_bp, url_prefix='/api/cart')
app.register_blueprint(home_bp, url_prefix='/')
app.register_blueprint(book_bp, url_prefix='/api')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:10052000@localhost:5432/test1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.secret_key = os.getenv('SECRET_KEY')
socketio = SocketIO(app, cors_allowed_origins="*")
oauth.init_app(app)
# Sử dụng SQLite để thực hành
# Đăng ký các Route từ file routes.py
# Cấu hình
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Kết nối db với app
db.init_app(app)
# Đường dẫn đến thư mục 'uploads'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Tạo thư mục nếu chưa có
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# Tạo database (nếu chưa có)

celery = Celery(
    app.name,
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)


@celery.task
def release_seat_task(seat_id):
    with app.app_context():
        seat = Seat.query.get(seat_id)
        if seat and seat.status == 'reserved':
            seat.status = 'available'
            seat.user_id = None
            db.session.commit()
            print(f'----Celery: da giai phong ghe {seat_id}')


with app.app_context():
    db.create_all()
    if not Seat.query.first():
        seats = [Seat(seat_code=f'A{i}') for i in range(1, 6)]
        db.session.add_all(seats)
        db.session.commit()


@socketio.on('connect')
def handle_connect():
    print("Một người dùng đã kết nối!")


# API Chat: Lắng nghe tin nhắn từ client
@socketio.on('send_message')
def handle_message(data):
    # Tạo object tin nhắn mới và lưu vào DB
    new_msg = Message(sender_id=data['user_id'], content=data['message'])
    db.session.add(new_msg)
    db.session.commit()

    emit('receive_message', data, broadcast=True)


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('receive_message', {'user': 'System', 'message': f'{username} đã vào phòng.'}, room=room)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, debug=True, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
