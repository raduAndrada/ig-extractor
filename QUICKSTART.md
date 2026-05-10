# Quick Start Guide

## 🚀 Getting Started

### 1. Install Dependencies

First, activate your virtual environment and install the required packages:

```bash
# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your preferred settings. You can leave most values as default for now.

### 3. Run the Application

```bash
python run.py
```

The application will start at `http://localhost:5000`

### 4. First Steps

1. Navigate to **Settings** to configure your Instagram credentials (optional - you can do this later)
2. Go to **Categories** and create a few categories like:
   - Food 🍕
   - Travel ✈️
   - Fashion 👗
   - Inspiration 💡
   - Memes 😂
3. Click **Fetch Posts** on the dashboard to sync your saved Instagram posts
4. Start organizing!

## 📝 Important Notes

### Instagram Login

- The app uses Instaloader which requires Instagram credentials
- Your credentials are stored locally only
- If you have 2FA enabled, you'll need to provide the code when prompted
- Instagram has rate limits - be patient when fetching large numbers of posts

### AI Categorization

There are two options for AI-powered categorization:

**Option 1: OpenAI (Recommended for best results)**
- Requires an API key from OpenAI
- Costs money per API call (~$0.01 per image)
- Provides high-quality categorization

**Option 2: Local Models (Free)**
- Requires more disk space and RAM
- Free to use
- Slower but no API costs

You can also organize manually without AI!

### Data Storage

- Database: `data/instagram_organizer.db` (SQLite)
- Thumbnails: `data/thumbnails/` (JPEG images)
- Session files: `session-*` (Instagram login sessions)

All data is stored locally on your machine.

## 🛠️ Troubleshooting

### Installation Issues

**PIL/Pillow issues:**
```bash
pip install --upgrade Pillow
```

**Instaloader issues:**
```bash
pip install --upgrade instaloader
```

### Instagram Login Fails

- Check your username and password
- If you have 2FA, make sure to enter the code when prompted
- Wait a few minutes if you've tried multiple times (rate limiting)

### Database Errors

Reset the database (WARNING: deletes all data):
```bash
rm data/instagram_organizer.db
python run.py  # Creates new database
```

## 📚 Next Steps

Once the basic app is running, you can:

1. Implement full-text search (FTS5)
2. Add AI categorization
3. Create export functionality
4. Add batch operations
5. Improve the UI

Check the main `plan.md` in the session folder for the complete roadmap!
