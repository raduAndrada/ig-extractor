# Free Deployment Options for Instagram Organizer

Access your app from anywhere - phone, tablet, computer!

## 🆓 Best Free Hosting Services

### ⭐ Option 1: PythonAnywhere (Recommended)
**Best for:** Flask apps with file storage  
**Free tier:** 1 web app, 512MB storage, daily usage limits  
**Pros:** Easy setup, persistent storage, Python-focused  
**Cons:** Limited to 100k hits/day

**Setup Guide:**

1. **Create Account**
   - Go to https://www.pythonanywhere.com
   - Sign up for free account
   - Confirm email

2. **Upload Your Code**
   ```bash
   # On your Mac, create a zip file
   cd /Users/pl80an/PycharmProjects
   zip -r ig-extractor.zip ig-extractor/ -x "*.pyc" "*__pycache__*" "*.git*" "*session-*" "*.venv*"
   ```
   
   - In PythonAnywhere: Files → Upload file
   - Upload the zip
   - Open Bash console: `unzip ig-extractor.zip`

3. **Install Dependencies**
   ```bash
   # In PythonAnywhere Bash console
   cd ig-extractor
   pip3 install --user -r requirements.txt
   ```

4. **Configure Web App**
   - Go to Web tab
   - Add a new web app
   - Choose Flask
   - Python version: 3.10
   - Path to app: `/home/yourusername/ig-extractor/run.py`
   - Working directory: `/home/yourusername/ig-extractor`

5. **Set Environment Variables**
   - Go to Web tab
   - Add to WSGI configuration file:
   ```python
   import os
   os.environ['SECRET_KEY'] = 'your-secret-key-here'
   ```

6. **Reload and Access**
   - Click green "Reload" button
   - Visit: `https://yourusername.pythonanywhere.com`

**Phone Access:** Just open that URL on your phone! ✨

---

### 🚀 Option 2: Render.com
**Best for:** Modern deployment, auto-scaling  
**Free tier:** 750 hours/month, spins down after 15min inactivity  
**Pros:** Modern platform, GitHub integration, SSL included  
**Cons:** Slower cold starts, limited hours

**Setup Guide:**

1. **Prepare for Deployment**

Create `render.yaml`:
```yaml
services:
  - type: web
    name: instagram-organizer
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn run:app
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: FLASK_ENV
        value: production
```

Add to `requirements.txt`:
```
gunicorn==21.2.0
```

2. **Push to GitHub**
   ```bash
   cd /Users/pl80an/PycharmProjects/ig-extractor
   git init
   git add .
   git commit -m "Initial commit"
   gh repo create ig-extractor --public --source=. --push
   ```

3. **Deploy on Render**
   - Go to https://render.com
   - Sign up (use GitHub)
   - New → Web Service
   - Connect your repository
   - Render auto-detects settings
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment

4. **Access**
   - URL: `https://instagram-organizer.onrender.com`
   - Open on phone browser!

**Note:** Free tier sleeps after 15 minutes. First request after sleep takes ~30 seconds to wake up.

---

### 💻 Option 3: Railway.app
**Best for:** Quick deploys, generous free tier  
**Free tier:** $5 credit/month  
**Pros:** Fast deployment, good free tier  
**Cons:** Credit system (but $5 usually enough)

**Setup:**

1. **Push to GitHub** (same as Render)

2. **Deploy**
   - Go to https://railway.app
   - Sign up with GitHub
   - New Project → Deploy from GitHub
   - Select repository
   - Add variables:
     - `SECRET_KEY` = your-key
     - `PORT` = 5000
   - Deploy!

3. **Generate Domain**
   - Settings → Generate Domain
   - Access from anywhere!

---

### 🌐 Option 4: Fly.io
**Best for:** Global edge network  
**Free tier:** 3 shared VMs, 3GB storage  
**Pros:** Fast globally, Docker-based  
**Cons:** Requires Docker knowledge

**Setup:**

1. **Install Fly CLI**
   ```bash
   brew install flyctl
   flyctl auth login
   ```

2. **Initialize App**
   ```bash
   cd /Users/pl80an/PycharmProjects/ig-extractor
   flyctl launch
   # Answer prompts:
   # - App name: ig-extractor-[yourname]
   # - Region: Choose closest
   # - PostgreSQL: No
   # - Redis: No
   ```

3. **Deploy**
   ```bash
   flyctl deploy
   flyctl open
   ```

---

### 📱 Option 5: Replit (Easiest!)
**Best for:** Beginners, quick testing  
**Free tier:** Always-on with basic plan  
**Pros:** Zero config, browser-based IDE  
**Cons:** Public by default, slower

**Setup:**

1. Go to https://replit.com
2. Sign up
3. Create New Repl → Import from GitHub
4. Paste GitHub URL or upload zip
5. Click "Run"
6. Share URL with yourself!

---

## 📊 Comparison Table

| Service | Setup Time | Persistent Storage | Auto-Sleep | Best For |
|---------|-----------|-------------------|-----------|----------|
| **PythonAnywhere** | 15 min | ✅ Yes | ❌ No | Production use |
| **Render.com** | 10 min | ⚠️ Limited | ✅ Yes (15min) | GitHub workflow |
| **Railway.app** | 5 min | ✅ Yes | ❌ No | Quick deploys |
| **Fly.io** | 20 min | ✅ Yes | ❌ No | Advanced users |
| **Replit** | 2 min | ⚠️ Limited | ⚠️ Sometimes | Testing |

## 🎯 My Recommendation

**For your use case (Instagram recipes, phone access):**

### 🥇 **PythonAnywhere** - Best Choice!

**Why:**
- ✅ Your SQLite database persists
- ✅ Thumbnail images saved permanently
- ✅ Instagram sessions don't expire
- ✅ No cold starts (app always ready)
- ✅ 100% free forever for basic use
- ✅ Easy to access from phone

**Quick Start:**
```bash
# 1. Create zip (exclude virtual env and cache)
cd /Users/pl80an/PycharmProjects
tar -czf ig-extractor.tar.gz ig-extractor/ \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='.venv' \
  --exclude='session-*'

# 2. Upload to PythonAnywhere via web interface
# 3. Extract and run - done in 10 minutes!
```

---

## 🔒 Security Notes for Public Deployment

Before deploying publicly:

1. **Change SECRET_KEY**
   ```python
   # Generate new secret
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Secure Instagram Sessions**
   - Don't commit session files
   - Add to `.gitignore`:
   ```
   session-*
   data/instagram_organizer.db
   data/thumbnails/
   ```

3. **Optional: Add Authentication**
   Create simple login protection:
   ```python
   # Add to run.py
   from flask_httpauth import HTTPBasicAuth
   auth = HTTPBasicAuth()
   
   @auth.verify_password
   def verify(username, password):
       return username == "your-user" and password == "your-pass"
   
   @app.before_request
   @auth.login_required
   def before_request():
       pass
   ```

4. **Limit Instagram Login**
   - Only login from trusted networks
   - Use strong Instagram password
   - Enable 2FA on Instagram

---

## 📱 Accessing from Phone

Once deployed, just:

1. **Open browser on phone**
2. **Go to your URL:**
   - PythonAnywhere: `https://yourusername.pythonanywhere.com`
   - Render: `https://your-app.onrender.com`
   - Railway: `https://your-app.railway.app`
   - Fly.io: `https://your-app.fly.dev`

3. **Add to Home Screen** (iOS/Android):
   - **iOS:** Safari → Share → Add to Home Screen
   - **Android:** Chrome → Menu → Add to Home Screen

4. **Works like native app!** 📱✨

---

## ⚡ Quick Deploy Commands

### PythonAnywhere (Recommended)
```bash
# Create zip
cd /Users/pl80an/PycharmProjects
zip -r ig-extractor.zip ig-extractor/ -x "*.pyc" "*__pycache__*" "*.venv*"

# Then:
# 1. Upload to pythonanywhere.com
# 2. Extract in bash console
# 3. pip install -r requirements.txt
# 4. Configure web app
# 5. Done!
```

### Render.com (GitHub Required)
```bash
# Push to GitHub
cd /Users/pl80an/PycharmProjects/ig-extractor
git init
git add .
git commit -m "Deploy"
gh repo create --public --source=. --push

# Then: Connect on render.com
```

### Replit (Fastest)
```bash
# Just upload folder to replit.com
# Click Run
# Done in 60 seconds!
```

---

## 💡 Pro Tips

1. **Database Backups**
   ```bash
   # Download your database regularly from PythonAnywhere
   # Files → Browse → data/ → Download instagram_organizer.db
   ```

2. **Monitor Usage**
   - PythonAnywhere: Check Web tab for hits
   - Render: Check dashboard for hours
   - Railway: Watch credit balance

3. **Update Deployment**
   ```bash
   # PythonAnywhere: Upload new code, reload web app
   # Render/Railway: Push to GitHub, auto-deploys
   ```

4. **Custom Domain** (optional)
   - Buy domain ($10/year)
   - Point to your deployment URL
   - Access via: `recipes.yourdomain.com`

---

## 🆘 Troubleshooting

**App won't start:**
- Check Python version (3.8+)
- Verify all dependencies installed
- Check logs in hosting platform

**Can't login to Instagram:**
- Instagram may block cloud IPs
- Try with VPN or different server region
- Consider manual data import

**Database resets:**
- Use PythonAnywhere (persistent storage)
- Enable disk persistence on Railway/Render

**Slow performance:**
- Free tiers have limits
- Upgrade to paid tier ($5-10/month)
- Or use PythonAnywhere (no speed limits)

---

## 🎉 Ready to Deploy!

Choose your platform and follow the guide. In 10-15 minutes you'll have your Instagram recipe organizer accessible from any device!

**My recommendation: Start with PythonAnywhere** - it's free forever and perfect for this app!

Questions? Check the docs:
- PythonAnywhere: https://help.pythonanywhere.com
- Render: https://render.com/docs
- Railway: https://docs.railway.app
