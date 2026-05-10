"""Flask application factory."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config
import logging

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_app(config_name='default'):
    """Create and configure the Flask application.
    
    Args:
        config_name: Configuration to use ('development', 'production', 'default')
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Set secret key for sessions
    app.secret_key = app.config['SECRET_KEY']
    
    # Add custom Jinja2 filters
    import json as json_module
    app.jinja_env.filters['from_json'] = lambda x: json_module.loads(x) if x else []
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Import models to ensure they're registered with SQLAlchemy
    with app.app_context():
        from app.models import User, Post, Category, Tag
        
        # Create database tables
        db.create_all()
        
        # Setup FTS5 if not already done
        try:
            from app.database_utils import create_fts_table
            create_fts_table()
        except Exception as e:
            app.logger.warning(f"FTS5 setup skipped: {e}")
    
    # Register blueprints
    from app.routes import main, posts, categories, instagram, database, ai, export, bulk, recipes, auth
    app.register_blueprint(main.bp)
    app.register_blueprint(posts.bp)
    app.register_blueprint(categories.bp)
    app.register_blueprint(instagram.bp)
    app.register_blueprint(database.bp)
    app.register_blueprint(ai.bp)
    app.register_blueprint(export.bp)
    app.register_blueprint(bulk.bp)
    app.register_blueprint(recipes.bp)
    app.register_blueprint(auth.bp)
    
    return app
