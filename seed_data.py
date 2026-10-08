"""
Script tạo dữ liệu mẫu để chạy demo nhanh.
Chạy bằng lệnh:  python seed_data.py

Lưu ý: script sẽ XOÁ SẠCH dữ liệu cũ trong CSDL trước khi tạo lại,
chỉ dùng cho môi trường phát triển / demo đồ án.

Ảnh đại diện / ảnh bìa / file nhạc KHÔNG được gán sẵn ở đây vì chưa có file thật.
Sau khi seed xong, vào từng sản phẩm rồi bấm "Sửa ảnh bìa / nhạc nghe thử"
(hoặc truy cập /quan-tri/san-pham/<id>/sua) để tải ảnh/nhạc thật lên.
Muốn thêm album hoàn toàn mới kèm ảnh/nhạc ngay từ đầu, dùng trang
"+ Thêm sản phẩm" (/quan-tri/san-pham/them) trên thanh điều hướng.
"""
from app import create_app
from extensions import db
from models import Artist, Product, Track

app = create_app()

with app.app_context():
    # Xoá dữ liệu cũ, tạo lại từ đầu cho sạch
    db.drop_all()
    db.create_all()

    # ---- Nghệ sĩ mẫu ----
    mck = Artist(
        name='MCK',
        bio='Rapper, nhạc sĩ Việt Nam, nổi bật với các dự án mang màu sắc bolero pha trap.',
    )
    tlinh = Artist(
        name='tlinh',
        bio='Ca sĩ, rapper trẻ với chất nhạc R&B/hip-hop giàu cảm xúc và ca từ tự sự.',
    )
    obito = Artist(
        name='obito',
        bio='Rapper miền Bắc, thành viên nhóm SpaceSpeakers, phong cách lyrical sắc sảo.',
    )
    db.session.add_all([mck, tlinh, obito])
    db.session.flush()  # để có id trước khi tạo Product

    # ---- Sản phẩm mẫu (chưa có ảnh bìa / nhạc thật, sẽ hiện icon mặc định) ----
    p1 = Product(
        artist_id=mck.id,
        title='Trong Lăng Kính Đa Chiều (Vinyl)',
        category='Đĩa Vinyl',
        price=890000,
        stock=25,
        description='Bản vinyl giới hạn của album, ép tại xưởng trong nước, kèm bìa in nổi.',
    )
    p2 = Product(
        artist_id=tlinh.id,
        title='Gieo Quẻ (CD Deluxe)',
        category='CD',
        price=250000,
        stock=60,
        description='Bản CD deluxe kèm photobook mini và lyric card.',
    )
    p3 = Product(
        artist_id=obito.id,
        title='Talk Show (USB Album)',
        category='USB Album',
        price=350000,
        stock=40,
        description='Trọn bộ album lossless trên USB thiết kế theo hình biểu tượng của nghệ sĩ.',
    )
    p4 = Product(
        artist_id=mck.id,
        title='Áo Thun Tour 2026',
        category='Áo thun',
        price=390000,
        stock=100,
        description='Áo thun cotton in hình graphic từ tour diễn 2026.',
    )
    db.session.add_all([p1, p2, p3, p4])
    db.session.flush()

    # ---- Track mẫu cho album Vinyl của MCK ----
    tracks = [
        Track(product_id=p1.id, track_number=1, song_name='Vô Đối', duration='03:12'),
        Track(product_id=p1.id, track_number=2, song_name='Bo', duration='02:58'),
        Track(product_id=p1.id, track_number=3, song_name='Túy Âm (Remix)', duration='04:05'),
    ]
    db.session.add_all(tracks)

    db.session.commit()
    print('Đã tạo dữ liệu mẫu thành công! (chưa có ảnh/nhạc thật - xem hướng dẫn ở đầu file này)')
