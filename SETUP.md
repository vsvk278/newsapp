# Setup Guide - Daily News Application

## Quick Start

This application is designed to run with zero configuration. No API keys, no external accounts, no setup required.

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Local Development

1. **Clone repository**:
```bash
git clone <your-repo-url>
cd news_app
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run application**:
```bash
uvicorn app.main:app --reload
```

4. **Access application**:
- Open http://localhost:8000 in your browser
- Register a new account
- Start browsing news!

## Deployment to Render (Free)

### Step 1: Prepare Repository

Ensure your code is in a GitHub repository.

### Step 2: Create Web Service

1. Go to https://render.com
2. Sign up or log in
3. Click "New +" → "Web Service"
4. Connect your GitHub repository

### Step 3: Configure Service

**Build Command**:
```
pip install -r requirements.txt
```

**Start Command**:
```
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

**Environment Variables** (Optional):
- `SECRET_KEY`: Any random string (for session security)

### Step 4: Deploy

Click "Create Web Service" and Render will:
- Build your application
- Deploy it automatically
- Provide a public URL

## No Configuration Needed

Unlike many applications, this news aggregator requires:
- ❌ No API keys
- ❌ No database setup
- ❌ No external accounts
- ❌ No billing setup

Everything works out of the box!

## How It Works

### Automatic News Fetching

On startup and every 12 hours, the application:
1. Fetches news from Google News RSS feeds
2. Extracts publisher-provided images
3. Stores articles in local SQLite database
4. Updates existing articles with missing images

### Image Handling

Images are sourced from:
1. RSS feed media fields
2. Article OpenGraph meta tags
3. Category-specific fallback images

All automatic, no configuration needed.

## Verification

After deployment, verify everything works:

1. **Visit your application URL**
2. **Register an account**
3. **Check news displays** - Should see articles with images
4. **Test categories** - Technology, Business, Sports, Health
5. **Try bookmarking** - Save and view bookmarks

## Customization (Optional)

### Change News Sources

Edit `app/config.py`:

```python
RSS_FEEDS = {
    "Technology": "https://news.google.com/rss/search?q=technology",
    "Business": "https://news.google.com/rss/search?q=business",
    # Add more categories...
}
```

### Change Fetch Interval

Edit `app/config.py`:

```python
FETCH_INTERVAL_HOURS = 12  # Change to desired hours
```

### Customize Fallback Images

Replace files in `static/`:
- `fallback-technology.jpg`
- `fallback-business.jpg`
- `fallback-sports.jpg`
- `fallback-health.jpg`

## Troubleshooting

### Application Won't Start

**Check Python version**:
```bash
python --version  # Should be 3.11+
```

**Reinstall dependencies**:
```bash
pip install -r requirements.txt --force-reinstall
```

### No Articles Appearing

**Wait for initial fetch**:
- First fetch happens on startup
- Takes 30-60 seconds
- Refresh page after a minute

**Check logs**:
```bash
# Look for "News fetched" messages
```

### Images Not Loading

**Check network**:
- Ensure server can access external URLs
- Verify no firewall blocking HTTP requests

**Check fallback images**:
- Ensure `static/fallback-*.jpg` files exist
- These should always display even if external images fail

## Database

### Location

SQLite database stored at: `./news_app.db`

### Backup (Optional)

```bash
cp news_app.db news_app_backup.db
```

### Reset (Clear All Data)

```bash
rm news_app.db
# Restart application to create fresh database
```

## Performance

### Expected Load

Designed for:
- 10 concurrent users
- 20 total users
- Low traffic

### Resource Usage

- **Memory**: ~100-200 MB
- **Storage**: ~10-50 MB (database grows over time)
- **CPU**: Minimal (spikes during RSS fetch)

## Security

### Built-in Features

- ✅ Password hashing (bcrypt)
- ✅ HTTP-only cookies
- ✅ HTTPS (via Render)
- ✅ SQL injection protection (SQLAlchemy ORM)

### Recommendations

1. **Set SECRET_KEY**:
```bash
export SECRET_KEY="your-random-string-here"
```

2. **Use strong passwords** when registering

3. **Keep dependencies updated**:
```bash
pip install -r requirements.txt --upgrade
```

## Monitoring

### Check Application Health

Visit: `http://your-app-url/`

Should display news articles.

### Check Database

```python
from app.database import SessionLocal
from app.models import Article, User

db = SessionLocal()

print(f"Articles: {db.query(Article).count()}")
print(f"Users: {db.query(User).count()}")

db.close()
```

## Updates

### Updating Application

1. **Pull latest code**:
```bash
git pull origin main
```

2. **Update dependencies** (if changed):
```bash
pip install -r requirements.txt
```

3. **Restart application**:
```bash
# Stop current instance (Ctrl+C)
uvicorn app.main:app --reload
```

For Render: Automatic deployment on git push.

## Cost

**Total Cost**: $0

- Hosting: Free (Render free tier)
- Database: Free (SQLite, local)
- News sources: Free (Google News RSS)
- Image extraction: Free (no API)

## Limitations

### Free Tier Constraints

Render free tier includes:
- 750 hours/month (enough for 24/7)
- Sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds

### Scalability

Designed for small-scale use:
- ✅ 10 concurrent users
- ⚠️ Not suitable for high traffic
- ⚠️ SQLite not ideal for >100 concurrent users

## Support

### Documentation

- `README.md` - Overview and features
- `IMAGE_EXTRACTION.md` - Image handling details
- `DEPLOYMENT_NOTES.md` - Technical documentation

### Common Issues

See `TROUBLESHOOTING.md` (if exists) or check:
- Application logs for errors
- Database file exists and is writable
- Network connectivity to external URLs

## Summary

✅ **Zero configuration** - Works out of the box
✅ **Free hosting** - Render free tier
✅ **No API keys** - Nothing to configure
✅ **Automatic updates** - News fetched every 12 hours
✅ **Simple deployment** - Push to GitHub, done

Get started in minutes with no setup required!