# Image Extraction Pipeline

## Overview

This application uses a Google News-style approach to display publisher-provided images with each article. Images are extracted directly from news sources, ensuring relevance and authenticity.

## Image Selection Pipeline

For each article, images are selected in the following priority order:

### 1. RSS Media Fields (Primary)

The application first checks RSS feed entries for embedded media:

- **media:content** - Standard RSS media content field
- **media:thumbnail** - RSS media thumbnail field
- **Links with image type** - RSS links tagged as images

**Advantages:**
- Fastest (no additional HTTP requests)
- Provided directly by news aggregator
- Already optimized for display

### 2. OpenGraph Extraction (Secondary)

If no RSS image is available, the application fetches the article URL and extracts the OpenGraph image:

```html
<meta property="og:image" content="https://example.com/image.jpg">
<meta name="og:image" content="https://example.com/image.jpg">
```

**Implementation:**
- Single HTTP request per article (with timeout)
- User-Agent header for compatibility
- Extracts first available OpenGraph tag
- Converts relative URLs to absolute

**Advantages:**
- Most publishers include OpenGraph images
- Represents the actual article content
- Standard metadata format

### 3. Category Fallback (Tertiary)

If both RSS and OpenGraph extraction fail, a category-specific fallback image is used:

- **Technology**: Blue gradient with tech icon
- **Business**: Green gradient with chart icon
- **Sports**: Red gradient with ball icon
- **Health**: Pink gradient with cross icon

**Advantages:**
- Always available
- Visually indicates category
- Maintains UI consistency

## Implementation Details

### Core Functions

#### `extract_rss_image(entry) -> Optional[str]`

Extracts image URL from RSS entry media fields.

```python
# Priority order:
1. media:content[0].url
2. media:thumbnail[0].url
3. links[].href where type starts with "image"
```

Returns `None` if no image found.

#### `extract_publisher_image(url: str) -> Optional[str]`

Fetches article URL and extracts OpenGraph image.

**Features:**
- 10-second timeout
- User-Agent header spoofing
- HTML parsing with BeautifulSoup
- Absolute URL conversion
- Silent failure on errors

**Returns:**
- Absolute image URL if found
- `None` if extraction fails

#### `get_category_fallback_image(category: str) -> str`

Returns category-specific fallback image path.

**Mapping:**
```python
{
    "Technology": "/static/fallback-technology.jpg",
    "Business": "/static/fallback-business.jpg",
    "Sports": "/static/fallback-sports.jpg",
    "Health": "/static/fallback-health.jpg"
}
```

#### `get_article_image(entry, category: str) -> str`

Main pipeline function that orchestrates image selection.

**Flow:**
```
1. Try extract_rss_image(entry)
   ↓ if None
2. Try extract_publisher_image(entry.link)
   ↓ if None
3. Return get_category_fallback_image(category)
```

Always returns a valid image URL.

## Error Handling

### Silent Failures

The application is designed to never crash due to image extraction:

- **Network timeouts**: Caught and ignored
- **Invalid HTML**: Caught and ignored
- **Missing meta tags**: Returns None, continues to fallback
- **HTTP errors**: Caught and ignored

### Logging

Errors are intentionally not logged to avoid noise. The fallback system ensures a valid image is always displayed.

## Caching and Updates

### Database Caching

Once an image URL is determined, it's stored in the `Article.image_url` field and reused for all future requests.

### Automatic Updates

Existing articles are updated if their `image_url` is:
- `NULL` or empty
- `/static/default-news.jpg`
- Starts with `/static/fallback-` (old category fallback)

**Update trigger:**
- Next RSS fetch cycle (every 12 hours)
- Application startup (initial fetch)

### No Duplicate Articles

The system checks for existing articles by URL before creating new entries. Updates are applied to existing records only.

## Performance Considerations

### HTTP Requests

- **RSS images**: 0 additional requests (already in feed)
- **OpenGraph extraction**: 1 request per article without RSS image
- **Timeout**: 10 seconds maximum per request

### Rate Limiting

Google News RSS typically includes images for most articles, minimizing OpenGraph extraction needs.

**Typical scenario:**
- 4 categories × 10 articles = 40 articles
- ~30-35 articles have RSS images (0 requests)
- ~5-10 articles need OpenGraph (5-10 requests)

### Concurrent Fetching

Image extraction happens during RSS fetch, which runs:
- Once on application startup
- Every 12 hours via scheduler
- Not during user requests (no blocking)

## Technical Requirements

### Dependencies

```python
requests       # HTTP client for fetching article HTML
beautifulsoup4 # HTML parsing for OpenGraph extraction
```

### No API Keys Required

- No authentication needed
- No rate limits (beyond standard HTTP politeness)
- No external service costs

## Fallback Images

Category fallback images are SVG files stored in `/static/`:

- `fallback-technology.jpg` - Blue gradient with tech icon
- `fallback-business.jpg` - Green gradient with chart
- `fallback-sports.jpg` - Red gradient with sports icon
- `fallback-health.jpg` - Pink gradient with health cross
- `default-news.jpg` - Gray gradient (generic fallback)

**Format:** SVG (scalable, small file size)
**Size:** 800×600 pixels
**Purpose:** Maintain visual consistency when no publisher image available

## Comparison to Other Approaches

### vs. AI Image Generation

| Aspect | Publisher Images | AI Generation |
|--------|------------------|---------------|
| Relevance | High (from source) | Variable |
| Cost | Free | ~$0.04 per image |
| Speed | Fast (cached) | Slow (API call) |
| Authenticity | Real news images | Synthetic |
| Reliability | High | Depends on API |

### vs. Stock Photos

| Aspect | Publisher Images | Stock Photos |
|--------|------------------|---------------|
| Relevance | High | Low (generic) |
| Cost | Free | Often requires API |
| Uniqueness | Per article | Often repeated |
| Source trust | Publisher | Third-party |

## Troubleshooting

### All Articles Show Fallback Images

**Possible Causes:**
1. Network connectivity issues
2. Publishers blocking requests (User-Agent issue)
3. RSS feeds not providing images

**Solutions:**
1. Check network connectivity
2. Verify User-Agent header is set
3. Test OpenGraph extraction manually

### Some Articles Missing Images

**Expected Behavior:**
- Not all articles have publisher images
- Fallback images are working as designed

**To Verify:**
- Check `Article.image_url` in database
- Should show mix of external URLs and fallback paths

### OpenGraph Extraction Failing

**Common Reasons:**
1. Article URL behind paywall/login
2. Publisher doesn't use OpenGraph tags
3. Network timeout (slow site)

**All cases gracefully fall back to category image.**

## Future Enhancements

Possible improvements (not currently implemented):

1. **Image caching**: Download and serve images locally
2. **Retry logic**: Retry failed extractions after delay
3. **Image validation**: Verify image URLs are accessible
4. **Multiple sources**: Try additional meta tags (Twitter Cards, etc.)

## Summary

The image extraction pipeline provides:

- ✅ Authentic publisher-provided images
- ✅ Zero API costs
- ✅ Graceful fallback system
- ✅ No external dependencies beyond HTTP
- ✅ Stable image URLs (cached permanently)
- ✅ Silent error handling (never crashes)

This approach prioritizes reliability, cost-effectiveness, and content authenticity.