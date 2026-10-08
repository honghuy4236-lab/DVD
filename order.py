import uuid
from urllib.parse import quote

from flask import (
    Blueprint, render_template, session, redirect,
    url_for, request, flash, current_app
)
from extensions import db
from models import Product, Order, OrderItem

order_bp = Blueprint('order', __name__)


def _generate_order_code():
    """Sinh mã đơn hàng ngắn, dễ đọc, VD: DH3F9A21C0"""
    return 'DH' + uuid.uuid4().hex[:8].upper()


def _build_vietqr_url(order):
    """
    Trả về link ảnh mã QR VietQR (chuẩn chuyển khoản ngân hàng qua NAPAS 247) —
    quét được thẳng bằng app ngân hàng/ví điện tử, tự điền sẵn số tiền + nội dung.
    Dùng dịch vụ ảnh miễn phí của VietQR.io, không cần API key:
        https://img.vietqr.io/image/<BANK_ID>-<SO_TK>-<TEMPLATE>.png?amount=...&addInfo=...&accountName=...

    Thông tin ngân hàng lấy từ config.py (BANK_ID, BANK_ACCOUNT_NO, BANK_ACCOUNT_NAME) —
    đổi thành tài khoản thật của bạn nếu muốn quét thanh toán thật.
    """
    bank_id = current_app.config['BANK_ID']
    account_no = current_app.config['BANK_ACCOUNT_NO']
    account_name = current_app.config['BANK_ACCOUNT_NAME']
    template = current_app.config['VIETQR_TEMPLATE']

    amount = int(order.total_amount)
    add_info = quote(f'Thanh toan don {order.order_code}')
    account_name_q = quote(account_name)

    return (
        f'https://img.vietqr.io/image/{bank_id}-{account_no}-{template}.png'
        f'?amount={amount}&addInfo={add_info}&accountName={account_name_q}'
    )


@order_bp.route('/thanh-toan', methods=['GET', 'POST'])
def checkout():
    """Trang nhập thông tin giao hàng và xác nhận đặt hàng từ giỏ hàng hiện tại."""
    cart = session.get('cart', {})
    if not cart:
        flash('Giỏ hàng đang trống, hãy chọn sản phẩm trước khi thanh toán.', 'warning')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        order = Order(
            order_code=_generate_order_code(),
            customer_name=request.form['customer_name'].strip(),
            customer_email=request.form['customer_email'].strip(),
            customer_phone=request.form.get('customer_phone', '').strip(),
            shipping_address=request.form['shipping_address'].strip(),
        )
        db.session.add(order)
        db.session.flush()  # để có order.id trước khi commit, dùng cho OrderItem

        total = 0
        for product_id, qty in cart.items():
            product = Product.query.get(int(product_id))
            if not product:
                continue
            db.session.add(OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                unit_price=product.price,
            ))
            total += float(product.price) * qty

        order.total_amount = total
        order.qr_code_image = _build_vietqr_url(order)

        db.session.commit()

        session['cart'] = {}   # xoá giỏ hàng sau khi đặt thành công
        return redirect(url_for('order.success', order_code=order.order_code))

    # GET: hiển thị lại tóm tắt giỏ hàng để khách xác nhận
    items = []
    total = 0
    for product_id, qty in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = float(product.price) * qty
            total += subtotal
            items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})

    return render_template('checkout.html', items=items, total=total)


@order_bp.route('/thanh-cong/<order_code>')
def success(order_code):
    """Trang xác nhận đặt hàng thành công, hiển thị mã QR thanh toán."""
    order = Order.query.filter_by(order_code=order_code).first_or_404()
    return render_template('order_success.html', order=order)
