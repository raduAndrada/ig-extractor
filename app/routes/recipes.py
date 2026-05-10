"""Recipe routes blueprint."""
from flask import Blueprint, render_template, jsonify, request
from app import db
from app.models.post import Post
from app.services.recipe_parser import RecipeParser
import json
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('recipes', __name__, url_prefix='/recipes')


@bp.route('/parse/<int:post_id>', methods=['POST'])
def parse_recipe(post_id):
    """Parse recipe from post caption."""
    post = Post.query.get_or_404(post_id)
    
    if not post.caption:
        return jsonify({
            'success': False,
            'error': 'Post has no caption to parse'
        }), 400
    
    try:
        parser = RecipeParser()
        result = parser.parse_recipe(post.caption)
        
        if result['is_recipe']:
            # Update post with recipe data
            post.is_recipe = True
            post.recipe_ingredients = json.dumps(result['ingredients'])
            post.recipe_directions = json.dumps(result['directions'])
            db.session.commit()
            
            return jsonify({
                'success': True,
                'is_recipe': True,
                'ingredients': result['ingredients'],
                'directions': result['directions'],
                'message': f"Found {len(result['ingredients'])} ingredients and {len(result['directions'])} steps"
            })
        else:
            return jsonify({
                'success': True,
                'is_recipe': False,
                'message': 'No recipe detected in caption'
            })
            
    except Exception as e:
        logger.error(f"Recipe parsing failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/batch-parse', methods=['POST'])
def batch_parse():
    """Parse recipes for multiple posts."""
    data = request.get_json()
    post_ids = data.get('post_ids', [])
    
    if not post_ids:
        # Parse all uncategorized food-related posts
        posts = Post.query.filter(
            Post.is_recipe == False,
            Post.caption.isnot(None)
        ).limit(100).all()
    else:
        posts = Post.query.filter(Post.id.in_(post_ids)).all()
    
    parser = RecipeParser()
    results = {
        'total': len(posts),
        'recipes_found': 0,
        'failed': 0
    }
    
    for post in posts:
        try:
            result = parser.parse_recipe(post.caption)
            
            if result['is_recipe']:
                post.is_recipe = True
                post.recipe_ingredients = json.dumps(result['ingredients'])
                post.recipe_directions = json.dumps(result['directions'])
                results['recipes_found'] += 1
        except Exception as e:
            logger.error(f"Failed to parse post {post.id}: {e}")
            results['failed'] += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'results': results
    })


@bp.route('/update/<int:post_id>', methods=['POST'])
def update_recipe(post_id):
    """Manually update recipe ingredients and directions."""
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    
    try:
        ingredients = data.get('ingredients', [])
        directions = data.get('directions', [])
        
        post.is_recipe = True
        post.recipe_ingredients = json.dumps(ingredients)
        post.recipe_directions = json.dumps(directions)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Recipe updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Recipe update failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/list')
def list_recipes():
    """List all posts marked as recipes."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    posts = Post.query.filter_by(is_recipe=True).order_by(
        Post.saved_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('recipes/list.html', posts=posts)


@bp.route('/<int:post_id>')
def view_recipe(post_id):
    """View recipe detail."""
    post = Post.query.get_or_404(post_id)
    
    if not post.is_recipe:
        return jsonify({
            'error': 'Post is not marked as a recipe'
        }), 404
    
    ingredients = json.loads(post.recipe_ingredients) if post.recipe_ingredients else []
    directions = json.loads(post.recipe_directions) if post.recipe_directions else []
    
    return render_template('recipes/detail.html',
                         post=post,
                         ingredients=ingredients,
                         directions=directions)
