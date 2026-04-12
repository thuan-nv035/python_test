# Khởi tạo Blueprint cho Product
import datetime
import os

import jwt
from flask import Blueprint, request, current_app, jsonify, render_template, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models.db_model import db
from models.user_model import User
from oauth_config import google
from utils import token_required

user_bp = Blueprint('user_bp', __name__)

server_url = os.getenv('SERVER_URL')


@user_bp.route('/dangky', methods=['GET', 'POST'])
def dang_ky():
    if request.method == 'POST':
        try:

            hashed_password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')
            file = request.files.get('avatar')
            fileName = None
            if file:
                fileName = f"{server_url}/static/uploads/{file.filename}"
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


@user_bp.route('/list')
def xem_danh_sach():
    # Lấy tất cả người dùng từ Database
    tat_ca = User.query.all()
    kq = ""
    for u in tat_ca:
        kq += f"ID: {u.id} - User: {u.username}<br>"
    return kq if kq else "Chưa có ai!"


@user_bp.route('/dangnhap', methods=['GET', 'POST'])
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
                'exp': datetime.datetime.now() + datetime.timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({
                'message': 'dang nhap thanh cong',
                'token': token
            }), 200

        else:
            return jsonify({"error": "Sai ten hoac mat khau"}), 401

    return render_template('dangnhap.html')


@user_bp.route('/login/google')
def login_google():
    redirect_uri = url_for('main.auth_callback', _external=True)
    print('redirect', redirect_uri)
    return google.authorize_redirect(redirect_uri)


@user_bp.route('/auth/callback')
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


@user_bp.route('/info', methods=['GET'])
@token_required
def get_user_info(current_user):
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'status': 'hihi'
    })
