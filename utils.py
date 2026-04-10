import os
import uuid
from functools import wraps

import jwt
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from requests import session


# Hàm xử lý chuỗi từ form-data sang mảng
def convert_to_list(data_string):
    if not data_string:
        return []
    return [item.strip() for item in data_string.split(',') if item.strip()]


# Hàm xử lý upload nhiều file và trả về danh sách link
def upload_multiple_files(files, upload_folder):
    image_links = []
    for file in files:
        if file and file.filename != '':
            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"

            save_path = os.path.join(upload_folder, unique_name)
            file.save(save_path)

            image_links.append(f"/static/uploads/{unique_name}")
    return image_links


from datetime import datetime


def format_date(dt):
    if not dt:
        return None
    # Định dạng: Ngày/Tháng/Năm Giờ:Phút (Ví dụ: 27/10/2023 15:30)
    return dt.strftime('%d/%m/%Y %H:%M')


def format_iso_date(dt):
    if not dt:
        return None
    # Định dạng chuẩn ISO 8601 cho Frontend dễ xử lý (Ví dụ: 2023-10-27T15:30:00)
    return dt.isoformat()


def delete_physical_files(image_links):
    """Xóa các file ảnh thực tế trên server dựa vào mảng link lưu trong DB"""
    if not image_links:
        return

    # Đảm bảo image_links luôn là list
    links = image_links if isinstance(image_links, list) else [image_links]

    for link in links:
        # Chuyển link "/static/uploads/abc.jpg" thành đường dẫn vật lý thực tế
        # Bỏ dấu "/" ở đầu để os.path.join hoạt động đúng
        file_path = os.path.join(os.getcwd(), link.lstrip('/'))

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Lỗi khi xóa file {file_path}: {e}")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        from models import User
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
