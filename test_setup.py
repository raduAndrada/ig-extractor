#!/usr/bin/env python3
"""Test script to verify the application setup."""
import sys
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    try:
        import flask
        print("✓ Flask")
        from flask_sqlalchemy import SQLAlchemy
        print("✓ Flask-SQLAlchemy")
        from flask_migrate import Migrate
        print("✓ Flask-Migrate")
        import instaloader
        print("✓ Instaloader")
        from PIL import Image
        print("✓ Pillow")
        from dotenv import load_dotenv
        print("✓ python-dotenv")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_structure():
    """Test that the project structure is correct."""
    print("\nTesting project structure...")
    required_dirs = [
        "app",
        "app/models",
        "app/routes",
        "app/services",
        "app/static/css",
        "app/static/js",
        "app/templates",
        "data",
        "data/thumbnails",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ (missing)")
            all_exist = False
    
    return all_exist


def test_app_creation():
    """Test that the Flask app can be created."""
    print("\nTesting app creation...")
    try:
        from app import create_app
        app = create_app('development')
        print("✓ App created successfully")
        
        with app.app_context():
            from app import db
            print("✓ Database initialized")
            
            # Test models
            from app.models import Post, Category, Tag
            print("✓ Models imported")
        
        return True
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Instagram Organizer - Installation Test")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Project Structure", test_structure()))
    results.append(("App Creation", test_app_creation()))
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All tests passed! You're ready to run the application.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure")
        print("2. Run: python run.py")
        print("3. Open: http://localhost:5000")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("\nTry running: pip install -r requirements.txt")
        return 1


if __name__ == '__main__':
    sys.exit(main())
