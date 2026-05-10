#!/usr/bin/env python3
"""Database management CLI tool."""
import sys
from app import create_app, db
from app.database_utils import (
    create_fts_table,
    drop_fts_table,
    rebuild_fts_index,
    get_fts_stats
)

app = create_app()


def setup_fts():
    """Setup FTS5 full-text search."""
    print("Setting up FTS5 full-text search...")
    with app.app_context():
        success = create_fts_table()
        if success:
            stats = get_fts_stats()
            print(f"✅ FTS5 setup complete!")
            print(f"   Indexed posts: {stats['indexed_posts']}")
            print(f"   Status: {stats['status']}")
        else:
            print("❌ FTS5 setup failed")
            return 1
    return 0


def rebuild_fts():
    """Rebuild FTS5 index."""
    print("Rebuilding FTS5 index...")
    with app.app_context():
        success = rebuild_fts_index()
        if success:
            stats = get_fts_stats()
            print(f"✅ FTS5 index rebuilt!")
            print(f"   Indexed posts: {stats['indexed_posts']}")
        else:
            print("❌ FTS5 rebuild failed")
            return 1
    return 0


def drop_fts():
    """Drop FTS5 table."""
    print("Dropping FTS5 table...")
    confirm = input("Are you sure? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cancelled")
        return 0
        
    with app.app_context():
        success = drop_fts_table()
        if success:
            print("✅ FTS5 table dropped")
        else:
            print("❌ Failed to drop FTS5 table")
            return 1
    return 0


def show_stats():
    """Show database statistics."""
    with app.app_context():
        from app.models import Post, Category, Tag
        
        total_posts = Post.query.count()
        total_categories = Category.query.count()
        total_tags = Tag.query.count()
        uncategorized = Post.query.filter(~Post.categories.any()).count()
        
        fts_stats = get_fts_stats()
        
        print("\n" + "=" * 50)
        print("DATABASE STATISTICS")
        print("=" * 50)
        print(f"Posts:          {total_posts}")
        print(f"Categories:     {total_categories}")
        print(f"Tags:           {total_tags}")
        print(f"Uncategorized:  {uncategorized}")
        print("\n" + "-" * 50)
        print("FTS5 Search Index")
        print("-" * 50)
        print(f"Indexed posts:  {fts_stats['indexed_posts']}")
        print(f"Status:         {fts_stats['status']}")
        print("=" * 50 + "\n")


def init_db():
    """Initialize database (create all tables)."""
    print("Initializing database...")
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")
        
        # Setup FTS5
        success = create_fts_table()
        if success:
            print("✅ FTS5 search enabled")
        else:
            print("⚠️  FTS5 setup skipped (may already exist)")
    return 0


def usage():
    """Print usage information."""
    print("""
Database Management Tool

Usage: python manage_db.py <command>

Commands:
    init        Initialize database (create tables + FTS5)
    setup-fts   Setup FTS5 full-text search
    rebuild-fts Rebuild FTS5 index from scratch
    drop-fts    Drop FTS5 table (careful!)
    stats       Show database statistics
    help        Show this help message

Examples:
    python manage_db.py init
    python manage_db.py stats
    python manage_db.py setup-fts
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        usage()
        return 1
    
    command = sys.argv[1].lower()
    
    commands = {
        'init': init_db,
        'setup-fts': setup_fts,
        'rebuild-fts': rebuild_fts,
        'drop-fts': drop_fts,
        'stats': show_stats,
        'help': lambda: usage() or 0
    }
    
    if command in commands:
        return commands[command]()
    else:
        print(f"Unknown command: {command}")
        usage()
        return 1


if __name__ == '__main__':
    sys.exit(main())
