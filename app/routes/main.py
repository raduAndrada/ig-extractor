"""Main routes blueprint."""
from flask import Blueprint, render_template, current_app, send_from_directory
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
import os

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Home page showing dashboard."""
    # Get statistics
    post_count = Post.query.count()
    category_count = Category.query.count()
    tag_count = Tag.query.count()
    uncategorized_count = Post.query.filter(~Post.categories.any()).count()
    
    return render_template(
        'index.html',
        post_count=post_count,
        category_count=category_count,
        tag_count=tag_count,
        uncategorized_count=uncategorized_count
    )


@bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@bp.route('/settings')
def settings():
    """Settings page."""
    return render_template('settings.html')


@bp.route('/search')
def search():
    """Search page."""
    return render_template('search.html')


@bp.route('/data/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    """Serve thumbnail images from data directory."""
    thumbnail_dir = os.path.join(current_app.config['BASE_DIR'], 'data', 'thumbnails')
    return send_from_directory(thumbnail_dir, filename)
