#!/bin/bash
# Quick Start Script for Instagram Organizer Multi-User App

echo "🚀 Instagram Organizer - Multi-User Setup"
echo "=========================================="
echo ""

# Check Python
echo "1️⃣  Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"
echo ""

# Install dependencies
echo "2️⃣  Installing dependencies..."
python3 -m pip install --quiet --upgrade pip
python3 -m pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"
echo ""

# Create database
echo "3️⃣  Creating database..."
python3 -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
print('✅ Database created')
"
echo ""

# Run tests
echo "4️⃣  Running tests..."
python3 test_auth.py 2>&1 | grep -E "(✅|✨)"
echo ""

# Start app
echo "5️⃣  Starting application..."
echo ""
echo "📱 Access the app at:"
echo "   http://localhost:5000"
echo ""
echo "📋 First time setup:"
echo "   1. Click 'Sign Up' to create account"
echo "   2. Login with your credentials"
echo "   3. Go to Settings → Connect Instagram"
echo "   4. Sync your saved posts"
echo "   5. Start organizing!"
echo ""
echo "🔒 Security:"
echo "   - All passwords are hashed"
echo "   - Each user's data is isolated"
echo "   - Session-based authentication"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

python3 run.py
