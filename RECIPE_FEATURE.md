# Recipe Feature Update - May 10, 2026

## Changes Made

### 1. Fixed Thumbnail Display ✅
**Issue:** Images not showing in post list and detail views
**Fix:** Changed thumbnail path from `url_for('static', filename='../' + post.thumbnail_path)` to `/{{ post.thumbnail_path }}`

**Files Modified:**
- `app/templates/posts/list.html` - Line 23
- `app/templates/posts/detail.html` - Line 14

### 2. Fixed Category Addition ✅
**Issue:** User reported not being able to add categories
**Status:** Feature was already implemented but using simple prompt()
**How it works:**
- Click "Add Category" button on post detail page
- Select from existing categories via prompt
- Category is added via POST to `/posts/<id>/categorize`

**Files Involved:**
- `app/routes/posts.py` - Lines 101-151 (categorize_post endpoint)
- `app/templates/posts/detail.html` - Lines 252-295 (JavaScript functions)

### 3. Added Recipe Parsing Feature 🍳 NEW!
**Purpose:** Extract ingredients and directions from Instagram captions for food recipes

**New Components:**

#### A. Database Changes
Added 3 new columns to `posts` table:
- `recipe_ingredients` (TEXT) - JSON array of ingredients
- `recipe_directions` (TEXT) - JSON array of cooking steps
- `is_recipe` (BOOLEAN) - Flag for recipe posts

#### B. Recipe Parser Service
**File:** `app/services/recipe_parser.py`

**Features:**
- 100+ ingredient keywords (proteins, dairy, vegetables, fruits, grains, spices, etc.)
- 50+ cooking action verbs (cook, bake, fry, mix, etc.)
- Measurement units (cup, tbsp, oz, gram, etc.)
- Smart pattern detection for:
  - Ingredient lists (bullets, numbers, keywords)
  - Direction steps (numbered, action verbs)
  - Recipe indicators ("recipe", "ingredients", "directions")

**How it works:**
1. Analyzes caption for recipe indicators
2. Extracts structured ingredients (bullets/numbers)
3. Falls back to keyword matching if no structure
4. Extracts numbered directions or action-based sentences
5. Returns cleaned, formatted lists

#### C. Recipe Routes
**File:** `app/routes/recipes.py`

**Endpoints:**
- `POST /recipes/parse/<post_id>` - Parse single post
- `POST /recipes/batch-parse` - Parse multiple posts
- `POST /recipes/update/<post_id>` - Manually update recipe
- `GET /recipes/list` - List all recipes
- `GET /recipes/<post_id>` - View recipe detail

#### D. UI Updates
**File:** `app/templates/posts/detail.html`

**For Non-Recipe Posts:**
- 🍳 "Parse Recipe" button with gradient styling
- Help text explaining feature
- One-click parsing with confirmation

**For Recipe Posts:**
- 🍳 Recipe Details section (yellow/orange theme)
- Ingredients list (bulleted, white background)
- Directions list (numbered, step-by-step)
- ✏️ Edit Recipe button (placeholder)

**CSS Added:**
- `.btn-recipe` - Gradient pink/red button
- `.recipe-section` - Yellow container with border
- `.ingredients-list` / `.directions-list` - White cards
- Responsive styling

#### E. Application Updates
**File:** `app/__init__.py`
- Registered `recipes` blueprint
- Added custom Jinja2 filter `from_json` for template JSON parsing

**File:** `app/models/post.py`
- Added recipe fields to model
- Updated `to_dict()` to include recipe data

## Usage

### Parse a Recipe:
1. Go to any post detail page
2. Click "🍳 Parse Recipe" button
3. Algorithm extracts ingredients and steps
4. Page reloads showing recipe details

### Example Caption Format:
```
Amazing Pasta Recipe! 🍝

Ingredients:
- 2 cups pasta
- 1 cup tomato sauce
- 1/4 cup parmesan cheese
- 2 cloves garlic
- Salt and pepper to taste

Directions:
1. Boil pasta in salted water for 8-10 minutes
2. Sauté garlic in olive oil until fragrant
3. Add tomato sauce and simmer for 5 minutes
4. Toss cooked pasta with sauce
5. Top with parmesan and serve hot!
```

### Parser Output:
**Ingredients:**
- 2 cups pasta
- 1 cup tomato sauce
- 1/4 cup parmesan cheese
- 2 cloves garlic
- Salt and pepper to taste

**Directions:**
1. Boil pasta in salted water for 8-10 minutes
2. Sauté garlic in olive oil until fragrant
3. Add tomato sauce and simmer for 5 minutes
4. Toss cooked pasta with sauce
5. Top with parmesan and serve hot

## Algorithm Details

### Recipe Detection:
Post is considered a recipe if:
- Contains words: "recipe", "ingredients", "directions", "instructions"
- OR has 3+ ingredient keywords AND 2+ direction keywords

### Ingredient Extraction:
1. Look for "Ingredients:" section
2. Extract bulleted/numbered lines
3. Validate against keyword dictionary
4. Remove emojis and formatting
5. Limit to 20 ingredients

### Direction Extraction:
1. Look for "Directions:" or "Steps:" section
2. Extract numbered steps
3. Extract sentences with action verbs
4. Clean and capitalize
5. Limit to 15 steps

### Keyword Matching Fallback:
If no structured format found:
- Scan all lines for ingredient keywords
- Extract sentences with cooking verbs
- Filter by length and relevance

## Technical Notes

- Recipe data stored as JSON strings in database
- Parsing is deterministic (no AI required)
- Works offline, no API costs
- Accuracy depends on caption structure
- Best with well-formatted captions
- Handles various emoji styles and bullet points

## Future Enhancements

Potential additions:
- [ ] Manual recipe editing UI
- [ ] Recipe export (PDF, text)
- [ ] Ingredient scaling calculator
- [ ] Cooking time extraction
- [ ] Nutrition info (if in caption)
- [ ] Recipe search by ingredient
- [ ] OCR for recipes in images
- [ ] Recipe sharing/printing

## Testing

To test:
1. Fetch saved posts from Instagram
2. Find a food recipe post
3. Click "Parse Recipe"
4. Verify ingredients and directions extracted
5. Check recipe display formatting

## Files Changed

1. `app/models/post.py` - Added recipe fields
2. `app/services/recipe_parser.py` - NEW parser logic
3. `app/routes/recipes.py` - NEW recipe endpoints
4. `app/__init__.py` - Registered blueprint, added filter
5. `app/templates/posts/detail.html` - Recipe UI
6. `app/templates/posts/list.html` - Fixed thumbnail path
7. Database: Added 3 columns to posts table

## Restart Required

```bash
# Stop current server (Ctrl+C)
# Restart:
python3 run.py
```

All features ready to use! 🚀
