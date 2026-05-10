"""Bulk operations routes."""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('bulk', __name__, url_prefix='/bulk')


@bp.route('/categorize', methods=['POST'])
@login_required
def bulk_categorize():
    """Apply category to multiple posts.
    
    Request:
        {
            'post_ids': [1, 2, 3],
            'category_id': 5,
            'action': 'add' or 'remove'
        }
    """
    data = request.get_json()
    post_ids = data.get('post_ids', [])
    category_id = data.get('category_id')
    action = data.get('action', 'add')
    
    if not post_ids or not category_id:
        return jsonify({
            'success': False,
            'error': 'post_ids and category_id required'
        }), 400
    
    try:
        posts = Post.query.filter(Post.id.in_(post_ids), Post.user_id == current_user.id).all()
        category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
        
        updated = 0
        
        for post in posts:
            if action == 'add':
                if category not in post.categories:
                    post.categories.append(category)
                    updated += 1
            elif action == 'remove':
                if category in post.categories:
                    post.categories.remove(category)
                    updated += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated': updated,
            'message': f'{action.capitalize()}ed category to {updated} posts'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Bulk categorize failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/tag', methods=['POST'])
def bulk_tag():
    """Apply tag to multiple posts.
    
    Request:
        {
            'post_ids': [1, 2, 3],
            'tag_name': 'vacation',
            'action': 'add' or 'remove'
        }
    """
    data = request.get_json()
    post_ids = data.get('post_ids', [])
    tag_name = data.get('tag_name')
    action = data.get('action', 'add')
    
    if not post_ids or not tag_name:
        return jsonify({
            'success': False,
            'error': 'post_ids and tag_name required'
        }), 400
    
    try:
        posts = Post.query.filter(Post.id.in_(post_ids)).all()
        
        # Get or create tag
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag and action == 'add':
            tag = Tag(name=tag_name)
            db.session.add(tag)
            db.session.flush()
        
        if not tag:
            return jsonify({
                'success': False,
                'error': f'Tag "{tag_name}" not found'
            }), 404
        
        updated = 0
        
        for post in posts:
            if action == 'add':
                if tag not in post.tags:
                    post.tags.append(tag)
                    updated += 1
            elif action == 'remove':
                if tag in post.tags:
                    post.tags.remove(tag)
                    updated += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated': updated,
            'message': f'{action.capitalize()}ed tag to {updated} posts'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Bulk tag failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/delete', methods=['POST'])
def bulk_delete():
    """Delete multiple posts.
    
    Request:
        {
            'post_ids': [1, 2, 3],
            'confirm': true
        }
    """
    data = request.get_json()
    post_ids = data.get('post_ids', [])
    confirm = data.get('confirm', False)
    
    if not post_ids:
        return jsonify({
            'success': False,
            'error': 'post_ids required'
        }), 400
    
    if not confirm:
        return jsonify({
            'success': False,
            'error': 'Please confirm deletion'
        }), 400
    
    try:
        posts = Post.query.filter(Post.id.in_(post_ids)).all()
        count = len(posts)
        
        for post in posts:
            db.session.delete(post)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'deleted': count,
            'message': f'Deleted {count} posts'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Bulk delete failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
