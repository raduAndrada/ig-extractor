"""Database migration utilities and full-text search setup."""
from app import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


def is_postgresql():
    """Check if using PostgreSQL."""
    return db.engine.url.drivername == 'postgresql'


def create_fts_table():
    """Create full-text search table/index for PostgreSQL or SQLite."""
    try:
        if is_postgresql():
            return create_postgres_fts()
        else:
            return create_sqlite_fts()
    except Exception as e:
        logger.error(f"Failed to create FTS: {e}")
        return False


def create_sqlite_fts():
    """Create SQLite FTS5 virtual table."""
    try:
        # Check if FTS table already exists
        result = db.session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='posts_fts'")
        ).fetchone()
        
        if result:
            logger.info("SQLite FTS5 table already exists")
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
        logger.info("SQLite FTS5 table and triggers created successfully")
        return True
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create SQLite FTS table: {e}")
        return False


def create_postgres_fts():
    """Create PostgreSQL full-text search indexes."""
    try:
        # Check if index already exists
        result = db.session.execute(text("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'posts' AND indexname = 'posts_fts_idx'
        """)).fetchone()
        
        if result:
            logger.info("PostgreSQL FTS index already exists")
            return True
        
        # Create GIN index for full-text search
        # Combines caption and owner_username into searchable text
        db.session.execute(text("""
            CREATE INDEX posts_fts_idx ON posts 
            USING GIN (to_tsvector('english', 
                COALESCE(caption, '') || ' ' || COALESCE(owner_username, '')
            ))
        """))
        
        db.session.commit()
        logger.info("PostgreSQL FTS index created successfully")
        return True
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create PostgreSQL FTS index: {e}")
        return False


def drop_fts_table():
    """Drop full-text search table/index."""
    try:
        if is_postgresql():
            db.session.execute(text("DROP INDEX IF EXISTS posts_fts_idx"))
        else:
            db.session.execute(text("DROP TRIGGER IF EXISTS posts_fts_insert"))
            db.session.execute(text("DROP TRIGGER IF EXISTS posts_fts_update"))
            db.session.execute(text("DROP TRIGGER IF EXISTS posts_fts_delete"))
            db.session.execute(text("DROP TABLE IF EXISTS posts_fts"))
        
        db.session.commit()
        logger.info("FTS table/index dropped")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to drop FTS: {e}")
        return False


def rebuild_fts_index():
    """Rebuild full-text search index from scratch."""
    try:
        if is_postgresql():
            # For PostgreSQL, just reindex
            db.session.execute(text("REINDEX INDEX posts_fts_idx"))
        else:
            # For SQLite, clear and repopulate
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
    """Search posts using full-text search (PostgreSQL or SQLite)."""
    try:
        if is_postgresql():
            return search_posts_postgres(query, limit)
        else:
            return search_posts_sqlite(query, limit)
    except Exception as e:
        logger.error(f"FTS search failed: {e}")
        return []


def search_posts_sqlite(query, limit=50):
    """Search posts using SQLite FTS5."""
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
        logger.error(f"SQLite FTS search failed: {e}")
        return []


def search_posts_postgres(query, limit=50):
    """Search posts using PostgreSQL full-text search."""
    try:
        result = db.session.execute(
            text("""
                SELECT id 
                FROM posts 
                WHERE to_tsvector('english', 
                    COALESCE(caption, '') || ' ' || COALESCE(owner_username, '')
                ) @@ plainto_tsquery('english', :query)
                ORDER BY ts_rank(
                    to_tsvector('english', 
                        COALESCE(caption, '') || ' ' || COALESCE(owner_username, '')
                    ),
                    plainto_tsquery('english', :query)
                ) DESC
                LIMIT :limit
            """),
            {'query': query, 'limit': limit}
        ).fetchall()
        
        return [row[0] for row in result]
        
    except Exception as e:
        logger.error(f"PostgreSQL FTS search failed: {e}")
        return []


def get_fts_stats():
    """Get statistics about the FTS index."""
    try:
        if is_postgresql():
            # Check if index exists
            result = db.session.execute(text("""
                SELECT indexname FROM pg_indexes 
                WHERE tablename = 'posts' AND indexname = 'posts_fts_idx'
            """)).fetchone()
            
            return {
                'enabled': bool(result),
                'type': 'postgresql',
                'index_name': 'posts_fts_idx'
            }
        else:
            count = db.session.execute(
                text("SELECT COUNT(*) FROM posts_fts")
            ).fetchone()[0]
            
            return {
                'row_count': count,
                'enabled': True,
                'type': 'sqlite'
            }
    except Exception as e:
        logger.error(f"Failed to get FTS stats: {e}")
        return {
            'enabled': False,
            'error': str(e)
        }
