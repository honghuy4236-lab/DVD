import os
from datetime import timedelta

from flask import Flask, render_template
from config import Config, DEFAULT_SECRET_KEY, DEFAULT_ADMIN_PASSWORD
from extensions import db
from models import ORDER_STATUS_CSS_CLASS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Trên host thật (HTTPS_ONLY=1) bắt buộc đã đổi khoá bí mật + mật khẩu admin, nếu không thì dừng luôn.
    if os.environ.get('HTTPS_ONLY') == '1' and (
        app.config['SECRET_KEY'] == DEFAULT_SECRET_KEY
        or app.config['ADMIN_PASSWORD'] == DEFAULT_ADMIN_PASSWORD
    ):
        raise RuntimeError('Chưa đặt SECRET_KEY / ADMIN_PASSWORD bằng biến môi trường (xem file WSGI).')

    db.init_app(app)

    # Bộ lọc dùng trong template: {{ order.status|status_class }} -> "pending"/"paid"/...
    app.jinja_env.filters['status_class'] = lambda s: ORDER_STATUS_CSS_CLASS.get(s, '')

    # created_at lưu giờ UTC; bộ lọc này đổi sang giờ Việt Nam (UTC+7, không có giờ mùa hè):
    # {{ order.created_at|vn_time }}
    def vn_time(dt, fmt='%d/%m/%Y %H:%M'):
        return (dt + timedelta(hours=7)).strftime(fmt) if dt else ''
    app.jinja_env.filters['vn_time'] = vn_time

    # Đăng ký các Blueprint (nhóm route theo chức năng)
    from routes.main import main_bp
    from routes.artist import artist_bp
    from routes.product import product_bp
    from routes.cart import cart_bp
    from routes.order import order_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(artist_bp, url_prefix='/nghe-si')
    app.register_blueprint(product_bp, url_prefix='/san-pham')
    app.register_blueprint(cart_bp, url_prefix='/gio-hang')
    app.register_blueprint(order_bp, url_prefix='/don-hang')
    app.register_blueprint(admin_bp, url_prefix='/quan-tri')

    # Biến dùng chung cho mọi template: link Zalo dựng từ số điện thoại trong config.py
    @app.context_processor
    def inject_zalo_link():
        phone = app.config.get('ZALO_PHONE', '').strip()
        return {'zalo_link': f'https://zalo.me/{phone}' if phone else ''}

    # Tạo bảng CSDL nếu chưa tồn tại (đủ dùng cho đồ án; dự án thật nên dùng Flask-Migrate)
    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
