import os.path
from functools import wraps
from hashlib import algorithms_available
from tkinter.messagebox import RETRY
from utils import convert_to_list, upload_multiple_files, delete_physical_files
from config import UPLOAD_FOLDER
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, current_app
from requests import session
from sqlalchemy.sql.coercions import expect
from werkzeug.debug import console
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from oauth_config import google
from models import db, User, Score, Products
import jwt
import datetime

SERVER_URL = os.getenv('SERVER_URL')
# Tạo một Blueprint
main_routes = Blueprint('main', __name__)


@main_routes.route('/')
def home():
    return 'trang chus'


@main_routes.route('/dangky', methods=['GET', 'POST'])
def dang_ky():
    if request.method == 'POST':
        try:

            hashed_password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')
            file = request.files.get('avatar')
            fileName = None
            if file:
                fileName = f"{SERVER_URL}/static/uploads/{file.filename}"
                name = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], name))
            newUser = User(
                username=request.form.get('username'),
                password=hashed_password,
                avatar=fileName
            )

            db.session.add(newUser)
            db.session.commit()

            return jsonify({
                'id': newUser.id,
                'username': newUser.username,
                'avatar': newUser.avatar,
                "message": "User created successfully"
            }), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        return render_template('dangky.html')


@main_routes.route('/list')
def xem_danh_sach():
    # Lấy tất cả người dùng từ Database
    tat_ca = User.query.all()
    kq = ""
    for u in tat_ca:
        kq += f"ID: {u.id} - User: {u.username}<br>"
    return kq if kq else "Chưa có ai!"


@main_routes.route('/dangnhap', methods=['GET', 'POST'])
def dang_nhap():
    if request.method == 'POST':
        data = request.get_json(force=True)
        user_name = data.get('username')
        pass_word = data.get('password')

        user = User.query.filter_by(username=user_name).first()
        print('user', User)
        if user and check_password_hash(user.password, pass_word):
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({
                'message': 'dang nhap thanh cong',
                'token': token
            }), 200

        else:
            return jsonify({"error": "Sai ten hoac mat khau"}), 401

    return render_template('dangnhap.html')


@main_routes.route('/game')
def game():
    return render_template('snake.html')


@main_routes.route('/save-score', methods=['POST'])
def save_score():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400

    new_score = Score(username="Người chơi", points=data['score'])
    db.session.add(new_score)
    db.session.commit()
    return jsonify({"status": "success"})


@main_routes.route('/get-score')
def get_score():
    top_score = Score.query.order_by(Score.points.desc()).first()
    if top_score:
        return jsonify({"username": top_score.username, "points": top_score.points})
    return jsonify({"points": 0})  # Sửa lỗi trả về None bạn gặp lúc nãy


@main_routes.route('/login/google')
def login_google():
    redirect_uri = url_for('main.auth_callback', _external=True)
    print('redirect', redirect_uri)
    return google.authorize_redirect(redirect_uri)


@main_routes.route('/auth/callback')
def auth_callback():
    try:
        # Thêm timeout và kiểm tra token
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        session['user'] = user_info
        return f"Chào {user_info['name']}!"
    except Exception as e:
        # Nếu lỗi JSON, in ra nội dung phản hồi để xem lỗi từ Google
        print(f"Lỗi xảy ra: {str(e)}")
        return "Lỗi xác thực. Hãy kiểm tra Console trong PyCharm để biết chi tiết."


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer'):
                token = auth_header.split(" ")[1]
        if not token:
            return jsonify({'message': 'thieu token ban e'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except Exception as e:
            return jsonify({'message': 'token het han'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@main_routes.route('/thong-tin-ca-nhan', methods=['GET'])
@token_required
def get_user_info(current_user):
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'status': 'hihi'
    })


@main_routes.route('/product/create', methods=['POST'])
@token_required
def create_product(current_user):
    files = request.files.getlist('img')
    list_filenames = []

    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join('../static/uploads', filename))
            list_filenames.append(filename)

    try:
        new_product = Products(
            img=list_filenames,
            title=request.form.get('title'),
            desc=request.form.get('desc'),
            size=convert_to_list('size'),
            color=convert_to_list('color'),
            price=request.form.get('price'),
            categories=request.form.get('categories'),
            user_id=current_user.id
        )  # Kết thúc bằng dấu )
        db.session.add(new_product)
        db.session.commit()

        product_data = new_product.to_dict()
        product_data['user_created'] = {
            'user_id': current_user.id,
            'username': current_user.username
        }
        return jsonify(product_data), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Lỗi hệ thống {str(e)}"}), 500


@main_routes.route('/product', methods=['GET'])
def get_product():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    pagination = Products.query.order_by(Products.id.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # 2. Chuyển danh sách đối tượng thành danh sách Dictionary
    products_list = [p.to_dict() for p in pagination.items]

    # 3. Trả về JSON
    return jsonify({
        'product': products_list,
        'total_page': pagination.pages,
        'current_page': pagination.page,
        'total_items': pagination.total,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })


@main_routes.route('/product/<int:id>', methods=['GET'])
def get_product_by_id(id):
    product = Products.query.get_or_404(id)
    product_data = product.to_dict()

    if 'user_created' not in product_data:
        from models import User
        user = User.query.get(product.user_id)
        if user:
            product_data['user_created'] = {
                'user_id': user.id,
                'username': user.username
            }
    return jsonify(product_data), 200


@main_routes.route('/product/update/<int:id>', methods=['PUT', 'PATCH'])
@token_required
def update_product(current_user, id):
    product = Products.query.get_or_404(id)
    data = request.get_json() if request.is_json else request.form
    try:
        # 3. Cập nhật từng trường nếu có dữ liệu mới gửi lên
        if 'title' in data: product.title = data.get('title')
        if 'desc' in data: product.desc = data.get('desc')
        if 'price' in data: product.price = data.get('price')
        if 'categories' in data: product.categories = data.get('categories')
        if 'size' in data: product.size = convert_to_list(data.get('size'))
        if 'color' in data: product.color = convert_to_list(data.get('color'))

        # Xử lý nếu có upload ảnh mới
        if 'img' in request.files:
            new_imgs = upload_multiple_files(request.files.getlist('img'), UPLOAD_FOLDER)
            if new_imgs:
                product.img = new_imgs

        # 4. Lưu vào Database
        db.session.commit()
        product_data = product.to_dict()
        product_data['user_created'] = {
            'user_id': current_user.id,
            'username': current_user.username
        }
        return jsonify({
            "message": "Cập nhật thành công",
            "product": product_data
        }), 200

    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Lỗi hệ thống: {str(e)}"}), 500


@main_routes.route('/product/delete/<int:id>', methods=['DELETE'])
@token_required
def delete_product(current_user, id):
    product = Products.query.get_or_404(id)

    try:
        delete_physical_files(product.img)
        db.session.delete(product)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'sản phẩm id {id} đã được xóa'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Không thể xóa sản phẩm: {str(e)}"}), 500
