"""Instagram authentication routes."""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.services.instagram_service import InstagramService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('instagram', __name__, url_prefix='/instagram')


@bp.route('/login', methods=['POST'])
@login_required
def login():
    """Login to Instagram and link to current user."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            'success': False,
            'message': 'Username and password required'
        }), 400
    
    instagram_service = InstagramService()
    result = instagram_service.login(username, password)
    
    if result['success']:
        # Store Instagram username on user record
        current_user.instagram_username = username
        db.session.commit()
        logger.info(f"User {current_user.username} linked Instagram account: {username}")
    
    return jsonify(result)


@bp.route('/login-2fa', methods=['POST'])
@login_required
def login_2fa():
    """Complete login with 2FA code."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    code = data.get('code')
    
    if not all([username, password, code]):
        return jsonify({
            'success': False,
            'message': 'Username, password, and 2FA code required'
        }), 400
    
    instagram_service = InstagramService()
    
    # First attempt regular login (will trigger 2FA)
    try:
        instagram_service.loader.login(username, password)
    except:
        pass
    
    # Then complete with 2FA
    result = instagram_service.login_with_2fa(username, password, code)
    
    if result['success']:
        current_user.instagram_username = username
        db.session.commit()
        logger.info(f"User {current_user.username} linked Instagram account: {username} (2FA)")
    
    return jsonify(result)


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout from Instagram."""
    current_user.instagram_username = None
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })


@bp.route('/status', methods=['GET'])
@login_required
def status():
    """Check Instagram login status."""
    username = current_user.instagram_username
    
    if username:
        # Verify session is still valid
        instagram_service = InstagramService()
        try:
            instagram_service.loader.load_session_from_file(username, f"session-{username}")
            is_valid = instagram_service.is_logged_in()
        except:
            is_valid = False
            
        if not is_valid:
            current_user.instagram_username = None
            db.session.commit()
            username = None
    
    return jsonify({
        'logged_in': username is not None,
        'username': username,
        'last_synced': current_user.instagram_synced_at.isoformat() if current_user.instagram_synced_at else None
    })
