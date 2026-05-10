"""Tag model for post tagging."""
from datetime import datetime
from app import db


class Tag(db.Model):
    """Tag model for post organization."""
    
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    name = db.Column(db.String(100), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Unique constraint: one tag name per user
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='_user_tag_uc'),
    )
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    
    def to_dict(self):
        """Convert tag to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'post_count': self.posts.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Association table for post-tag many-to-many relationship
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)
