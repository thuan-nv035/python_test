from flask import Blueprint, render_template, request, jsonify

from models import Cart, db, CartProduct
from utils import token_required

cart_bp = Blueprint('cart_bp', __name__)


@cart_bp.route('/get-all', methods=['GET'])
@token_required
def get_all_cart(current_user):
    page = request.args.get('page', type=int)
    per_page = 20

    pagination = Cart.query.order_by(Cart.id.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    cart_list = []
    for c in pagination.items:
        cart_dict = c.to_dict()
        products_detail = []
        for item in c.products:
            p_info = item.to_dict()
            # Nếu item.product là relationship trỏ tới bảng Product
            if hasattr(item, 'product') and item.product:
                p_info['detail'] = item.product.to_dict()
            products_detail.append(p_info)

        cart_dict['products'] = products_detail
        cart_list.append(cart_dict)
    return jsonify({
        'cart': cart_list,
        'total_page': pagination.pages,
        'current_page': pagination.page,
        'total_items': pagination.total,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })


@cart_bp.route('/create', methods=['POST'])
@token_required
def create_cart(current_user):
    data = request.get_json()
    user_id = current_user.id
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

    if item:
        item.quantity += quantity
    else:
        item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    return jsonify({'da them vao gio hang'}), 201
