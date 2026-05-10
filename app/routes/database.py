"""Database management routes."""
from flask import Blueprint, jsonify, current_app
from app import db
from app.database_utils import (
    create_fts_table, 
    rebuild_fts_index, 
    get_fts_stats,
    drop_fts_table
)
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('database', __name__, url_prefix='/database')


@bp.route('/setup-fts', methods=['POST'])
def setup_fts():
    """Setup FTS5 full-text search table."""
    try:
        success = create_fts_table()
        
        if success:
            stats = get_fts_stats()
            return jsonify({
                'success': True,
                'message': 'FTS5 search enabled successfully',
                'stats': stats
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to setup FTS5'
            }), 500
            
    except Exception as e:
        logger.error(f"FTS setup failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/rebuild-fts', methods=['POST'])
def rebuild_fts():
    """Rebuild FTS5 index from scratch."""
    try:
        success = rebuild_fts_index()
        
        if success:
            stats = get_fts_stats()
            return jsonify({
                'success': True,
                'message': 'FTS5 index rebuilt successfully',
                'stats': stats
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to rebuild FTS5 index'
            }), 500
            
    except Exception as e:
        logger.error(f"FTS rebuild failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/fts-stats', methods=['GET'])
def fts_stats():
    """Get FTS5 statistics."""
    try:
        stats = get_fts_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Failed to get FTS stats: {e}")
        return jsonify({
            'indexed_posts': 0,
            'status': 'error',
            'error': str(e)
        }), 500


@bp.route('/drop-fts', methods=['POST'])
def drop_fts():
    """Drop FTS5 table and triggers (for debugging)."""
    try:
        success = drop_fts_table()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'FTS5 table dropped'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to drop FTS5 table'
            }), 500
            
    except Exception as e:
        logger.error(f"FTS drop failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
