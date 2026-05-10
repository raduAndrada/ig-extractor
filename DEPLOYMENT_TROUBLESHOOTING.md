# Deployment Troubleshooting Guide

## ❌ Error: "Getting requirements to build wheel ... KeyError: '__version__'"

### 🔍 Problem
This error occurs when:
1. Using Python 3.13 (too new, some packages incompatible)
2. Missing build tools for compiled dependencies
3. Package version conflicts

### ✅ Solutions

#### Solution 1: Use Python 3.10 (RECOMMENDED for PythonAnywhere)

**On PythonAnywhere:**
1. When creating web app, select **Python 3.10** (not 3.11 or 3.13)
2. Use `requirements-pythonanywhere.txt` instead of `requirements.txt`

```bash
# In PythonAnywhere Bash console
pip3.10 install --user -r requirements-pythonanywhere.txt
```

#### Solution 2: Install Without Versions (Let pip choose)

**If still failing:**
```bash
# Install without specific versions
pip3 install --user Flask Flask-SQLAlchemy instaloader Pillow python-dotenv
```

#### Solution 3: Install One by One

**If batch install fails:**
```bash
pip3 install --user Flask==3.0.0
pip3 install --user Flask-SQLAlchemy==3.1.1
pip3 install --user instaloader
pip3 install --user Pillow
pip3 install --user python-dotenv
pip3 install --user openai  # optional
pip3 install --user tqdm
pip3 install --user python-dateutil
```

---

## 🐛 Common Deployment Issues

### Issue 1: ModuleNotFoundError

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Fix:**
```bash
# Make sure virtual environment active OR
# Use --user flag for PythonAnywhere
pip3 install --user -r requirements-pythonanywhere.txt
```

### Issue 2: Permission Denied

**Error:** `PermissionError: [Errno 13] Permission denied`

**Fix:**
```bash
# On PythonAnywhere, always use --user flag
pip3 install --user package-name
```

### Issue 3: Database Not Found

**Error:** `sqlite3.OperationalError: unable to open database file`

**Fix:**
```bash
# Create data directory
mkdir -p /home/yourusername/data/thumbnails

# Set permissions
chmod 755 /home/yourusername/data
```

### Issue 4: Import Error in WSGI

**Error:** `ImportError: No module named 'run'`

**Fix - Check WSGI Configuration:**
```python
import sys
import os

# IMPORTANT: Update with YOUR username
project_home = '/home/yourusername'  # ← Change this!
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from run import app as application
```

### Issue 5: Instagram Login Fails

**Error:** `LoginRequiredException` or session errors

**Fix:**
1. **Use 2FA** - More reliable for cloud deployments
2. **Login from local first** - Upload `session-username` file
3. **Alternative:** Manually upload posts data

### Issue 6: Thumbnails Not Showing

**Error:** 404 errors for `/data/thumbnails/*.jpg`

**Fix:**
```bash
# Create thumbnails directory
mkdir -p /home/yourusername/data/thumbnails

# Check permissions
ls -la /home/yourusername/data/
```

---

## 📋 Pre-Deployment Checklist

### ✅ Before Deploying to PythonAnywhere

- [ ] Python version: **3.10** (not 3.11 or 3.13)
- [ ] Use: `requirements-pythonanywhere.txt`
- [ ] Install with: `pip3 install --user -r requirements-pythonanywhere.txt`
- [ ] Create directories: `mkdir -p data/thumbnails`
- [ ] Update WSGI config with your username
- [ ] Set SECRET_KEY in WSGI config
- [ ] Check file paths are absolute: `/home/yourusername/...`

### ✅ Before Deploying to Render/Railway

- [ ] Push code to GitHub
- [ ] Update `runtime.txt` to `python-3.11.0` (not 3.13)
- [ ] Use: `requirements-deploy.txt` or `requirements.txt`
- [ ] Set environment variables (SECRET_KEY, FLASK_ENV)
- [ ] Enable persistent disk for database
- [ ] Add `.gitignore` entries for sensitive files

---

## 🔧 PythonAnywhere Specific Fixes

### Fix 1: Use Correct Python Version

```bash
# Check Python version
python3 --version

# If 3.13, use 3.10 explicitly
python3.10 -m pip install --user package-name
```

### Fix 2: WSGI Configuration Template

**Working WSGI config for PythonAnywhere:**

```python
# /var/www/yourusername_pythonanywhere_com_wsgi.py
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['SECRET_KEY'] = 'your-secret-key-change-this-randomly-generated'
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from run import app as application

# Optional: Set up logging
import logging
logging.basicConfig(level=logging.INFO)
```

### Fix 3: Static Files Configuration

**On PythonAnywhere Web tab:**
- URL: `/static/`
- Directory: `/home/yourusername/app/static/`

**For thumbnails:**
- URL: `/data/thumbnails/`
- Directory: `/home/yourusername/data/thumbnails/`

---

## 🚀 Alternative: Minimal Installation

If all else fails, install ONLY what's needed:

```bash
# Absolute minimum to run the app
pip3 install --user Flask
pip3 install --user Flask-SQLAlchemy
pip3 install --user instaloader
pip3 install --user Pillow
```

Then test if app runs:
```bash
python3 run.py
```

If it works, add others one by one.

---

## 📱 Can't Deploy? Local Network Alternative

If deployment keeps failing, access from phone via local network:

**On your Mac:**
```bash
# Find your Mac's IP address
ifconfig | grep "inet " | grep -v 127.0.0.1

# Run app on network
python3 run.py
# Flask will show: Running on http://0.0.0.0:5000
```

**On your phone:**
1. Connect to **same WiFi** as Mac
2. Open browser
3. Go to: `http://YOUR-MAC-IP:5000`
   - Example: `http://192.168.1.147:5000`

This works while both devices on same WiFi!

---

## 🆘 Still Stuck?

### Option 1: Use Replit (No Installation Needed!)

1. Go to https://replit.com
2. Create new Repl → **Import from GitHub**
3. Paste your GitHub URL (or upload folder)
4. Click **Run**
5. Share URL - works on phone!

**Replit installs everything automatically!** ✨

### Option 2: Use Docker (Advanced)

```bash
# In project directory
docker build -t ig-extractor .
docker run -p 5000:5000 ig-extractor
```

### Option 3: Simplify Dependencies

Comment out optional packages in requirements:
```
# openai==1.3.0  # Optional - only if using AI
# Flask-Migrate==4.0.5  # Optional - only for migrations
```

---

## 📧 Get Help

**PythonAnywhere Forums:**
- https://www.pythonanywhere.com/forums/

**Include in your question:**
1. Python version: `python3 --version`
2. Full error message
3. Which file you're installing from
4. Installation command you used

**Example:**
```
Error installing on PythonAnywhere
Python: 3.10
Command: pip3 install --user -r requirements.txt
Error: [paste full error]
```

---

## ✅ Working Configuration (Verified)

**This setup WORKS on PythonAnywhere:**

```bash
# 1. Python version
Python 3.10

# 2. Install command
pip3 install --user Flask Flask-SQLAlchemy instaloader Pillow python-dotenv

# 3. WSGI config
import sys
sys.path.insert(0, '/home/yourusername')
from run import app as application

# 4. Web app settings
- Python version: 3.10
- Source code: /home/yourusername
- Working directory: /home/yourusername
```

**This configuration has been tested and works!** 🎉
