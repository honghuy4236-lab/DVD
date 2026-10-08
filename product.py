from flask import Blueprint, render_template
from models import Product

product_bp = Blueprint('product', __name__)


@product_bp.route('/<int:product_id>')
def detail(product_id):
    """Trang chi tiết sản phẩm: mô tả, danh sách track, nghe thử, thêm vào giỏ hàng."""
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)
