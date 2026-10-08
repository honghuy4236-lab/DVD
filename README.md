# H-DVD — Khung Website TMĐT Bán Ấn Phẩm & Merch Nghệ Sĩ Việt

Đồ án học phần: website kiểu **Bandcamp phiên bản Việt Nam** — bán Đĩa Vinyl/CD/Cassette,
USB Album, Merchandise và cho nghe thử nhạc, xây bằng **Python (Flask) + SQLAlchemy**.

## 1. Công nghệ sử dụng

- **Flask** — web framework, tổ chức route theo Blueprint (main, artist, product, cart, order)
- **Flask-SQLAlchemy** — ORM, ánh xạ 5 bảng: `Artist`, `Product`, `Track`, `Order`, `OrderItem`
- **SQLite** — CSDL mặc định (file `database.db`, tự sinh khi chạy lần đầu), dễ đổi sang MySQL/PostgreSQL
- **VietQR.io** — sinh ảnh mã QR chuyển khoản ngân hàng thật cho từng đơn hàng (không cần thư viện Python riêng)
- **Jinja2** — template HTML, không dùng JS framework nặng, dễ hiểu để bảo vệ đồ án

## 2. Cấu trúc thư mục

```
bandcamp_vietnam/
├── app.py                # Khởi tạo Flask app (application factory), đăng ký Blueprint
├── config.py             # Cấu hình (CSDL, thư mục upload, secret key)
├── extensions.py         # Đối tượng db (SQLAlchemy) dùng chung
├── models.py             # 5 bảng CSDL: Artist, Product, Track, Order, OrderItem
├── seed_data.py          # Script tạo dữ liệu mẫu để demo (MCK, tlinh, obito...)
├── requirements.txt
├── routes/
│   ├── main.py           # Trang chủ, tìm kiếm, lọc theo danh mục
│   ├── artist.py         # Trang chi tiết nghệ sĩ
│   ├── product.py        # Trang chi tiết sản phẩm (tracklist, nghe thử, thêm giỏ)
│   ├── cart.py           # Giỏ hàng (lưu trong session, không cần đăng nhập)
│   ├── order.py          # Đặt hàng + sinh mã QR thanh toán
│   ├── admin.py          # Quản trị: Nghệ sĩ / Sản phẩm / Đơn hàng / Tin nhắn
│   └── chat.py           # API chat cho khách (gửi/nhận tin nhắn qua session ẩn danh)
├── templates/            # Giao diện HTML (Jinja2) - trang khách hàng
│   └── admin/            # Giao diện khu vực quản trị (đăng nhập, dashboard, CRUD, tin nhắn)
└── static/
    ├── css/style.css     # Toàn bộ giao diện (theme "vinyl / cassette")
    ├── js/
    │   ├── main.js
    │   └── chat-widget.js   # Khung liên hệ nổi: chat + Zalo
    ├── img/bank-logo.png    # Logo ngân hàng hiển thị cạnh mã QR thanh toán
    └── uploads/          # Nơi để ảnh nghệ sĩ, ảnh bìa album, file mp3 demo
        ├── avatars/
        ├── covers/
        ├── audio/
        └── merch/
```

## 3. Cài đặt & chạy thử (trên VS Code)

Mở thư mục này trong VS Code, mở Terminal (`Ctrl + ~`) rồi chạy:

```bash
# 1. Tạo môi trường ảo (khuyên dùng)
python -m venv venv
venv\Scripts\activate        # Windows
# hoặc: source venv/bin/activate   # macOS/Linux

# 2. Cài thư viện
pip install -r requirements.txt

# 3. (Tuỳ chọn) Tạo dữ liệu mẫu để demo ngay
python seed_data.py

# 4. Chạy server
python app.py
```

Sau đó mở trình duyệt tại: **http://127.0.0.1:5000**

> Nếu không chạy `seed_data.py`, website vẫn chạy được nhưng chưa có sản phẩm nào — bạn
> có thể tự thêm dữ liệu qua Flask shell hoặc viết thêm trang quản trị (gợi ý mở rộng bên dưới).

## 4. Khu vực Quản trị (Admin)

Truy cập tại **`/quan-tri`** (có link "Quản trị" nhỏ ở cuối trang, hoặc gõ thẳng URL) —
yêu cầu đăng nhập, tách biệt hoàn toàn với trang khách hàng.

- **Đăng nhập mặc định**: `admin` / `admin123` (đổi trong `config.py`, mục `ADMIN_USERNAME` /
  `ADMIN_PASSWORD`, hoặc qua biến môi trường — **nhớ đổi trước khi demo/nộp công khai**)
- **Tổng quan** — số nghệ sĩ, sản phẩm, đơn hàng, tổng doanh thu; danh sách đơn hàng gần đây
- **Nghệ sĩ** — thêm / sửa / xoá, upload ảnh đại diện
- **Sản phẩm** — thêm / sửa / xoá, upload ảnh bìa + file nhạc nghe thử, nhập nhanh tracklist
  (mỗi dòng dạng `Tên bài hát | 03:45`), gán vào nghệ sĩ có sẵn hoặc tạo nghệ sĩ mới ngay tại chỗ
- **Đơn hàng** — xem danh sách, xem chi tiết từng đơn (sản phẩm, địa chỉ giao hàng, mã QR),
  cập nhật trạng thái (Chờ thanh toán → Đã thanh toán → Đang giao hàng → Hoàn thành / Đã hủy)
- **Tin nhắn** — hộp thư của khung "Chat với nhân viên", xem theo từng khách và trả lời trực tiếp

Định dạng file hỗ trợ: ảnh (`jpg, jpeg, png, webp, gif`), nhạc (`mp3, wav, ogg, m4a`).

> Lưu ý bảo mật: cơ chế đăng nhập ở đây dùng session đơn giản, đủ cho phạm vi đồ án học phần.
> Nếu triển khai thật, nên đổi mật khẩu mặc định, dùng HTTPS, và cân nhắc hash mật khẩu +
> giới hạn số lần đăng nhập sai.

> Lưu ý bản quyền: nếu đây là đồ án nộp/demo công khai, chỉ nên dùng ảnh và nhạc bạn có quyền
> sử dụng (ảnh tự chụp/tự thiết kế, nhạc mẫu do bạn tạo hoặc nhạc royalty-free), tránh dùng
> nguyên bìa album/bài hát gốc của nghệ sĩ nếu chưa được phép.

## 4b. Cấu hình mã QR chuyển khoản (VietQR)

Mã QR ở trang thanh toán dùng dịch vụ ảnh miễn phí của **VietQR.io** (chuẩn NAPAS 247) — quét
được thẳng bằng app ngân hàng/ví điện tử, tự điền sẵn số tiền và nội dung chuyển khoản.

Mở `config.py`, sửa 3 giá trị sau thành tài khoản ngân hàng thật của bạn (đang để tài khoản demo):

```python
BANK_ID = 'MB'                    # mã BIN (VD 970422) hoặc tên viết tắt: MB, VCB, ICB, TCB, ACB, TPB...
BANK_ACCOUNT_NO = '0123456789'    # số tài khoản nhận tiền
BANK_ACCOUNT_NAME = 'SOUND VAULT' # tên chủ tài khoản (không dấu, viết hoa)
```

Tra cứu mã ngân hàng tại: https://api.vietqr.io/v2/banks — dùng để demo/nộp bài là đủ, không
cần đăng ký tài khoản VietQR (đây là "Quick Link" miễn phí, không cần API key).

## 4c. Khung liên hệ nổi (Chat với nhân viên / Zalo)

Ở mọi trang khách hàng có nút **"Liên hệ"** nổi góc dưới bên phải, bấm vào hiện 2 lựa chọn:

- **Chat với nhân viên** — khung chat nhỏ ngay trên trang, khách gõ tin nhắn và gửi mà không
  cần đăng nhập (mỗi trình duyệt được gán 1 mã phiên ẩn danh qua cookie). Toàn bộ tin nhắn được
  lưu vào bảng `ChatMessage` và xuất hiện ngay trong mục **Tin nhắn** ở khu quản trị (`/quan-tri/tin-nhan`),
  admin trả lời tại đó thì khách sẽ thấy tin nhắn mới trong vòng vài giây (khung chat tự làm mới).
- **Liên hệ Zalo** — hiện mã QR quét ra thẳng cuộc trò chuyện Zalo (link dạng `zalo.me/<so_dien_thoai>`),
  kèm nút "Mở Zalo" cho máy tính. Đổi số điện thoại thật của bạn ở `config.py`, mục `ZALO_PHONE`
  (đang để tạm số trùng với tài khoản ngân hàng demo).

Mã QR Zalo dùng dịch vụ ảnh miễn phí `api.qrserver.com` (không cần API key), tương tự cách làm
mã QR VietQR ở trên.

## 5. Luồng hoạt động chính

1. **Trang chủ (`/`)** — liệt kê sản phẩm, tìm theo tên, lọc theo danh mục, dải nghệ sĩ nổi bật.
2. **Trang nghệ sĩ (`/nghe-si/<id>`)** — tiểu sử + toàn bộ sản phẩm của nghệ sĩ đó.
3. **Trang sản phẩm (`/san-pham/<id>`)** — mô tả, danh sách track, audio nghe thử, form thêm vào giỏ.
4. **Giỏ hàng (`/gio-hang`)** — xem, xoá sản phẩm; giỏ hàng lưu trong session (không cần tài khoản).
5. **Thanh toán (`/don-hang/thanh-toan`)** — nhập tên, email, SĐT, địa chỉ giao hàng.
6. Khi xác nhận: hệ thống tạo `Order` + các `OrderItem`, **sinh mã QR chuyển khoản VietQR** chứa
   sẵn số tiền và nội dung (mã đơn hàng), rồi chuyển sang trang
   **Đặt hàng thành công (`/don-hang/thanh-cong/<order_code>`)** hiển thị mã QR để khách quét thanh toán.

## 6. Vài lưu ý khi bảo vệ đồ án

- Bảng `category` (Product) và `status` (Order) mình dùng kiểu chuỗi (`String`) thay vì
  `Enum` của SQLAlchemy để đơn giản hoá thao tác hiển thị trong template và dễ debug —
  danh sách giá trị hợp lệ khai báo tại `CATEGORY_CHOICES` / `ORDER_STATUS_CHOICES` trong `models.py`.
- Mình có thêm trường `cover_image` (ảnh bìa) và `created_at` ngoài schema gốc để website
  hiển thị đẹp và sắp xếp được sản phẩm mới nhất — có thể bỏ nếu đồ án yêu cầu bám sát schema tối giản.
- Giỏ hàng hiện dùng **session** (không cần đăng nhập) — phù hợp với phạm vi đồ án; nếu cần
  có tài khoản khách hàng, nên thêm bảng `Customer`/`User` và Flask-Login.
- Ảnh/audio hiện phải copy thủ công vào các thư mục trong `static/uploads/` và điền đúng
  đường dẫn khi tạo `Product`/`Artist` (xem ví dụ trong `seed_data.py`).

## 7. Hướng mở rộng gợi ý (nếu còn thời gian)

- Trang quản trị (CRUD Artist/Product/Track) — có thể dùng `Flask-Admin` cho nhanh.
- Đăng ký/đăng nhập khách hàng (`Flask-Login`) để xem lịch sử đơn hàng.
- Kết nối cổng thanh toán tự động xác nhận (VNPay/Momo/Open API ngân hàng) thay vì chờ khách tự chuyển khoản theo mã QR.
- Phân trang (`paginate()`) khi số sản phẩm lớn.
- Đánh giá/bình luận sản phẩm.
