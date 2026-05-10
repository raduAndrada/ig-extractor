"""Database migration utilities and FTS5 search setup."""
from app import db
import logging

logger = logging.getLogger(__name__)


def create_fts_table():
    """Create FTS5 virtual table for full-text search.
    
    This creates a virtual table that indexes post captions and owner usernames
    for lightning-fast full-text search.
    """
    try:
        # Check if FTS table already exists
        result = db.session.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='posts_fts'"
        ).fetchone()
        
        if result:
            logger.info("FTS table already exists")
            return True
        
        # Create FTS5 virtual table
        db.session.execute("""
            CREATE VIRTUAL TABLE posts_fts USING fts5(
                post_id UNINDEXED,
                caption,
                owner_username,
                content='posts',
                content_rowid='id'
            )
        """)
        
        # Create triggers to keep FTS table in sync
        
        # INSERT trigger
        db.session.execute("""
            CREATE TRIGGER posts_fts_insert AFTER INSERT ON posts BEGIN
                INSERT INTO posts_fts(rowid, post_id, caption, owner_username)
                VALUES (new.id, new.id, new.caption, new.owner_username);
            END;
        """)
        
        # UPDATE trigger
        db.session.execute("""
            CREATE TRIGGER posts_fts_update AFTER UPDATE ON posts BEGIN
                UPDATE posts_fts 
                SET caption = new.caption, owner_username = new.owner_username
                WHERE rowid = old.id;
            END;
        """)
        
        # DELETE trigger
        db.session.execute("""
            CREATE TRIGGER posts_fts_delete AFTER DELETE ON posts BEGIN
                DELETE FROM posts_fts WHERE rowid = old.id;
            END;
        """)
        
        # Populate with existing data
        db.session.execute("""
            INSERT INTO posts_fts(rowid, post_id, caption, owner_username)
            SELECT id, id, caption, owner_username FROM posts
        """)
        
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
        db.session.execute("DROP TRIGGER IF EXISTS posts_fts_insert")
        db.session.execute("DROP TRIGGER IF EXISTS posts_fts_update")
        db.session.execute("DROP TRIGGER IF EXISTS posts_fts_delete")
        db.session.execute("DROP TABLE IF EXISTS posts_fts")
        db.session.commit()
        logger.info("FTS table and triggers dropped")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to drop FTS table: {e}")
        return False


def rebuild_fts_index():
    """Rebuild the FTS index from scratch.
    
    Useful if the index gets out of sync or corrupted.
    """
    try:
        # Clear existing FTS data
        db.session.execute("DELETE FROM posts_fts")
        
        # Repopulate
        db.session.execute("""
            INSERT INTO posts_fts(rowid, post_id, caption, owner_username)
            SELECT id, id, caption, owner_username FROM posts
        """)
        
        db.session.commit()
        logger.info("FTS index rebuilt successfully")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to rebuild FTS index: {e}")
        return False


def search_posts_fts(query, limit=50):
    """Search posts using FTS5.
    
    Args:
        query: Search query string
        limit: Maximum number of results
        
    Returns:
        List of post IDs matching the query, ordered by relevance
    """
    try:
        # Use FTS5 MATCH for full-text search
        # The '-rank' orders by relevance (best matches first)
        result = db.session.execute(
            """
            SELECT post_id, rank 
            FROM posts_fts 
            WHERE posts_fts MATCH :query 
            ORDER BY rank 
            LIMIT :limit
            """,
            {'query': query, 'limit': limit}
        ).fetchall()
        
        return [row[0] for row in result]
        
    except Exception as e:
        logger.error(f"FTS search failed: {e}")
        return []


def get_fts_stats():
    """Get statistics about the FTS index.
    
    Returns:
        dict: Statistics including index size and row count
    """
    try:
        count = db.session.execute(
            "SELECT COUNT(*) FROM posts_fts"
        ).scalar()
        
        return {
            'indexed_posts': count,
            'status': 'active'
        }
    except Exception as e:
        logger.error(f"Failed to get FTS stats: {e}")
        return {
            'indexed_posts': 0,
            'status': 'error'
        }
