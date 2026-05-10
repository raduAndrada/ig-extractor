"""Database migration utilities and FTS5 search setup."""
from app import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


def create_fts_table():
    """Create FTS5 virtual table for full-text search."""
    try:
        # Check if FTS table already exists
        result = db.session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='posts_fts'")
        ).fetchone()
        
        if result:
            logger.info("FTS table already exists")
            return True
        
        # Create FTS5 virtual table
        db.session.execute(text("""
            CREATE VIRTUAL TABLE posts_fts USING fts5(
                post_id UNINDEXED,
                caption,
                owner_username,
                content='posts',
                content_rowid='id'
            )
        """))
        
        # Create triggers
        db.session.execute(text("""
            CREATE TRIGGER posts_fts_insert AFTER INSERT ON posts BEGIN
                INSERT INTO posts_fts(rowid, post_id, caption, owner_username)
                VALUES (new.id, new.id, new.caption, new.owner_username);
            END;
        """))
        
        db.session.execute(text("""
            CREATE TRIGGER posts_fts_update AFTER UPDATE ON posts BEGIN
                UPDATE posts_fts 
                SET caption = new.caption, owner_username = new.owner_username
                WHERE rowid = old.id;
            END;
        """))
        
        db.session.execute(text("""
            CREATE TRIGGER posts_fts_delete AFTER DELETE ON posts BEGIN
                DELETE FROM posts_fts WHERE rowid = old.id;
            END;
        """))
        
        # Populate with existing data
        db.session.execute(text("""
            INSERT INTO posts_fts(rowid, post_id, caption, owner_username)
            SELECT id, id, caption, owner_username FROM posts
        """))
        
        db.session.commit()
        logger.info("FTS5 table and triggers created successfully")
        return True
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create FTS table: {e}")
        return False


def drop_fts_table():
    """Drop FTS5 table and triggers."""
    try:
        db.session.execute(text("DROP TRIGGER IF EXISTS posts_fts_insert"))
        db.session.execute(text("DROP TRIGGER IF EXISTS posts_fts_update"))
        db.session.execute(text("DROP TRIGGER IF EXISTS posts_fts_delete"))
        db.session.execute(text("DROP TABLE IF EXISTS posts_fts"))
        db.session.commit()
        logger.info("FTS table and triggers dropped")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to drop FTS table: {e}")
        return False


def rebuild_fts_index():
    """Rebuild FTS5 index from scratch."""
    try:
        db.session.execute(text("DELETE FROM posts_fts"))
        db.session.execute(text("""
            INSERT INTO posts_fts(rowid, post_id, caption, owner_username)
            SELECT id, id, caption, owner_username FROM posts
        """))
        db.session.commit()
        logger.info("FTS index rebuilt successfully")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to rebuild FTS index: {e}")
        return False


def search_posts_fts(query, limit=50):
    """Search posts using FTS5."""
    try:
        result = db.session.execute(
            text("""
                SELECT rowid 
                FROM posts_fts 
                WHERE posts_fts MATCH :query 
                ORDER BY rank 
                LIMIT :limit
            """),
            {'query': query, 'limit': limit}
        ).fetchall()
        
        return [row[0] for row in result]
        
    except Exception as e:
        logger.error(f"FTS search failed: {e}")
        return []


def get_fts_stats():
    """Get statistics about the FTS index."""
    try:
        count = db.session.execute(
            text("SELECT COUNT(*) FROM posts_fts")
        ).fetchone()[0]
        
        return {
            'row_count': count,
            'enabled': True
        }
    except Exception as e:
        logger.error(f"Failed to get FTS stats: {e}")
        return {
            'row_count': 0,
            'enabled': False,
            'error': str(e)
        }
