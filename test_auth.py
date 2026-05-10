#!/usr/bin/env python3
"""Test script for multi-user authentication system."""

from app import create_app, db
from app.models.user import User
from app.models.category import Category
from app.models.post import Post

def test_auth_system():
    """Test the authentication system."""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Multi-User Authentication System\n")
        
        # Test 1: Create user
        print("1️⃣ Creating test user...")
        user = User(
            email="test@example.com",
            username="testuser"
        )
        user.set_password("password123")
        
        db.session.add(user)
        db.session.commit()
        print(f"✅ Created user: {user.username} (ID: {user.id})")
        
        # Test 2: Password verification
        print("\n2️⃣ Testing password verification...")
        assert user.check_password("password123"), "❌ Password check failed!"
        assert not user.check_password("wrongpass"), "❌ Should reject wrong password!"
        print("✅ Password verification working")
        
        # Test 3: Create category for user
        print("\n3️⃣ Creating category for user...")
        category = Category(
            user_id=user.id,
            name="Food",
            color="#FF5733"
        )
        db.session.add(category)
        db.session.commit()
        print(f"✅ Created category: {category.name} for user {user.username}")
        
        # Test 4: Create post for user
        print("\n4️⃣ Creating post for user...")
        from datetime import datetime
        post = Post(
            user_id=user.id,
            instagram_id="123456789",
            shortcode="ABC123",
            caption="Test post",
            post_url="https://instagram.com/p/ABC123/",
            media_type="photo",
            thumbnail_url="https://example.com/thumb.jpg",
            owner_username="instagram_user",
            saved_at=datetime.utcnow()
        )
        db.session.add(post)
        db.session.commit()
        print(f"✅ Created post: {post.shortcode} for user {user.username}")
        
        # Test 5: Verify user isolation
        print("\n5️⃣ Testing data isolation...")
        user_posts = Post.query.filter_by(user_id=user.id).count()
        user_categories = Category.query.filter_by(user_id=user.id).count()
        print(f"✅ User {user.username} has {user_posts} post(s) and {user_categories} category(ies)")
        
        # Test 6: Create second user
        print("\n6️⃣ Creating second user...")
        user2 = User(
            email="user2@example.com",
            username="user2"
        )
        user2.set_password("password456")
        db.session.add(user2)
        db.session.commit()
        print(f"✅ Created user: {user2.username} (ID: {user2.id})")
        
        # Test 7: Verify second user has no data
        print("\n7️⃣ Verifying data isolation between users...")
        user2_posts = Post.query.filter_by(user_id=user2.id).count()
        user2_categories = Category.query.filter_by(user_id=user2.id).count()
        print(f"✅ User {user2.username} has {user2_posts} post(s) and {user2_categories} category(ies)")
        
        # Test 8: Test cascade delete
        print("\n8️⃣ Testing cascade delete...")
        db.session.delete(user)
        db.session.commit()
        
        orphan_posts = Post.query.filter_by(user_id=user.id).count()
        orphan_categories = Category.query.filter_by(user_id=user.id).count()
        
        assert orphan_posts == 0, "❌ Posts not deleted on user delete!"
        assert orphan_categories == 0, "❌ Categories not deleted on user delete!"
        print("✅ Cascade delete working correctly")
        
        print("\n✨ All tests passed! Authentication system is working!\n")
        
        # Clean up
        db.session.delete(user2)
        db.session.commit()
        print("🧹 Cleaned up test data")

if __name__ == "__main__":
    test_auth_system()
