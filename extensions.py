from flask_sqlalchemy import SQLAlchemy

# Khởi tạo ở đây (chưa gắn với app) để models.py và app.py đều import được
# mà không bị lỗi import vòng (circular import).
db = SQLAlchemy()
