import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Giá trị mặc định chỉ để chạy local; app.py sẽ từ chối khởi động trên host thật nếu còn dùng 2 giá trị này.
DEFAULT_SECRET_KEY = 'khoa-bi-mat-dung-de-phat-trien-doi-khi-len-that'
DEFAULT_ADMIN_PASSWORD = 'admin123'


class Config:
    """
    Cấu hình chung cho ứng dụng.
    Trong đồ án, có thể để nguyên các giá trị mặc định để chạy local.
    Khi triển khai thật, nên đưa SECRET_KEY và DATABASE_URL vào biến môi trường.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)

    # Cookie phiên (giỏ hàng + đăng nhập admin): chặn JS đọc, không gửi chéo site, chỉ gửi qua HTTPS khi lên host.
    # Trên host đặt biến môi trường HTTPS_ONLY=1; chạy local (http) thì để trống.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('HTTPS_ONLY') == '1'

    # Mặc định dùng SQLite cho gọn nhẹ, phù hợp làm đồ án học phần.
    # Muốn đổi sang MySQL/PostgreSQL chỉ cần đổi biến môi trường DATABASE_URL.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Thư mục lưu file upload: ảnh nghệ sĩ, ảnh bìa album, file nhạc demo, mã QR...
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

    # Tài khoản đăng nhập khu vực quản trị (/quan-tri).
    # Đồ án nên đổi 2 giá trị này (hoặc đặt qua biến môi trường) trước khi nộp/demo công khai.
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', DEFAULT_ADMIN_PASSWORD)

    # ---- Cấu hình VietQR (mã QR chuyển khoản ngân hàng ở trang thanh toán) ----
    # BANK_ID: mã BIN (VD 970422) HOẶC tên viết tắt ngân hàng (VD: MB, VCB, ICB, TCB, ACB, TPB...)
    # Tra cứu mã ngân hàng tại: https://api.vietqr.io/v2/banks
    # ĐANG DÙNG SỐ TÀI KHOẢN DEMO — đổi thành tài khoản thật của bạn để quét thanh toán thật được.
    BANK_ID = os.environ.get('BANK_ID', 'MB')
    BANK_ACCOUNT_NO = os.environ.get('BANK_ACCOUNT_NO', '0869918423')
    BANK_ACCOUNT_NAME = os.environ.get('BANK_ACCOUNT_NAME', 'H DVD')
    VIETQR_TEMPLATE = os.environ.get('VIETQR_TEMPLATE', 'compact2')  # compact | compact2 | qr_only | print

    # ---- Liên hệ Zalo (nút "Liên hệ" nổi ở góc trang) ----
    # Số điện thoại đăng ký Zalo — dùng để tạo link zalo.me/<so_dien_thoai> và mã QR tương ứng.
    ZALO_PHONE = os.environ.get('ZALO_PHONE', '0869918423')

    # Giới hạn dung lượng file gửi lên (phòng khi upload file nhạc/ảnh quá nặng)
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
