"""Instagram authentication routes."""
from flask import Blueprint, request, jsonify, session, current_app
from app.services.instagram_service import InstagramService
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('instagram', __name__, url_prefix='/instagram')


@bp.route('/login', methods=['POST'])
def login():
    """Login to Instagram."""
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
        # Store username in session
        session['instagram_username'] = username
        session['instagram_logged_in'] = True
    
    return jsonify(result)


@bp.route('/login-2fa', methods=['POST'])
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
        session['instagram_username'] = username
        session['instagram_logged_in'] = True
    
    return jsonify(result)


@bp.route('/logout', methods=['POST'])
def logout():
    """Logout from Instagram."""
    session.pop('instagram_username', None)
    session.pop('instagram_logged_in', None)
    
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })


@bp.route('/status', methods=['GET'])
def status():
    """Check Instagram login status."""
    logged_in = session.get('instagram_logged_in', False)
    username = session.get('instagram_username', None)
    
    if logged_in and username:
        # Verify session is still valid
        instagram_service = InstagramService()
        try:
            instagram_service.loader.load_session_from_file(username, f"session-{username}")
            is_valid = instagram_service.is_logged_in()
        except:
            is_valid = False
            
        if not is_valid:
            session.pop('instagram_username', None)
            session.pop('instagram_logged_in', None)
            logged_in = False
            username = None
    
    return jsonify({
        'logged_in': logged_in,
        'username': username
    })
