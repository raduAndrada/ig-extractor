"""Posts routes blueprint."""
from flask import Blueprint, render_template, jsonify, request, current_app, session
from app import db
from app.models.post import Post
from app.models.category import Category
from app.services.instagram_service import InstagramService
from app.database_utils import search_posts_fts
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('posts', __name__, url_prefix='/posts')


@bp.route('/')
def list_posts():
    """List all posts with optional filters."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category', type=int)
    
    query = Post.query
    
    # Apply search filter using FTS5
    if search:
        # Use FTS5 for full-text search
        post_ids = search_posts_fts(search, limit=1000)
        if post_ids:
            query = query.filter(Post.id.in_(post_ids))
        else:
            # Fallback to LIKE search if FTS fails
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
def view_post(post_id):
    """View single post detail."""
    post = Post.query.get_or_404(post_id)
    available_categories = Category.query.all()
    
    # Convert categories to simple dicts for JavaScript
    categories_json = [{'id': c.id, 'name': c.name, 'color': c.color} for c in available_categories]
    
    return render_template('posts/detail.html', 
                         post=post, 
                         available_categories=available_categories,
                         categories_json=categories_json)


@bp.route('/fetch', methods=['POST'])
def fetch_posts():
    """Trigger fetching new posts from Instagram."""
    # Check if logged in
    if not session.get('instagram_logged_in'):
        return jsonify({
            'success': False,
            'error': 'Not logged in to Instagram. Please login first in Settings.'
        }), 401
    
    username = session.get('instagram_username')
    
    try:
        data = request.get_json() or {}
        max_posts = data.get('max_posts', current_app.config.get('MAX_POSTS_PER_FETCH', 50))
        
        instagram_service = InstagramService()
        
        # Load existing session
        try:
            instagram_service.loader.load_session_from_file(username, f"session-{username}")
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return jsonify({
                'success': False,
                'error': 'Session expired. Please login again.'
            }), 401
        
        # Fetch posts
        result = instagram_service.fetch_saved_posts(max_posts=max_posts)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/<int:post_id>/categorize', methods=['POST'])
def categorize_post(post_id):
    """Add/remove category from post."""
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    category_id = data.get('category_id')
    action = data.get('action', 'add')  # 'add' or 'remove'
    
    from app.models.category import Category
    category = Category.query.get_or_404(category_id)
    
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
def search_posts():
    """Full-text search across posts using FTS5."""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'posts': []})
    
    try:
        # Use FTS5 for search
        post_ids = search_posts_fts(query, limit=50)
        
        if not post_ids:
            return jsonify({'posts': []})
        
        # Fetch posts in the order returned by FTS (by relevance)
        posts = []
        for post_id in post_ids:
            post = Post.query.get(post_id)
            if post:
                posts.append(post.to_dict())
        
        return jsonify({
            'posts': posts,
            'count': len(posts),
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        # Fallback to basic search
        posts = Post.query.filter(
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
def stats():
    """Get post statistics."""
    total = Post.query.count()
    uncategorized = Post.query.filter(~Post.categories.any()).count()
    
    # Get posts by media type
    photos = Post.query.filter_by(media_type='photo').count()
    videos = Post.query.filter_by(media_type='video').count()
    carousels = Post.query.filter_by(media_type='carousel').count()
    
    return jsonify({
        'total': total,
        'uncategorized': uncategorized,
        'photos': photos,
        'videos': videos,
        'carousels': carousels
    })
