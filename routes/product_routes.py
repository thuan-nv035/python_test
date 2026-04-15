import os

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from models import db, Products
from utils import convert_to_list, token_required, delete_physical_files, upload_multiple_files

# Khởi tạo Blueprint cho Product
product_bp = Blueprint('product_bp', __name__)


@product_bp.route('/create', methods=['POST'])
@token_required
def create_product(current_user):
    files = request.files.getlist('img')
    list_filenames = []

    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join('static/uploads', filename))
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
            user_id=current_user.id,
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


@product_bp.route('/', methods=['GET'])
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


@product_bp.route('/<int:id>', methods=['GET'])
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


@product_bp.route('/update/<int:id>', methods=['PUT', 'PATCH'])
@token_required
def update_product(current_user, id):
    product = Products.query.get_or_404(id)
    data = request.get_json() if request.is_json else request.form
    try:
        if 'title' in data: product.title = data.get('title')
        if 'desc' in data: product.desc = data.get('desc')
        if 'price' in data: product.price = data.get('price')
        if 'categories' in data: product.categories = data.get('categories')
        if 'size' in data: product.size = convert_to_list(data.get('size'))
        if 'color' in data: product.color = convert_to_list(data.get('color'))

        if 'img' in request.files:
            new_imgs = upload_multiple_files(request.files.getlist('img'), UPLOAD_FOLDER)
            if new_imgs:
                product.img = new_imgs

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


@product_bp.route('/delete/<int:id>', methods=['DELETE'])
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
