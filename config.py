"""Application configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
basedir = Path(__file__).parent.absolute()
load_dotenv(basedir / '.env')


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{basedir}/data/instagram_organizer.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Paths
    BASE_DIR = basedir
    DATA_DIR = basedir / 'data'
    THUMBNAIL_DIR = basedir / 'data' / 'thumbnails'
    
    # Instagram
    INSTAGRAM_USERNAME = os.environ.get('INSTAGRAM_USERNAME', '')
    INSTAGRAM_PASSWORD = os.environ.get('INSTAGRAM_PASSWORD', '')
    MAX_POSTS_PER_FETCH = int(os.environ.get('MAX_POSTS_PER_FETCH', 50))
    FETCH_DELAY_SECONDS = int(os.environ.get('FETCH_DELAY_SECONDS', 5))
    
    # Media
    THUMBNAIL_SIZE = int(os.environ.get('THUMBNAIL_SIZE', 400))
    
    # AI Configuration
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'openai')  # 'openai' or 'local'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    MODEL_NAME = os.environ.get('MODEL_NAME', 'openai/clip-vit-base-patch32')
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    THUMBNAIL_DIR.mkdir(exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
