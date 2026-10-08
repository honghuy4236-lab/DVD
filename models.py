from datetime import datetime
from extensions import db

# ------------------------------------------------------------------
# Danh sách lựa chọn (thay cho Enum để đơn giản hoá cho đồ án học phần,
# dễ hiển thị trong template và dễ debug hơn so với Enum của SQLAlchemy).
# ------------------------------------------------------------------
CATEGORY_CHOICES = [
    'Đĩa Vinyl',
    'CD',
    'Cassette',
    'USB Album',
    'Áo thun',
    'Photobook',
]

ORDER_STATUS_CHOICES = [
    'Chờ thanh toán',
    'Đã thanh toán',
    'Đang giao hàng',
    'Hoàn thành',
    'Đã hủy',
]

# Dùng để tô màu badge trạng thái trong trang quản trị (xem app.py, bộ lọc status_class)
ORDER_STATUS_CSS_CLASS = {
    'Chờ thanh toán': 'pending',
    'Đã thanh toán': 'paid',
    'Đang giao hàng': 'shipping',
    'Hoàn thành': 'completed',
    'Đã hủy': 'cancelled',
}


class Artist(db.Model):
    """Nghệ sĩ / Ca sĩ (VD: MCK, tlinh, obito, ...)"""
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    bio = db.Column(db.Text)                     # tiểu sử ngắn
    avatar = db.Column(db.String(255))            # đường dẫn ảnh đại diện, VD: uploads/avatars/mck.jpg
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Một nghệ sĩ có nhiều sản phẩm; xoá nghệ sĩ thì xoá luôn sản phẩm của họ
    products = db.relationship(
        'Product', backref='artist', lazy=True, cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Artist {self.name}>'


class Product(db.Model):
    """Sản phẩm âm nhạc & merch: Album Vinyl/CD/Cassette, USB Album, Áo thun, Photobook..."""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)

    title = db.Column(db.String(200), nullable=False)       # Tên Album/Sản phẩm
    category = db.Column(db.String(50), nullable=False, default=CATEGORY_CHOICES[0])
    price = db.Column(db.Numeric(12, 2), nullable=False, default=0)   # Giá bán (VNĐ)
    stock = db.Column(db.Integer, nullable=False, default=0)          # Số lượng tồn
    description = db.Column(db.Text)

    cover_image = db.Column(db.String(255))        # ảnh bìa sản phẩm (bổ sung để hiển thị đẹp hơn)
    demo_audio_file = db.Column(db.String(255))     # file mp3 nghe thử

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Một sản phẩm (album) có nhiều track
    tracks = db.relationship(
        'Track', backref='product', lazy=True,
        cascade='all, delete-orphan', order_by='Track.track_number'
    )
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    @property
    def is_in_stock(self):
        return self.stock > 0

    def __repr__(self):
        return f'<Product {self.title}>'


class Track(db.Model):
    """Bài hát trong Album"""
    __tablename__ = 'tracks'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    track_number = db.Column(db.Integer, nullable=False)
    song_name = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.String(10))   # định dạng "mm:ss", VD: "03:45"

    def __repr__(self):
        return f'<Track {self.track_number}. {self.song_name}>'


class Order(db.Model):
    """Đơn hàng: thông tin giao hàng, thanh toán, mã QR"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_code = db.Column(db.String(20), unique=True, nullable=False)  # mã đơn, VD: DH3F9A21C0

    customer_name = db.Column(db.String(150), nullable=False)
    customer_email = db.Column(db.String(150), nullable=False)
    customer_phone = db.Column(db.String(20))
    shipping_address = db.Column(db.Text, nullable=False)   # địa chỉ giao hàng

    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    status = db.Column(db.String(50), nullable=False, default=ORDER_STATUS_CHOICES[0])

    qr_code_image = db.Column(db.String(255))   # đường dẫn ảnh mã QR của đơn hàng
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship(
        'OrderItem', backref='order', lazy=True, cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Order {self.order_code}>'


class OrderItem(db.Model):
    """Chi tiết từng sản phẩm trong một đơn hàng (giỏ hàng đã chốt)"""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)   # giá tại thời điểm đặt hàng

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def __repr__(self):
        return f'<OrderItem product_id={self.product_id} x{self.quantity}>'


class ChatMessage(db.Model):
    """
    Tin nhắn của khung chat 'Chat với nhân viên' trên website.
    Không cần khách đăng nhập: mỗi trình duyệt khách được gán 1 session_id ngẫu nhiên
    (lưu trong cookie session Flask), toàn bộ tin nhắn qua lại giữa khách <-> admin
    của session đó được nhóm chung vào 1 cuộc hội thoại trong trang quản trị.
    """
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), nullable=False, index=True)
    sender = db.Column(db.String(10), nullable=False)   # 'customer' hoặc 'admin'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ChatMessage {self.sender}: {self.message[:20]}>'
