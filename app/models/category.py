"""Category model for organizing posts."""
from datetime import datetime
from app import db


class Category(db.Model):
    """Category model for organizing posts."""
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    color = db.Column(db.String(7), default='#3B82F6')  # Hex color code
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        """Convert category to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'post_count': self.posts.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Association table for post-category many-to-many relationship
post_categories = db.Table('post_categories',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True),
    db.Column('is_ai_suggested', db.Boolean, default=False),
    db.Column('confidence_score', db.Float),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)
