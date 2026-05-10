# Installation & Testing Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation Steps

### Step 1: Navigate to Project Directory

```bash
cd /Users/pl80an/PycharmProjects/ig-extractor
```

### Step 2: Activate Virtual Environment

You already have a `.venv` directory, so activate it:

```bash
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-SQLAlchemy (database ORM)
- Flask-Migrate (database migrations)
- Instaloader (Instagram API)
- Pillow (image processing)
- python-dotenv (environment variables)
- tqdm (progress bars)

**Note:** OpenAI is optional and commented out by default. Uncomment in `requirements.txt` if you want AI features.

### Step 4: Configure Environment

```bash
cp .env.example .env
```

The default `.env` settings are fine for initial testing. You can configure Instagram credentials later.

### Step 5: Test the Installation

```bash
python test_setup.py
```

This will verify:
- All packages are installed correctly
- Directory structure is complete
- Flask app can be created
- Database models work

Expected output:
```
============================================================
Instagram Organizer - Installation Test
============================================================

Testing imports...
✓ Flask
✓ Flask-SQLAlchemy
✓ Flask-Migrate
✓ Instaloader
✓ Pillow
✓ python-dotenv

Testing project structure...
✓ app/
✓ app/models/
✓ app/routes/
...

Testing app creation...
✓ App created successfully
✓ Database initialized
✓ Models imported

============================================================
Test Results
============================================================
Imports: ✓ PASSED
Project Structure: ✓ PASSED
App Creation: ✓ PASSED
============================================================

✅ All tests passed! You're ready to run the application.
```

### Step 6: Run the Application

```bash
python run.py
```

You should see:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 7: Open in Browser

Navigate to: **http://localhost:5000**

You should see the Instagram Organizer dashboard!

## What to Test

### 1. Navigation
- Click through Dashboard, Posts, Categories, Settings
- All pages should load without errors

### 2. Create Categories
1. Go to **Categories**
2. Click **+ New Category**
3. Enter name (e.g., "Food"), pick a color
4. Click **Create**
5. Category should appear in the list

### 3. View Empty States
- Posts page should show "No posts found" message
- Dashboard stats should all be 0

### 4. Instagram Login (Optional)
1. Go to **Settings**
2. Enter your Instagram username and password
3. Click **Connect Instagram**

**Note:** Full Instagram integration requires completing Phase 2 of the implementation.

## Troubleshooting

### "No module named 'flask'"

The virtual environment isn't activated or packages aren't installed:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### "Address already in use"

Port 5000 is taken. Either:
- Stop the other process using port 5000
- Or change the port in `run.py`:
  ```python
  app.run(host='0.0.0.0', port=5001, debug=True)
  ```

### Database Errors

Delete and recreate:
```bash
rm -rf data/instagram_organizer.db
python run.py  # Will create fresh database
```

### Import Errors

Make sure you're in the project root directory and virtual environment is active.

## What's Working vs What's Not

### ✅ Working (Phase 1 Complete)

- ✅ Flask app structure
- ✅ Database models (Posts, Categories, Tags)
- ✅ All routes defined
- ✅ Basic templates (Dashboard, Posts, Categories, Settings)
- ✅ CSS styling
- ✅ Category CRUD operations
- ✅ Project structure

### 🚧 Not Yet Implemented (Future Phases)

- ❌ Instagram login/authentication
- ❌ Fetching saved posts from Instagram
- ❌ Full-text search (FTS5)
- ❌ AI categorization
- ❌ Tag management
- ❌ Export functionality
- ❌ Bulk operations
- ❌ Progress indicators

These features are planned in the next phases of development.

## Next Steps

Once the basic app is confirmed working:

1. **Phase 2:** Implement Instagram integration
2. **Phase 3:** Add full-text search
3. **Phase 4:** Implement AI categorization
4. **Phase 5-6:** Complete UI features
5. **Phase 7:** Polish and deployment

See `plan.md` in the session folder for the complete roadmap!

## Getting Help

If you encounter issues:

1. Check this guide's Troubleshooting section
2. Review the main `README.md`
3. Check `QUICKSTART.md` for common setup steps
4. Run `python test_setup.py` to diagnose issues
