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

    data_product = data.pop('products', [])

    new_cart = Cart(**data)
    try:
        for item in data_product:
            child = CartProduct(**item)
            new_cart.products.append(child)
        db.session.add(new_cart)
        db.session.commit()

        return jsonify(new_cart.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)})
