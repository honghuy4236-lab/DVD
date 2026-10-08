import os
from functools import wraps
from werkzeug.utils import secure_filename

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, session
)
from extensions import db
from models import (
    Artist, Product, Track, Order,
    CATEGORY_CHOICES, ORDER_STATUS_CHOICES
)

admin_bp = Blueprint('admin', __name__)

ALLOWED_IMAGE_EXT = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
ALLOWED_AUDIO_EXT = {'mp3', 'wav', 'ogg', 'm4a'}


# ------------------------------------------------------------------
# Đăng nhập / bảo vệ khu vực quản trị
# ------------------------------------------------------------------
def admin_required(view):
    """Decorator: chặn truy cập nếu chưa đăng nhập quản trị, đưa về trang login."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin.login', next=request.path))
        return view(*args, **kwargs)
    return wrapped


@admin_bp.route('/dang-nhap', methods=['GET', 'POST'])
def login():
    if session.get('is_admin'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if (username == current_app.config['ADMIN_USERNAME']
                and password == current_app.config['ADMIN_PASSWORD']):
            session['is_admin'] = True
            flash('Đăng nhập thành công.', 'success')
            return redirect(request.args.get('next') or url_for('admin.dashboard'))
        flash('Sai tên đăng nhập hoặc mật khẩu.', 'warning')

    return render_template('admin/login.html')


@admin_bp.route('/dang-xuat')
def logout():
    session.pop('is_admin', None)
    flash('Đã đăng xuất khỏi khu vực quản trị.', 'info')
    return redirect(url_for('admin.login'))


# ------------------------------------------------------------------
# Tiện ích upload file dùng chung
# ------------------------------------------------------------------
def _extension_ok(filename, allowed_ext):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext


def _save_upload(file_storage, subfolder, allowed_ext):
    """
    Lưu 1 file upload vào static/uploads/<subfolder>/.
    Trả về (đường_dẫn_tương_đối, thông_báo_lỗi). Một trong hai luôn là None.
    """
    if not file_storage or file_storage.filename == '':
        return None, None

    if not _extension_ok(file_storage.filename, allowed_ext):
        return None, f'File "{file_storage.filename}" sai định dạng. Cho phép: {", ".join(sorted(allowed_ext))}'

    filename = secure_filename(file_storage.filename)
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder, exist_ok=True)

    base, ext = os.path.splitext(filename)
    final_name = filename
    counter = 1
    while os.path.exists(os.path.join(folder, final_name)):
        final_name = f'{base}_{counter}{ext}'
        counter += 1

    file_storage.save(os.path.join(folder, final_name))
    return f'uploads/{subfolder}/{final_name}', None


# ------------------------------------------------------------------
# Tổng quan (dashboard)
# ------------------------------------------------------------------
@admin_bp.route('/')
@admin_required
def dashboard():
    revenue = (
        db.session.query(db.func.coalesce(db.func.sum(Order.total_amount), 0))
        .filter(Order.status != 'Đã hủy')
        .scalar()
    )
    stats = {
        'artist_count': Artist.query.count(),
        'product_count': Product.query.count(),
        'order_count': Order.query.count(),
        'revenue': revenue or 0,
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)


# ------------------------------------------------------------------
# Quản lý Nghệ sĩ
# ------------------------------------------------------------------
@admin_bp.route('/nghe-si')
@admin_required
def list_artists():
    artists = Artist.query.order_by(Artist.name).all()
    return render_template('admin/artists.html', artists=artists)


def _artist_form(artist=None):
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Vui lòng nhập tên nghệ sĩ.', 'warning')
            return render_template('admin/artist_form.html', artist=artist)

        avatar_path, err = _save_upload(request.files.get('avatar'), 'avatars', ALLOWED_IMAGE_EXT)
        if err:
            flash(err, 'warning')
            return render_template('admin/artist_form.html', artist=artist)

        if artist is None:
            artist = Artist(name=name)
            db.session.add(artist)

        artist.name = name
        artist.bio = request.form.get('bio', '').strip()
        if avatar_path:
            artist.avatar = avatar_path

        db.session.commit()
        flash(f'Đã lưu nghệ sĩ "{artist.name}".', 'success')
        return redirect(url_for('admin.list_artists'))

    return render_template('admin/artist_form.html', artist=artist)


@admin_bp.route('/nghe-si/them', methods=['GET', 'POST'])
@admin_required
def add_artist():
    return _artist_form(None)


@admin_bp.route('/nghe-si/<int:artist_id>/sua', methods=['GET', 'POST'])
@admin_required
def edit_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    return _artist_form(artist)


@admin_bp.route('/nghe-si/<int:artist_id>/xoa', methods=['POST'])
@admin_required
def delete_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    name = artist.name
    db.session.delete(artist)  # cascade: xoá luôn sản phẩm + track của nghệ sĩ này
    db.session.commit()
    flash(f'Đã xoá nghệ sĩ "{name}" (và toàn bộ sản phẩm của họ).', 'info')
    return redirect(url_for('admin.list_artists'))


# ------------------------------------------------------------------
# Quản lý Sản phẩm (kèm ảnh bìa, nhạc nghe thử, tracklist)
# ------------------------------------------------------------------
@admin_bp.route('/san-pham')
@admin_required
def list_products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)


def _tracks_to_text(product):
    if not product:
        return ''
    return '\n'.join(f'{t.song_name} | {t.duration or ""}' for t in product.tracks)


def _product_form(product=None):
    artists = Artist.query.order_by(Artist.name).all()

    if request.method == 'POST':
        errors = []

        # ---- Xác định nghệ sĩ ----
        artist_id = request.form.get('artist_id', '')
        new_artist_name = request.form.get('new_artist_name', '').strip()
        artist = None

        if new_artist_name:
            avatar_path, err = _save_upload(
                request.files.get('new_artist_avatar'), 'avatars', ALLOWED_IMAGE_EXT
            )
            if err:
                errors.append(err)
            artist = Artist(
                name=new_artist_name,
                bio=request.form.get('new_artist_bio', '').strip(),
                avatar=avatar_path,
            )
            db.session.add(artist)
            db.session.flush()
        elif artist_id:
            artist = Artist.query.get(int(artist_id))
        elif product:
            artist = product.artist
        else:
            errors.append('Vui lòng chọn nghệ sĩ có sẵn hoặc nhập tên nghệ sĩ mới.')

        title = request.form.get('title', '').strip()
        if not title:
            errors.append('Vui lòng nhập tên album/sản phẩm.')

        cover_path, err_cover = _save_upload(
            request.files.get('cover_image'), 'covers', ALLOWED_IMAGE_EXT
        )
        if err_cover:
            errors.append(err_cover)

        audio_path, err_audio = _save_upload(
            request.files.get('demo_audio_file'), 'audio', ALLOWED_AUDIO_EXT
        )
        if err_audio:
            errors.append(err_audio)

        if errors:
            for e in errors:
                flash(e, 'warning')
            return render_template(
                'admin/product_form.html', artists=artists, categories=CATEGORY_CHOICES,
                product=product, form=request.form, tracks_text=request.form.get('tracks', '')
            )

        if product is None:
            product = Product(artist_id=artist.id)
            db.session.add(product)
        else:
            product.artist_id = artist.id

        product.title = title
        product.category = request.form.get('category', CATEGORY_CHOICES[0])
        product.price = float(request.form.get('price') or 0)
        product.stock = int(request.form.get('stock') or 0)
        product.description = request.form.get('description', '').strip()
        if cover_path:
            product.cover_image = cover_path
        if audio_path:
            product.demo_audio_file = audio_path

        db.session.flush()

        # ---- Ghi lại tracklist: xoá cũ, thêm lại theo nội dung mới nhập ----
        Track.query.filter_by(product_id=product.id).delete()
        raw_tracks = request.form.get('tracks', '')
        lines = [l.strip() for l in raw_tracks.splitlines() if l.strip()]
        for i, line in enumerate(lines, start=1):
            if '|' in line:
                song_name, duration = (p.strip() for p in line.split('|', 1))
            else:
                song_name, duration = line, ''
            db.session.add(Track(
                product_id=product.id, track_number=i,
                song_name=song_name, duration=duration
            ))

        db.session.commit()
        flash(f'Đã lưu sản phẩm "{product.title}".', 'success')
        return redirect(url_for('admin.list_products'))

    return render_template(
        'admin/product_form.html', artists=artists, categories=CATEGORY_CHOICES,
        product=product, form={}, tracks_text=_tracks_to_text(product)
    )


@admin_bp.route('/san-pham/them', methods=['GET', 'POST'])
@admin_required
def add_product():
    return _product_form(None)


@admin_bp.route('/san-pham/<int:product_id>/sua', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    return _product_form(product)


@admin_bp.route('/san-pham/<int:product_id>/xoa', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    title = product.title
    db.session.delete(product)
    db.session.commit()
    flash(f'Đã xoá sản phẩm "{title}".', 'info')
    return redirect(url_for('admin.list_products'))


# ------------------------------------------------------------------
# Quản lý Đơn hàng
# ------------------------------------------------------------------
@admin_bp.route('/don-hang')
@admin_required
def list_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)


@admin_bp.route('/don-hang/<int:order_id>', methods=['GET', 'POST'])
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        new_status = request.form.get('status')
        if new_status in ORDER_STATUS_CHOICES:
            order.status = new_status
            db.session.commit()
            flash(f'Đã cập nhật trạng thái đơn {order.order_code}.', 'success')
        return redirect(url_for('admin.order_detail', order_id=order.id))

    return render_template('admin/order_detail.html', order=order, statuses=ORDER_STATUS_CHOICES)
