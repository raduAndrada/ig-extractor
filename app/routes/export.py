"""Export and bulk operations routes."""
from flask import Blueprint, jsonify, request, send_file
from flask_login import login_required, current_user
from app import db
from app.models.post import Post
from app.models.category import Category
from app.models.tag import Tag
import json
import csv
import io
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('export', __name__, url_prefix='/export')


@bp.route('/json', methods=['POST'])
@login_required
def export_json():
    """Export posts to JSON format.
    
    Request:
        {
            'post_ids': [1, 2, 3] or 'all',
            'include_categories': true,
            'include_tags': true
        }
    """
    data = request.get_json() or {}
    post_ids = data.get('post_ids', 'all')
    include_categories = data.get('include_categories', True)
    include_tags = data.get('include_tags', True)
    
    try:
        # Get posts for current user only
        if post_ids == 'all':
            posts = Post.query.filter_by(user_id=current_user.id).all()
        else:
            posts = Post.query.filter(Post.id.in_(post_ids), Post.user_id == current_user.id).all()
        
        # Build export data
        export_data = {
            'exported_at': datetime.utcnow().isoformat(),
            'total_posts': len(posts),
            'posts': []
        }
        
        for post in posts:
            post_data = {
                'id': post.id,
                'instagram_id': post.instagram_id,
                'shortcode': post.shortcode,
                'caption': post.caption,
                'post_url': post.post_url,
                'media_type': post.media_type,
                'owner_username': post.owner_username,
                'owner_fullname': post.owner_fullname,
                'likes_count': post.likes_count,
                'comments_count': post.comments_count,
                'saved_at': post.saved_at.isoformat() if post.saved_at else None,
                'fetched_at': post.fetched_at.isoformat() if post.fetched_at else None
            }
            
            if include_categories:
                post_data['categories'] = [cat.name for cat in post.categories]
            
            if include_tags:
                post_data['tags'] = [tag.name for tag in post.tags]
            
            export_data['posts'].append(post_data)
        
        # Create file in memory
        output = io.BytesIO()
        output.write(json.dumps(export_data, indent=2).encode('utf-8'))
        output.seek(0)
        
        filename = f'instagram_posts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        return send_file(
            output,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"JSON export failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/csv', methods=['POST'])
def export_csv():
    """Export posts to CSV format.
    
    Request:
        {
            'post_ids': [1, 2, 3] or 'all',
            'include_categories': true,
            'include_tags': true
        }
    """
    data = request.get_json() or {}
    post_ids = data.get('post_ids', 'all')
    include_categories = data.get('include_categories', True)
    include_tags = data.get('include_tags', True)
    
    try:
        # Get posts
        if post_ids == 'all':
            posts = Post.query.all()
        else:
            posts = Post.query.filter(Post.id.in_(post_ids)).all()
        
        # Create CSV in memory
        output = io.StringIO()
        
        # Define columns
        columns = [
            'ID', 'Instagram ID', 'Shortcode', 'Caption', 'URL', 
            'Media Type', 'Owner', 'Likes', 'Comments', 'Saved At'
        ]
        
        if include_categories:
            columns.append('Categories')
        if include_tags:
            columns.append('Tags')
        
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        
        # Write rows
        for post in posts:
            row = {
                'ID': post.id,
                'Instagram ID': post.instagram_id,
                'Shortcode': post.shortcode,
                'Caption': post.caption or '',
                'URL': post.post_url,
                'Media Type': post.media_type,
                'Owner': post.owner_username,
                'Likes': post.likes_count,
                'Comments': post.comments_count,
                'Saved At': post.saved_at.strftime('%Y-%m-%d %H:%M:%S') if post.saved_at else ''
            }
            
            if include_categories:
                row['Categories'] = ', '.join([cat.name for cat in post.categories])
            
            if include_tags:
                row['Tags'] = ', '.join([tag.name for tag in post.tags])
            
            writer.writerow(row)
        
        # Convert to bytes
        output.seek(0)
        bytes_output = io.BytesIO(output.getvalue().encode('utf-8'))
        
        filename = f'instagram_posts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return send_file(
            bytes_output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"CSV export failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/stats', methods=['GET'])
def export_stats():
    """Get export statistics."""
    total_posts = Post.query.count()
    categorized = Post.query.filter(Post.categories.any()).count()
    tagged = Post.query.filter(Post.tags.any()).count()
    
    return jsonify({
        'total_posts': total_posts,
        'categorized': categorized,
        'tagged': tagged,
        'uncategorized': total_posts - categorized,
        'untagged': total_posts - tagged
    })
