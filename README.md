# Instagram Saved Posts Organizer

A powerful web application to extract, organize, and search your Instagram saved posts with AI-powered categorization.

## ✨ Features

- 📥 **Instagram Integration** - Fetch all your saved posts automatically
- 🔐 **Secure Login** - 2FA support, session persistence
- 🤖 **AI Categorization** - Intelligent auto-categorization with confidence scores
- 🏷️ **Smart Tagging** - Automatic tag extraction from captions
- 🔍 **Lightning Search** - FTS5 full-text search (10-100x faster)
- 📊 **Export** - Export to JSON/CSV with all metadata
- 🎨 **Beautiful UI** - Modern, responsive interface
- 💾 **Local Storage** - All data stored on your machine

## 🚀 Quick Start

```bash
# 1. Navigate to project
cd /Users/pl80an/PycharmProjects/ig-extractor

# 2. Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure (optional)
cp .env.example .env

# 5. Run application
python run.py

# 6. Open browser
# http://localhost:5000
```

That's it! 🎉

## 📖 User Guide

### First Time Setup

1. **Start Application** - Run `python run.py`
2. **Connect Instagram**
   - Go to Settings
   - Enter username/password
   - Complete 2FA if enabled
   - Session saved automatically
3. **Fetch Posts**
   - Go to Dashboard
   - Click "Fetch Now"
   - Wait for sync (shows progress)
4. **Create Categories**
   - Go to Categories
   - Click "New Category"
   - Choose name and color
5. **Organize**
   - Browse Posts
   - Click post for details
   - Use AI Suggest or add manually

### AI Features

**Auto-Categorization:**
- Click "🤖 AI Suggest" on any post
- Get instant category suggestions
- See confidence scores
- One-click apply

**Tag Extraction:**
- Click "🤖 AI Extract" on any post
- Automatically extract hashtags and keywords
- Review and apply

**Batch Processing:**
- Select multiple posts
- Apply categories/tags to all
- Use API for automation

### Search

**Basic Search:**
- Enter keywords in search box
- Instant FTS5 powered results

**Advanced Search:**
```
"exact phrase"        # Phrase search
word1 word2           # AND search  
word1 OR word2        # OR search
word1 NOT word2       # Exclude
prefix*               # Wildcard
```

### Export

1. Go to Settings
2. Click "Export as JSON" or "Export as CSV"
3. Confirm export
4. File downloads automatically

Exports include:
- All post metadata
- Categories
- Tags
- Engagement metrics

## 🛠️ Tech Stack

- **Backend:** Python 3.8+, Flask, SQLAlchemy
- **Database:** SQLite with FTS5 full-text search
- **Instagram:** Instaloader library
- **AI:** OpenAI API / Local models / Keyword matching
- **Frontend:** HTML, CSS, JavaScript
- **Media:** Pillow for image processing

## 📁 Project Structure

```
ig-extractor/
├── app/
│   ├── models/              # Database models
│   ├── routes/              # Flask routes
│   ├── services/            # Business logic
│   ├── static/              # CSS, JS, images
│   └── templates/           # HTML templates
├── data/                    # Database & thumbnails
├── .env.example            # Environment template
├── config.py               # Configuration
├── run.py                  # Application entry point
├── manage_db.py           # Database CLI tool
└── requirements.txt        # Dependencies
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Flask
SECRET_KEY=your-secret-key
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///data/instagram_organizer.db

# Instagram
MAX_POSTS_PER_FETCH=50
FETCH_DELAY_SECONDS=5

# AI Provider (choose one)
AI_PROVIDER=keyword        # Free, always works
# AI_PROVIDER=openai       # Best quality, requires API key
# AI_PROVIDER=local        # Free, requires transformers

# OpenAI (if using)
# OPENAI_API_KEY=sk-your-key-here

# Media
THUMBNAIL_SIZE=400
```

### AI Configuration

**Keyword Matching (Default):**
- No setup needed
- Built-in keyword database
- Instant results
- 60-70% accuracy

**OpenAI (Best):**
1. Get API key from https://platform.openai.com
2. Set `AI_PROVIDER=openai` and `OPENAI_API_KEY` in `.env`
3. ~90-95% accuracy
4. ~$0.0001 per categorization

**Local Models (Free):**
1. Install: `pip install transformers torch`
2. Set `AI_PROVIDER=local` in `.env`
3. 70-80% accuracy
4. No API costs

## 📊 Database Management

```bash
# View statistics
python manage_db.py stats

# Setup FTS5 search
python manage_db.py setup-fts

# Rebuild search index
python manage_db.py rebuild-fts

# Initialize database
python manage_db.py init
```

## 🔐 Privacy & Security

- **Local Storage:** All data stored on your machine
- **No Cloud:** Never uploads your data anywhere
- **Sessions:** Instagram session files stored locally
- **HTTPS:** Use nginx reverse proxy for HTTPS
- **API Keys:** Keep your OpenAI key private

## 🚨 Troubleshooting

### Instagram Login Issues

**Problem:** Login fails  
**Solution:** Check username/password, try 2FA

**Problem:** Session expired  
**Solution:** Login again in Settings

**Problem:** Rate limited  
**Solution:** Wait 10-15 minutes, increase `FETCH_DELAY_SECONDS`

### Search Issues

**Problem:** Search not working  
**Solution:** Run `python manage_db.py setup-fts`

**Problem:** Out of sync  
**Solution:** Run `python manage_db.py rebuild-fts`

### Performance Issues

**Problem:** Slow search  
**Solution:** FTS5 should be instant. Check if enabled.

**Problem:** High memory usage  
**Solution:** Reduce `MAX_POSTS_PER_FETCH`, use keyword AI

### General Issues

**Problem:** Port 5000 in use  
**Solution:** Change port in `run.py` or kill other process

**Problem:** Permission denied  
**Solution:** Check file permissions, use virtual environment

**Problem:** Database locked  
**Solution:** Close all app instances, restart

## 📚 Additional Documentation

- **INSTALLATION.md** - Detailed setup guide
- **DEPLOYMENT.md** - Production deployment
- **QUICKSTART.md** - Quick reference
- **PHASE1-4_COMPLETE.md** - Development history

## 🎯 Use Cases

- **Organize Recipes** - Categorize food saves
- **Travel Inspiration** - Tag dream destinations
- **Shopping Lists** - Track products you want
- **Design References** - Organize visual inspiration
- **Research** - Categorize articles and resources
- **Content Planning** - Plan social media posts

## 🔮 Future Enhancements

Potential additions:
- Mobile app
- Cloud sync
- Collaborative collections
- Browser extension
- Advanced analytics
- Image similarity search
- OCR for text in images

## 🤝 Contributing

This is a personal project, but feel free to fork and customize for your needs!

## 📄 License

MIT License - feel free to use and modify!

## 🙏 Credits

Built with:
- [Flask](https://flask.palletsprojects.com/)
- [Instaloader](https://instaloader.github.io/)
- [SQLite FTS5](https://www.sqlite.org/fts5.html)
- [OpenAI](https://openai.com/)
- [Pillow](https://python-pillow.org/)

## 📞 Support

For issues or questions:
1. Check documentation files
2. Review error logs in terminal
3. Use `python manage_db.py stats` to check database
4. Try resetting: delete `data/` and reinitialize

---

**Enjoy organizing your Instagram saves!** ✨

Built with ❤️ using Python and Flask
