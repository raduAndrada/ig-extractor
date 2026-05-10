"""Main routes blueprint."""
from flask import Blueprint, render_template, current_app, send_from_directory
from flask_login import login_required, current_user
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
import os

bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def index():
    """Home page showing dashboard."""
    # Get statistics for current user
    post_count = Post.query.filter_by(user_id=current_user.id).count()
    category_count = Category.query.filter_by(user_id=current_user.id).count()
    tag_count = Tag.query.filter_by(user_id=current_user.id).count()
    uncategorized_count = Post.query.filter_by(user_id=current_user.id).filter(~Post.categories.any()).count()
    
    # Get recent posts
    recent_posts = Post.query.filter_by(user_id=current_user.id).order_by(Post.saved_at.desc()).limit(6).all()
    
    return render_template(
        'index.html',
        post_count=post_count,
        category_count=category_count,
        tag_count=tag_count,
        uncategorized_count=uncategorized_count,
        recent_posts=recent_posts
    )


@bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@bp.route('/settings')
@login_required
def settings():
    """Settings page."""
    return render_template('settings.html')


@bp.route('/search')
@login_required
def search():
    """Search page."""
    return render_template('search.html')


@bp.route('/data/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    """Serve thumbnail images from data directory."""
    thumbnail_dir = os.path.join(current_app.config['BASE_DIR'], 'data', 'thumbnails')
    return send_from_directory(thumbnail_dir, filename)
