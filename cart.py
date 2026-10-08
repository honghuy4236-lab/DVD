from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from models import Product

cart_bp = Blueprint('cart', __name__)


def _get_cart():
    """
    Giỏ hàng được lưu tạm trong session dưới dạng dict:
        {"<product_id>": số_lượng, ...}
    Cách này không cần đăng nhập, phù hợp với phạm vi đồ án học phần.
    """
    return session.setdefault('cart', {})


@cart_bp.route('/')
def view_cart():
    cart = _get_cart()
    items = []
    total = 0
    for product_id, qty in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = float(product.price) * qty
            total += subtotal
            items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
    return render_template('cart.html', items=items, total=total)


@cart_bp.route('/them/<int:product_id>', methods=['POST'])
def add(product_id):
    product = Product.query.get_or_404(product_id)
    cart = _get_cart()
    key = str(product_id)

    try:
        qty = max(1, int(request.form.get('quantity', 1)))
    except ValueError:
        qty = 1

    cart[key] = cart.get(key, 0) + qty
    session.modified = True  # bắt buộc phải gọi vì sửa dict lồng trong session

    total_count = sum(cart.values())

    # Trả về JSON cho Fetch API / AJAX không load lại trang
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': f'Đã thêm "{product.title}" vào giỏ hàng!',
            'cart_count': total_count
        })

    # Nếu truy cập dạng form bình thường thì vẫn redirect như cũ
    flash(f'Đã thêm "{product.title}" vào giỏ hàng.', 'success')
    return redirect(request.referrer or url_for('main.index'))


@cart_bp.route('/xoa/<int:product_id>', methods=['POST'])
def remove(product_id):
    cart = _get_cart()
    cart.pop(str(product_id), None)
    session.modified = True
    flash('Đã xoá sản phẩm khỏi giỏ hàng.', 'info')
    return redirect(url_for('cart.view_cart'))