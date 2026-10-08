from flask import Blueprint, render_template, request
from models import Product, Artist, CATEGORY_CHOICES

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Trang chủ: hiển thị sản phẩm mới nhất + cho phép tìm theo tên/từ khoá + lọc theo danh mục."""
    keyword = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()

    query = Product.query
    if keyword:
        query = query.filter(Product.title.ilike(f'%{keyword}%'))
    if category:
        query = query.filter(Product.category == category)

    products = query.order_by(Product.created_at.desc()).all()
    artists = Artist.query.order_by(Artist.name).limit(10).all()

    return render_template(
        'index.html',
        products=products,
        artists=artists,
        keyword=keyword,
        selected_category=category,
        categories=CATEGORY_CHOICES,
    )
