"""Post model representing Instagram saved posts."""
from datetime import datetime
from app import db


class Post(db.Model):
    """Instagram post model."""
    
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    instagram_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    shortcode = db.Column(db.String(50), unique=True, nullable=False, index=True)
    caption = db.Column(db.Text)
    post_url = db.Column(db.String(500))
    media_type = db.Column(db.String(20))  # 'photo', 'video', 'carousel'
    thumbnail_path = db.Column(db.String(500))
    owner_username = db.Column(db.String(100), index=True)
    owner_fullname = db.Column(db.String(200))
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    saved_at = db.Column(db.DateTime, nullable=False, index=True)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Recipe-specific fields
    recipe_ingredients = db.Column(db.Text)  # JSON array of ingredients
    recipe_directions = db.Column(db.Text)   # JSON array of directions/steps
    is_recipe = db.Column(db.Boolean, default=False, index=True)
    
    # Relationships
    categories = db.relationship(
        'Category',
        secondary='post_categories',
        backref=db.backref('posts', lazy='dynamic')
    )
    tags = db.relationship(
        'Tag',
        secondary='post_tags',
        backref=db.backref('posts', lazy='dynamic')
    )
    
    def __repr__(self):
        return f'<Post {self.shortcode}>'
    
    def to_dict(self):
        """Convert post to dictionary."""
        import json
        
        return {
            'id': self.id,
            'instagram_id': self.instagram_id,
            'shortcode': self.shortcode,
            'caption': self.caption,
            'post_url': self.post_url,
            'media_type': self.media_type,
            'thumbnail_path': self.thumbnail_path,
            'owner_username': self.owner_username,
            'owner_fullname': self.owner_fullname,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'saved_at': self.saved_at.isoformat() if self.saved_at else None,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
            'is_recipe': self.is_recipe,
            'recipe_ingredients': json.loads(self.recipe_ingredients) if self.recipe_ingredients else None,
            'recipe_directions': json.loads(self.recipe_directions) if self.recipe_directions else None,
            'categories': [cat.to_dict() for cat in self.categories],
            'tags': [tag.to_dict() for tag in self.tags]
        }
