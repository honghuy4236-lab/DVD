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

    # Không cho thêm vượt quá số lượng tồn kho
    in_cart = cart.get(key, 0)
    can_add = min(qty, max(0, product.stock - in_cart))

    if can_add > 0:
        cart[key] = in_cart + can_add
        session.modified = True  # bắt buộc phải gọi vì sửa dict lồng trong session

    if can_add == 0:
        ok = False
        message = (f'"{product.title}" đã hết hàng.' if product.stock <= 0
                   else f'Giỏ hàng đã có đủ số lượng còn lại ({product.stock}) của "{product.title}".')
    elif can_add < qty:
        ok = True
        message = f'Chỉ còn {product.stock} sản phẩm "{product.title}", đã thêm {can_add} vào giỏ.'
    else:
        ok = True
        message = f'Đã thêm "{product.title}" vào giỏ hàng!'

    total_count = sum(cart.values())

    # Trả về JSON cho Fetch API / AJAX không load lại trang
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': ok, 'message': message, 'cart_count': total_count})

    # Nếu truy cập dạng form bình thường thì vẫn redirect như cũ
    flash(message, 'success' if ok else 'warning')
    return redirect(request.referrer or url_for('main.index'))


@cart_bp.route('/xoa/<int:product_id>', methods=['POST'])
def remove(product_id):
    cart = _get_cart()
    cart.pop(str(product_id), None)
    session.modified = True
    flash('Đã xoá sản phẩm khỏi giỏ hàng.', 'info')
    return redirect(url_for('cart.view_cart'))