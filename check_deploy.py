"""
Kiểm tra trước khi đưa website lên host Linux (PythonAnywhere...).
Chạy tại thư mục gốc dự án:   python check_deploy.py

Windows không phân biệt chữ hoa/thường còn Linux thì có, nên "LOw.png" trong CSDL mà trên đĩa là "Low.png"
sẽ chạy tốt ở máy bạn nhưng mất ảnh trên host. Script này tìm đúng những lỗi đó, và báo dung lượng uploads.
Chỉ đọc dữ liệu, không sửa gì.
"""
import os
import sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(BASE, 'static')
DB = os.path.join(BASE, 'database.db')
LIMIT_MB = 400          # host miễn phí ~512 MB cho toàn bộ tài khoản, chừa chỗ cho thư viện Python
BIG_FILE_MB = 10


def exact_exists(rel_path):
    """True nếu file tồn tại và TỪNG đoạn tên khớp chính xác hoa/thường (đúng như Linux sẽ xét)."""
    current = STATIC
    for part in rel_path.split('/'):
        if not os.path.isdir(current) or part not in os.listdir(current):
            return False
        current = os.path.join(current, part)
    return os.path.isfile(current)


def main():
    if not os.path.isfile(DB):
        print('Không thấy database.db cạnh script này.')
        return

    con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    rows = []
    rows += [('Ảnh nghệ sĩ', n, p) for n, p in con.execute('SELECT name, avatar FROM artists')]
    rows += [('Ảnh bìa', n, p) for n, p in con.execute('SELECT title, cover_image FROM products')]
    rows += [('Nhạc nghe thử', n, p) for n, p in con.execute('SELECT title, demo_audio_file FROM products')]

    problems = 0
    for kind, name, path in rows:
        if not path:
            continue
        if '\\' in path:
            print(f'[DẤU \\ ]  {kind} "{name}": {path}  -> đổi \\ thành /')
            problems += 1
        elif not exact_exists(path):
            print(f'[THIẾU / SAI HOA-THƯỜNG]  {kind} "{name}": {path}')
            problems += 1

    # Dung lượng thư mục uploads
    total = 0
    uploads = os.path.join(STATIC, 'uploads')
    for root, _, files in os.walk(uploads):
        for f in files:
            size = os.path.getsize(os.path.join(root, f))
            total += size
            if size > BIG_FILE_MB * 1024 * 1024:
                rel = os.path.relpath(os.path.join(root, f), STATIC).replace(os.sep, '/')
                print(f'[FILE NẶNG {size / 1024 / 1024:.1f} MB]  {rel}  -> nên cắt đoạn nghe thử 30-60 giây')

    total_mb = total / 1024 / 1024
    print(f'\nstatic/uploads: {total_mb:.1f} MB (nên dưới {LIMIT_MB} MB nếu dùng gói miễn phí)')
    if total_mb > LIMIT_MB:
        problems += 1
        print('[QUÁ NẶNG] hãy nén ảnh PNG và cắt ngắn file nhạc trước khi nén zip.')

    print('\nKết quả:', 'OK, sẵn sàng.' if problems == 0 else f'có {problems} vấn đề cần xử lý ở trên.')


if __name__ == '__main__':
    main()
