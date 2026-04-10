# Khởi tạo Blueprint cho Product
import datetime
import os

import jwt
from flask import Blueprint, request, current_app, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models import User, db
from routes.routes import SERVER_URL

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/dangky', methods=['GET', 'POST'])
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
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({
                'message': 'dang nhap thanh cong',
                'token': token
            }), 200

        else:
            return jsonify({"error": "Sai ten hoac mat khau"}), 401

    return render_template('dangnhap.html')
