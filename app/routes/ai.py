"""AI-powered categorization and tagging routes."""
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
from app.services.ai_service import AIService
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('ai', __name__, url_prefix='/ai')


@bp.route('/suggest-categories/<int:post_id>', methods=['POST'])
@login_required
def suggest_categories(post_id):
    """Get AI category suggestions for a post.
    
    Returns:
        {
            'suggestions': [
                {'category': 'Food', 'confidence': 0.95},
                {'category': 'Travel', 'confidence': 0.7}
            ]
        }
    """
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first_or_404()
    
    # Get available categories for current user
    categories = [cat.name for cat in Category.query.filter_by(user_id=current_user.id).all()]
    
    if not categories:
        return jsonify({
            'success': False,
            'error': 'No categories available. Create some categories first.'
        }), 400
    
    try:
        ai_service = AIService()
        suggestions = ai_service.suggest_categories(post, categories)
        
        # Format response
        formatted_suggestions = [
            {
                'category': cat,
                'confidence': round(conf, 2)
            }
            for cat, conf in suggestions
        ]
        
        return jsonify({
            'success': True,
            'suggestions': formatted_suggestions
        })
        
    except Exception as e:
        logger.error(f"Category suggestion failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/extract-tags/<int:post_id>', methods=['POST'])
@login_required
def extract_tags(post_id):
    """Extract tags from a post.
    
    Returns:
        {
            'tags': ['food', 'recipe', 'delicious', ...]
        }
    """
    post = Post.query.filter_by(id=post_id, user_id=current_user.id).first_or_404()
    
    try:
        ai_service = AIService()
        tags = ai_service.extract_tags(post)
        
        return jsonify({
            'success': True,
            'tags': tags
        })
        
    except Exception as e:
        logger.error(f"Tag extraction failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/batch-categorize', methods=['POST'])
@login_required
def batch_categorize():
    """Suggest categories for multiple posts.
    
    Request:
        {
            'post_ids': [1, 2, 3, ...],
            'auto_apply': false,  // If true, automatically apply high-confidence suggestions
            'confidence_threshold': 0.8  // Only auto-apply if confidence >= threshold
        }
    
    Returns:
        {
            'results': {
                '1': [{'category': 'Food', 'confidence': 0.95}],
                '2': [{'category': 'Travel', 'confidence': 0.8}]
            },
            'auto_applied': 5  // Number of categories auto-applied
        }
    """
    data = request.get_json()
    post_ids = data.get('post_ids', [])
    auto_apply = data.get('auto_apply', False)
    threshold = data.get('confidence_threshold', 0.8)
    
    if not post_ids:
        # Process all uncategorized posts for current user
        posts = Post.query.filter_by(user_id=current_user.id).filter(~Post.categories.any()).limit(50).all()
    else:
        posts = Post.query.filter(Post.id.in_(post_ids), Post.user_id == current_user.id).all()
    
    # Get available categories for current user
    categories = [cat.name for cat in Category.query.filter_by(user_id=current_user.id).all()]
    category_map = {cat.name: cat for cat in Category.query.filter_by(user_id=current_user.id).all()}
    
    if not categories:
        return jsonify({
            'success': False,
            'error': 'No categories available'
        }), 400
    
    try:
        ai_service = AIService()
        suggestions = ai_service.batch_suggest_categories(posts, categories)
        
        # Format results
        results = {}
        auto_applied_count = 0
        
        for post_id, cats in suggestions.items():
            formatted = [
                {'category': cat, 'confidence': round(conf, 2)}
                for cat, conf in cats
            ]
            results[str(post_id)] = formatted
            
            # Auto-apply if requested
            if auto_apply:
                post = next((p for p in posts if p.id == post_id), None)
                if post:
                    for cat, conf in cats:
                        if conf >= threshold:
                            category = category_map.get(cat)
                            if category and category not in post.categories:
                                post.categories.append(category)
                                auto_applied_count += 1
        
        if auto_apply:
            db.session.commit()
        
        return jsonify({
            'success': True,
            'results': results,
            'auto_applied': auto_applied_count
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Batch categorization failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/batch-extract-tags', methods=['POST'])
def batch_extract_tags():
    """Extract tags for multiple posts.
    
    Request:
        {
            'post_ids': [1, 2, 3, ...],
            'auto_create': true  // If true, create Tag objects
        }
    
    Returns:
        {
            'results': {
                '1': ['food', 'recipe'],
                '2': ['travel', 'beach']
            },
            'tags_created': 15
        }
    """
    data = request.get_json()
    post_ids = data.get('post_ids', [])
    auto_create = data.get('auto_create', False)
    
    if not post_ids:
        return jsonify({
            'success': False,
            'error': 'No post IDs provided'
        }), 400
    
    # Get posts
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    
    try:
        ai_service = AIService()
        tag_results = ai_service.batch_extract_tags(posts)
        
        tags_created = 0
        
        # Auto-create tags if requested
        if auto_create:
            for post_id, tag_names in tag_results.items():
                post = next((p for p in posts if p.id == post_id), None)
                if not post:
                    continue
                
                for tag_name in tag_names:
                    # Get or create tag
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                        tags_created += 1
                    
                    # Associate with post if not already
                    if tag not in post.tags:
                        post.tags.append(tag)
            
            db.session.commit()
        
        # Format results
        results = {str(k): v for k, v in tag_results.items()}
        
        return jsonify({
            'success': True,
            'results': results,
            'tags_created': tags_created
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Batch tag extraction failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/accept-suggestion/<int:post_id>', methods=['POST'])
def accept_suggestion(post_id):
    """Accept an AI category suggestion and apply it to post.
    
    Request:
        {
            'category': 'Food',
            'confidence': 0.95
        }
    """
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    category_name = data.get('category')
    
    if not category_name:
        return jsonify({
            'success': False,
            'error': 'Category name required'
        }), 400
    
    try:
        category = Category.query.filter_by(name=category_name).first()
        
        if not category:
            return jsonify({
                'success': False,
                'error': f'Category "{category_name}" not found'
            }), 404
        
        if category in post.categories:
            return jsonify({
                'success': False,
                'error': 'Category already assigned'
            }), 400
        
        post.categories.append(category)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Applied category: {category_name}'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to accept suggestion: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
