# Troubleshooting Guide - Image Generation

## Common Issues and Solutions

### Issue 1: All Articles Show Same Default Image

**Symptoms:**
- Every news card has the same placeholder image
- No unique images per headline
- Articles display `/static/default-news.jpg`

**Root Causes:**
1. `OPENAI_API_KEY` environment variable not set
2. Articles were cached before API key was configured
3. RSS fetch hasn't run since API key was added

**Solutions:**

**Step 1: Verify API Key**
```bash
# Linux/Mac
echo $OPENAI_API_KEY

# Windows PowerShell
echo $env:OPENAI_API_KEY

# Should output: ...
```

**Step 2: Set API Key (if missing)**
```bash
# Linux/Mac
export OPENAI_API_KEY=YOUR_API_KEY_HERE

# Windows Command Prompt
set OPENAI_API_KEY=YOUR_API_KEY_HERE

# Windows PowerShell
$env:OPENAI_API_KEY="YOUR_API_KEY_HERE"
```

**Step 3: Restart Application**
```bash
# Stop current instance (Ctrl+C)
# Start again
uvicorn app.main:app --reload
```

**Step 4: Wait for RSS Fetch or Trigger Manually**

The application fetches news every 12 hours. To update immediately:

```python
# Run in Python shell or create a script
from app.database import SessionLocal
from app.news.rss import fetch_and_store_news

db = SessionLocal()
try:
    fetch_and_store_news(db)
    print("News fetched and images generated successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
```

**Step 5: Verify Database**

Check that articles now have unique image URLs:

```python
from app.database import SessionLocal
from app.models import Article

db = SessionLocal()
articles = db.query(Article).limit(10).all()

for article in articles:
    print(f"{article.title[:50]}... -> {article.image_url[:60]}...")

db.close()
```

Expected output:
```
Tech Giant Announces New Product... -> https://oaidalleapiprodscus.blob.core.windows.net/...
Sports Team Wins Championship... -> https://oaidalleapiprodscus.blob.core.windows.net/...
```

NOT:
```
Tech Giant Announces New Product... -> /static/default-news.jpg
Sports Team Wins Championship... -> /static/default-news.jpg
```

---

### Issue 2: Application Won't Start

**Symptoms:**
```
RuntimeError: OPENAI_API_KEY environment variable is required for AI image generation.
Please set it in your environment or deployment configuration.
```

**Root Cause:**
- `OPENAI_API_KEY` not set in environment

**Solution:**

1. **Get OpenAI API Key** (if you don't have one):
   - Go to https://platform.openai.com/api-keys
   - Create new secret key
   - Copy the key (starts with ``)

2. **Set Environment Variable:**
   ```bash
   export OPENAI_API_KEY=YOUR_API_KEY_HERE
   ```

3. **Restart Application:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **For Render Deployment:**
   - Go to Render Dashboard
   - Select your web service
   - Click "Environment" tab
   - Add variable: `OPENAI_API_KEY` = `YOUR_API_KEY_HERE`
   - Save and redeploy

---

### Issue 3: "Failed to Generate AI Image" Error

**Symptoms:**
```
RuntimeError: Failed to generate AI image for headline 'Your Headline Here': [error details]
```

**Common Causes & Solutions:**

**Cause 1: Invalid API Key**
```
Error: Incorrect API key provided
```
- **Solution:** Verify key at https://platform.openai.com/api-keys
- Regenerate key if needed
- Update environment variable

**Cause 2: Insufficient Credits**
```
Error: You exceeded your current quota
```
- **Solution:** Add billing at https://platform.openai.com/account/billing
- Verify payment method
- Add credits to account

**Cause 3: Rate Limit**
```
Error: Rate limit exceeded
```
- **Solution:** Wait 1 minute and retry
- DALL-E 3 limit: 5 images/minute
- System will retry on next fetch cycle

**Cause 4: Network Issues**
```
Error: Connection timeout
```
- **Solution:** Check internet connection
- Verify OpenAI API status: https://status.openai.com
- Retry in a few minutes

---

### Issue 4: High OpenAI Costs

**Symptoms:**
- Unexpected charges on OpenAI account
- More images generated than expected

**Diagnosis:**

1. **Check OpenAI Usage:**
   - Go to https://platform.openai.com/usage
   - Review DALL-E 3 requests
   - Check timestamps

2. **Check Database Image URLs:**
   ```python
   from app.database import SessionLocal
   from app.models import Article
   
   db = SessionLocal()
   
   total = db.query(Article).count()
   openai_images = db.query(Article).filter(
       Article.image_url.like('%oaidalleapi%')
   ).count()
   rss_images = total - openai_images
   
   print(f"Total articles: {total}")
   print(f"OpenAI generated: {openai_images}")
   print(f"RSS images: {rss_images}")
   print(f"Cost estimate: ${openai_images * 0.04:.2f}")
   
   db.close()
   ```

**Cost Reduction Strategies:**

1. **Verify RSS Feeds Provide Images:**
   - Most Google News RSS feeds include images
   - If many are missing, consider different RSS sources

2. **Set OpenAI Spending Limits:**
   - Go to https://platform.openai.com/account/limits
   - Set monthly hard cap
   - Enable email alerts

3. **Monitor Regular Costs:**
   - Expected: $0.20-$0.80 per day (typical)
   - If higher, check RSS image availability

---

### Issue 5: Images Not Updating After Setting API Key

**Symptoms:**
- API key is set correctly
- Application starts successfully
- Old articles still show `/static/default-news.jpg`
- New articles get AI-generated images

**Root Cause:**
- RSS fetch hasn't run since API key was added
- Scheduler waits for 12-hour interval

**Solution:**

**Option 1: Wait for Scheduled Fetch**
- Next fetch will update old articles automatically
- Happens every 12 hours

**Option 2: Trigger Manual Fetch**
```python
from app.database import SessionLocal
from app.news.rss import fetch_and_store_news

db = SessionLocal()
fetch_and_store_news(db)
db.close()

print("Articles updated!")
```

**Option 3: Restart Application**
- Scheduler fetches news immediately on startup
```bash
# Stop application (Ctrl+C)
# Start again
uvicorn app.main:app --reload
```

---

### Issue 6: Images Display But Don't Match Headlines

**Symptoms:**
- Images are unique but seem unrelated to headlines
- Generic or abstract images instead of news-related

**Diagnosis:**

1. **Check Image URLs in Database:**
   ```python
   from app.database import SessionLocal
   from app.models import Article
   
   db = SessionLocal()
   article = db.query(Article).first()
   print(f"Title: {article.title}")
   print(f"Image URL: {article.image_url}")
   db.close()
   ```

2. **Verify Prompt Format:**
   - Should be: `Realistic news photograph illustrating: {headline}. Professional journalism style, cinematic lighting, no text, no watermark.`

**Possible Causes:**

1. **Headline Too Vague:**
   - Short or generic headlines produce generic images
   - Solution: This is a limitation of RSS feed quality

2. **DALL-E 3 Interpretation:**
   - AI interprets headlines creatively
   - Solution: This is expected behavior

3. **Wrong Prompt Format:**
   - Check `app/news/rss.py` function `generate_image_from_headline()`
   - Verify prompt matches specification

---

## Quick Diagnostic Checklist

Run through this checklist to diagnose issues:

- [ ] `OPENAI_API_KEY` environment variable is set
- [ ] API key is valid (check at https://platform.openai.com/api-keys)
- [ ] OpenAI account has billing enabled
- [ ] Application starts without errors
- [ ] RSS fetch has run at least once since API key was set
- [ ] Database shows unique OpenAI URLs (not `/static/default-news.jpg`)
- [ ] UI displays unique background images per article
- [ ] No duplicate articles in database

---

## Getting Additional Help

### Logs

Check application logs for errors:
```bash
# Application should log errors during RSS fetch
# Look for lines containing "Error generating image" or "RuntimeError"
```

### Database Inspection

```python
from app.database import SessionLocal
from app.models import Article

db = SessionLocal()

# Check for articles with default images
default_images = db.query(Article).filter(
    Article.image_url == '/static/default-news.jpg'
).count()

print(f"Articles with default image: {default_images}")

# Check recent articles
recent = db.query(Article).order_by(
    Article.published_at.desc()
).limit(5).all()

for article in recent:
    print(f"{article.title[:40]}... | {article.image_url[:60]}...")

db.close()
```

### Contact Support

If issues persist:

1. Gather information:
   - Error messages
   - Environment variable status
   - OpenAI account status
   - Database query results

2. Check documentation:
   - `OPENAI_SETUP.md`
   - `IMAGE_GENERATION_FIXES.md`
   - `DEPLOYMENT_NOTES.md`

3. Review OpenAI status:
   - https://status.openai.com
   - Check for API outages