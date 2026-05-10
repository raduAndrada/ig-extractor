#!/bin/bash

echo "🚀 Instagram Organizer - Quick Deploy to PythonAnywhere"
echo "========================================================="
echo ""

# Create deployment package
echo "📦 Creating deployment package..."
cd "$(dirname "$0")"

# Create temporary directory
mkdir -p deploy_temp
cp -r app deploy_temp/
cp -r data deploy_temp/
cp *.py deploy_temp/
cp requirements.txt deploy_temp/
cp config.py deploy_temp/
cp -r app/static deploy_temp/app/
cp -r app/templates deploy_temp/app/

# Create data directories in temp
mkdir -p deploy_temp/data/thumbnails

# Create archive
echo "📦 Compressing files..."
tar -czf instagram-organizer-deploy.tar.gz -C deploy_temp . \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='*.db' \
  --exclude='session-*' \
  --exclude='*.log'

# Clean up
rm -rf deploy_temp

echo "✅ Deployment package created: instagram-organizer-deploy.tar.gz"
echo ""
echo "📱 Next steps for PythonAnywhere:"
echo "1. Go to https://www.pythonanywhere.com"
echo "2. Sign up for free account"
echo "3. Go to Files tab"
echo "4. Upload instagram-organizer-deploy.tar.gz"
echo "5. Open Bash console and run:"
echo "   tar -xzf instagram-organizer-deploy.tar.gz"
echo "   pip3 install --user -r requirements.txt"
echo "6. Go to Web tab → Add new web app"
echo "7. Choose Manual configuration → Python 3.10"
echo "8. Set:"
echo "   Source code: /home/yourusername"
echo "   Working directory: /home/yourusername"
echo "   WSGI file: Edit and point to run.py"
echo "9. Reload web app"
echo "10. Access: https://yourusername.pythonanywhere.com"
echo ""
echo "🎉 Done! Your app will be live!"
