"""Categories routes blueprint."""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.category import Category

bp = Blueprint('categories', __name__, url_prefix='/categories')


@bp.route('/')
@login_required
def list_categories():
    """List all categories for current user."""
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    return render_template('categories/list.html', categories=categories)


@bp.route('/api')
@login_required
def api_list_categories():
    """API endpoint for categories list."""
    categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()
    return jsonify({
        'categories': [cat.to_dict() for cat in categories]
    })


@bp.route('/create', methods=['POST'])
@login_required
def create_category():
    """Create new category."""
    data = request.get_json()
    name = data.get('name')
    color = data.get('color', '#3B82F6')
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    category = Category(user_id=current_user.id, name=name, color=color)
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'category': category.to_dict()
    })


@bp.route('/<int:category_id>/update', methods=['PUT'])
@login_required
def update_category(category_id):
    """Update category."""
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    
    if 'name' in data:
        category.name = data['name']
    if 'color' in data:
        category.color = data['color']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'category': category.to_dict()
    })


@bp.route('/<int:category_id>/delete', methods=['DELETE'])
@login_required
def delete_category(category_id):
    """Delete category."""
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'success': True})
