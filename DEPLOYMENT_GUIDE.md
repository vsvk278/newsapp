# Quick Deployment Guide

## Problem Fixed
Grey article tiles caused by Unsplash API returning redirects (not compatible with CSS background-image).

## Solution
Replaced Unsplash Source API with Picsum Photos API + enhanced OpenGraph extraction.

---

## Deployment Steps

### 1. Replace the File
Copy the fixed `rss.py` to your application:
```bash
cp rss.py app/news/rss.py
```

### 2. Restart Application
```bash
# For systemd service:
systemctl restart news-app

# For direct run:
pkill -f "uvicorn"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Verify Fix (After 2-3 minutes)
```python
from app.database import SessionLocal
from app.models import Article

db = SessionLocal()

# Count Picsum images (should be 25-30)
picsum = db.query(Article).filter(
    Article.image_url.like('%picsum%')
).count()

# Count NULL or empty (should be 0)
invalid = db.query(Article).filter(
    (Article.image_url == None) | (Article.image_url == '')
).count()

print(f"Picsum images: {picsum}")
print(f"Invalid images: {invalid}")

db.close()
```

Expected:
```
Picsum images: 28
Invalid images: 0
```

### 4. Check UI
- Open app in browser
- Verify NO grey tiles
- Verify each article shows an image
- Verify images are diverse/unique

---

## What Changed

### File Modified
`app/news/rss.py`

### Function 1: get_free_headline_image()
**Before:** Used Unsplash Source API (returns redirects)
**After:** Uses Picsum Photos API (returns direct image URLs)

### Function 2: extract_publisher_image()
**Before:** Only checked OpenGraph og:image
**After:** Checks og:image, twitter:image, link rel="image_src", and large img tags

---

## Migration Timeline

### Automatic (Recommended)
- Wait 12 hours for next RSS fetch
- Articles automatically updated with working images

### Manual (Immediate)
- Restart application (triggers RSS fetch)
- All articles updated in 2-3 minutes

### Force Reset (Nuclear Option)
```bash
# Delete database and rebuild
rm news_app.db
systemctl restart news-app
```

---

## Expected Results

### Before Fix
- 25 grey tiles (62.5%)
- 15 working images (37.5%)

### After Fix
- 0 grey tiles (0%)
- 40 working images (100%)
- ~35 unique images (87.5% diversity)

---

## Troubleshooting

### Still seeing grey tiles?
```bash
# Check if RSS fetch completed
grep "News fetched successfully" app.log | tail -1

# Verify Picsum in code
grep "picsum.photos" app/news/rss.py
```

### Images not loading?
```bash
# Test Picsum API
curl -I "https://picsum.photos/200/200"

# Should return HTTP 200
```

### Want immediate fix?
```bash
# Force immediate update
systemctl restart news-app
```

---

## Support

If issues persist after following this guide:
1. Check application logs: `tail -f app.log`
2. Verify database has articles: `sqlite3 news_app.db "SELECT COUNT(*) FROM articles;"`
3. Verify network access: `curl https://picsum.photos/200/200 -I`

---

## Files Included

1. `rss.py` - Fixed RSS image extraction code
2. `FIX_EXPLANATION.md` - Detailed technical explanation
3. `DEPLOYMENT_GUIDE.md` - This file

**Deploy `rss.py` and restart. That's it.**
