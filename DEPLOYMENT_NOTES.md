# Deployment Notes - UI Enhancements

## Changes Made

### 1. AI-Generated Images Per Headline

**Modified**: `app/config.py`
- Added `OPENAI_API_KEY` configuration from environment variable

**Modified**: `app/news/rss.py`
- Added `generate_image_from_headline()` function
- Uses OpenAI DALL-E 3 API to generate unique images
- Prompt format: "Realistic news photograph illustrating: {headline}. Cinematic lighting, professional journalism style, no text, no watermark."
- Images are generated server-side only when RSS doesn't provide an image
- Generated image URLs are cached in the `image_url` database field
- No regeneration on subsequent requests (images persist in database)

**Modified**: `requirements.txt`
- Added `openai` package for image generation

### 2. Removed Secondary Headline/Summary

**Modified**: `templates/index.html`
- Removed summary text (`<p>` tag with article.summary)
- Cards now display only: Category, Main headline, Date, Read more link
- Adjusted spacing (mb-2 changed to mb-4 for headline)

**Modified**: `templates/bookmarks.html`
- Removed summary text (`<p>` tag with article.summary)
- Cards now display only: Category, Main headline, Date, Read more link
- Adjusted spacing (mb-2 changed to mb-4 for headline)

## Configuration Required

**CRITICAL**: Set the following environment variable before deployment:

```bash
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
```

Without this API key:
- AI image generation will fallback to `/static/default-news.jpg`
- All articles without RSS images will use the default image

## How It Works

1. **Image Generation Flow**:
   - RSS feed is fetched
   - If RSS contains image → use it
   - If no RSS image → generate AI image from headline
   - Generated URL is saved to database
   - Future requests use cached URL (no regeneration)

2. **Image Caching**:
   - Each article has only ONE image generated (on first fetch)
   - Image URLs are stored in the existing `image_url` field
   - No new database tables or fields added
   - Existing articles are never regenerated

3. **Card Display**:
   - Category badge (top left)
   - Bookmark star (top right)
   - Main headline (center, bold white text)
   - Published date (bottom left)
   - "Read more →" link (bottom right)
   - Dark gradient overlay ensures text readability

## Testing Checklist

- [ ] OpenAI API key is set in environment
- [ ] New articles get unique AI-generated images
- [ ] Images match headline topics
- [ ] No summary text visible on cards
- [ ] Card height remains consistent
- [ ] Text is readable over all images
- [ ] Gradient overlay displays correctly
- [ ] Existing cached images are not regenerated
- [ ] Bookmark functionality works
- [ ] All links work correctly

## Cost Considerations

**OpenAI DALL-E 3 Pricing**:
- ~$0.04 per image (1024x1024, standard quality)
- With 4 categories × 10 articles = 40 images per fetch cycle
- Cost per 12-hour cycle: ~$1.60 (worst case, if all need generation)
- Most articles will have RSS images, reducing costs significantly

**Cost Optimization**:
- Images are generated ONCE and cached permanently
- Only new articles without RSS images trigger generation
- Consider using RSS images when available (already implemented)

## No Breaking Changes

- Database schema unchanged
- Authentication unchanged
- RSS fetching schedule unchanged
- All existing functionality intact
- Routing unchanged

# Deployment Notes - AI Image Generation Fixes

## Critical Fixes Applied

### Fix 1: API Key Validation (NO SILENT FALLBACK)

**Previous Behavior:**
- Missing `OPENAI_API_KEY` → Silent fallback to `/static/default-news.jpg`
- No error indication
- Application ran but with duplicate default images

**New Behavior:**
- Missing `OPENAI_API_KEY` → **Runtime error raised**
- Clear error message: "OPENAI_API_KEY environment variable is required for AI image generation"
- Application will not silently degrade
- **OPENAI_API_KEY is now MANDATORY**

### Fix 2: Image Regeneration for Cached Articles

**Previous Behavior:**
- Articles with `/static/default-news.jpg` were never updated
- Existing articles always skipped (cache logic)
- Same default image displayed for all articles

**New Behavior:**
- Checks existing articles for default image
- If `image_url == '/static/default-news.jpg'`:
  - Attempts to extract RSS image
  - If no RSS image, generates AI image from headline
  - Updates existing row (no duplicate creation)
  - Commits changes to database
- Articles with real images (RSS or previously generated) are NOT regenerated

### Fix 3: Image Generation Logic Flow

**For New Articles:**
1. Extract RSS image (if available)
2. If no RSS image → Generate AI image from headline
3. Store article with image URL
4. Commit to database

**For Existing Articles:**
1. Check if exists in database
2. If has default image → Regenerate (RSS or AI)
3. If has real image → Skip (no update needed)
4. Never create duplicates

## Updated Image Generation

**Function:** `generate_image_from_headline(headline)`

**Behavior:**
- ✅ Raises `RuntimeError` if `OPENAI_API_KEY` missing
- ✅ Uses exact prompt format:
  ```
  Realistic news photograph illustrating: {headline}. Professional journalism style, cinematic lighting, no text, no watermark.
  ```
- ✅ Returns OpenAI-hosted image URL
- ✅ Raises `RuntimeError` on generation failure

**Function:** `extract_image_url(entry)`

**Behavior:**
- ✅ Returns actual URL if RSS has image
- ✅ Returns `None` if no RSS image (not default image)
- ✅ Enables proper AI generation fallback

## Configuration Required

### MANDATORY Environment Variable

```bash
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
```

**CRITICAL:** This is no longer optional. The application will raise an error on startup if:
- The key is missing
- Articles need AI-generated images

**Local Development:**
```bash
export OPENAI_API_KEY=YOUR_API_KEY_HERE
uvicorn app.main:app --reload
```

**Render Deployment:**
1. Go to Environment tab
2. Add `OPENAI_API_KEY` with your OpenAI API key
3. Save and redeploy

## Migration Instructions

### For Existing Deployments with Default Images

If your database already has articles with `/static/default-news.jpg`:

1. **Set OPENAI_API_KEY** in environment
2. **Restart application**
3. **Wait for next scheduled fetch** (or trigger manually)
4. Articles with default images will automatically update

**Manual Trigger (Optional):**
```python
from app.database import SessionLocal
from app.news.rss import fetch_and_store_news

db = SessionLocal()
fetch_and_store_news(db)
db.close()
```

### Fresh Deployment

1. Set `OPENAI_API_KEY` before first deployment
2. Deploy application
3. Articles will get unique images on first fetch

## Error Handling

### Missing API Key Error

**Error Message:**
```
RuntimeError: OPENAI_API_KEY environment variable is required for AI image generation. 
Please set it in your environment or deployment configuration.
```

**Solution:**
- Set the environment variable
- Restart the application

### Image Generation Failure

**Error Message:**
```
RuntimeError: Failed to generate AI image for headline '{headline}': {error details}
```

**Possible Causes:**
- Invalid API key
- OpenAI API rate limits
- Network issues
- Insufficient API credits

**Solution:**
- Check API key validity at https://platform.openai.com/api-keys
- Verify billing at https://platform.openai.com/account/billing
- Check rate limits
- Wait and retry

## Testing Checklist

After applying fixes:

- [ ] `OPENAI_API_KEY` is set in environment
- [ ] Application starts without errors
- [ ] Each new article gets unique AI-generated image
- [ ] Previously cached articles with default images are updated
- [ ] No duplicate articles created
- [ ] RSS images are used when available (no unnecessary generation)
- [ ] All article cards display unique images
- [ ] No silent fallback to default image

## Cost Implications

**Before Fix:**
- All articles used default image (free, but broken)

**After Fix:**
- RSS images used when available (free)
- AI generation only when needed (~$0.04 per image)
- **One-time cost** to regenerate existing default images
- **Ongoing cost** only for new articles without RSS images

**Initial Migration Cost:**
- If 40 cached articles have default images
- Cost: 40 × $0.04 = $1.60 (one-time)

## Files Modified

**Modified:**
- `app/news/rss.py` - All three functions updated

**Changes:**
1. `generate_image_from_headline()`:
   - Raises error if API key missing
   - Updated prompt format
   - Raises error on generation failure

2. `extract_image_url()`:
   - Returns `None` instead of default image
   - Enables proper fallback logic

3. `fetch_and_store_news()`:
   - Checks existing articles for default images
   - Updates existing articles (no duplicates)
   - Generates AI images for articles without RSS images

## Rollback Instructions

If you need to revert to silent fallback behavior (not recommended):

1. Modify `generate_image_from_headline()` to return `/static/default-news.jpg` on errors
2. Modify `extract_image_url()` to return `/static/default-news.jpg` instead of `None`
3. Remove update logic for existing articles
4. Redeploy

**Warning:** Rolling back will restore the duplicate image issue.

## No Breaking Changes

- ✅ Database schema unchanged
- ✅ Authentication unchanged
- ✅ Routing unchanged
- ✅ Frontend unchanged
- ✅ RSS fetching schedule unchanged

**New Requirement:**
- ⚠️ `OPENAI_API_KEY` is now **mandatory** (was optional with silent fallback)