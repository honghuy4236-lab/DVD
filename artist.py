from flask import Blueprint, render_template
from models import Artist

artist_bp = Blueprint('artist', __name__)


@artist_bp.route('/<int:artist_id>')
def detail(artist_id):
    """Trang chi tiết một nghệ sĩ: tiểu sử + toàn bộ sản phẩm của họ."""
    artist = Artist.query.get_or_404(artist_id)
    return render_template('artist_detail.html', artist=artist)
