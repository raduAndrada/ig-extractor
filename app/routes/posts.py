"""Posts routes blueprint."""
from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.post import Post
from app.models.category import Category
from app.services.instagram_service import InstagramService
from app.database_utils import search_posts_fts
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('posts', __name__, url_prefix='/posts')


@bp.route('/')
@login_required
def list_posts():
    """List all posts with optional filters."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    
    query = Post.query.filter_by(user_id=current_user.id)
    
    # Apply search filter using FTS5
    if search:
        post_ids = search_posts_fts(search, limit=1000)
        if post_ids:
            query = query.filter(Post.id.in_(post_ids))
        else:
            query = query.filter(
                db.or_(
                    Post.caption.contains(search),
                    Post.owner_username.contains(search)
                )
            )
    
    # Apply category filter
    if category_id:
        query = query.join(Post.categories).filter_by(id=category_id)
    
    # Pagination
    posts = query.order_by(Post.saved_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('posts/list.html', posts=posts, search=search)


@bp.route('/<int:post_id>')
@login_required
def view_post(post_id):
    """View single post detail."""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first_or_404()
    available_categories = Category.query.filter_by(user_id=current_user.id).all()
    
    # Convert categories to simple dicts for JavaScript
    categories_json = [{'id': c.id, 'name': c.name, 'color': c.color} for c in available_categories]
    
    return render_template('posts/detail.html', 
                         post=post, 
                         available_categories=available_categories,
                         categories_json=categories_json)


@bp.route('/fetch', methods=['POST'])
@login_required
def fetch_posts():
    """Trigger fetching new posts from Instagram."""
    try:
        data = request.get_json() or {}
        max_posts = data.get('max_posts', current_app.config.get('MAX_POSTS_PER_FETCH', 50))
        
        instagram_service = InstagramService()
        
        # Check if user has synced before
        if not current_user.instagram_username:
            return jsonify({
                'success': False,
                'error': 'Please connect your Instagram account first in Settings.'
            }), 401
        
        # Load session for current user
        try:
            instagram_service.loader.load_session_from_file(
                current_user.instagram_username, 
                f"session-{current_user.instagram_username}"
            )
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return jsonify({
                'success': False,
                'error': 'Instagram session expired. Please reconnect in Settings.'
            }), 401
        
        # Fetch posts for current user
        result = instagram_service.fetch_saved_posts(
            user_id=current_user.id,
            max_posts=max_posts
        )
        
        # Update user's last sync time
        if result.get('success'):
            from datetime import datetime
            current_user.instagram_synced_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/<int:post_id>/categorize', methods=['POST'])
@login_required
def categorize_post(post_id):
    """Add/remove category from post."""
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    category_id = data.get('category_id')
    action = data.get('action', 'add')
    
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    
    try:
        if action == 'add':
            if category not in post.categories:
                post.categories.append(category)
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': f'Added category: {category.name}'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Category already assigned'
                }), 400
        elif action == 'remove':
            if category in post.categories:
                post.categories.remove(category)
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': f'Removed category: {category.name}'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Category not assigned'
                }), 400
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid action'
            }), 400
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Categorize failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/search')
@login_required
def search_posts():
    """Full-text search across posts using FTS5."""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'posts': []})
    
    try:
        post_ids = search_posts_fts(query, limit=50)
        
        if not post_ids:
            return jsonify({'posts': []})
        
        # Fetch posts for current user only
        posts = []
        for post_id in post_ids:
            post = Post.query.filter_by(id=post_id, user_id=current_user.id).first()
            if post:
                posts.append(post.to_dict())
        
        return jsonify({
            'posts': posts,
            'count': len(posts),
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        posts = Post.query.filter_by(user_id=current_user.id).filter(
            db.or_(
                Post.caption.contains(query),
                Post.owner_username.contains(query)
            )
        ).limit(50).all()
        
        return jsonify({
            'posts': [post.to_dict() for post in posts],
            'count': len(posts),
            'query': query,
            'fallback': True
        })


@bp.route('/stats')
@login_required
def stats():
    """Get post statistics for current user."""
    total = Post.query.filter_by(user_id=current_user.id).count()
    uncategorized = Post.query.filter_by(user_id=current_user.id).filter(~Post.categories.any()).count()
    
    photos = Post.query.filter_by(user_id=current_user.id, media_type='photo').count()
    videos = Post.query.filter_by(user_id=current_user.id, media_type='video').count()
    carousels = Post.query.filter_by(user_id=current_user.id, media_type='carousel').count()
    
    return jsonify({
        'total': total,
        'uncategorized': uncategorized,
        'photos': photos,
        'videos': videos,
        'carousels': carousels
    })
