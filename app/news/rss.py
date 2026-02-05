import feedparser
from datetime import datetime
from sqlalchemy.orm import Session
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.config import RSS_FEEDS, CATEGORY_FALLBACKS
from app.models import Article


def strip_html_tags(text):
    """Remove HTML tags from text"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def is_valid_image_url(url: str) -> bool:
    """
    Validate image URL - reject logos, icons, sprites, favicons
    """
    if not url or not isinstance(url, str):
        return False

    url_lower = url.lower()

    # Reject common logo/icon patterns
    invalid_patterns = ['logo', 'icon', 'sprite',
                        'favicon', 'avatar', 'default-thumb']
    for pattern in invalid_patterns:
        if pattern in url_lower:
            return False

    # Reject Google News placeholders
    if 'news.google.com' in url_lower and '/images/' in url_lower:
        return False

    # Must be http/https
    if not url.startswith('http'):
        return False

    return True


def extract_keywords_from_headline(headline: str, category: str) -> list:
    """
    Extract meaningful keywords from headline and category for image search
    """
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'says', 'said',
        'new', 'first', 'more', 'after', 'over', 'year', 'years'
    }

    # Clean and split headline
    words = re.findall(r'\b[a-zA-Z]{3,}\b', headline.lower())

    # Remove stop words
    keywords = [w for w in words if w not in stop_words]

    # Start with category
    result = [category.lower()]

    # Add up to 2 keywords from headline
    result.extend(keywords[:2])

    return result[:3]


def get_free_headline_image(headline: str, category: str, article_url: str) -> str:
    """
    Get a free placeholder image based on article hash.
    Uses Picsum Photos API which returns DIRECT image URLs (not redirects).
    Deterministic: same article always gets same image.
    """
    # Create deterministic seed from article URL
    seed = abs(hash(article_url)) % 1000
    
    # Picsum Photos API - returns DIRECT image URLs (works in CSS background-image)
    # No redirects, no API key needed, completely free
    url = f"https://picsum.photos/seed/{seed}/800/600"
    
    return url


def extract_rss_image(entry) -> str:
    """
    Extract image URL from RSS entry media fields.
    Priority: media:content -> media:thumbnail -> enclosure -> links
    """
    # Priority 1: media:content
    if hasattr(entry, 'media_content') and entry.media_content:
        url = entry.media_content[0].get('url')
        if url and is_valid_image_url(url):
            return url

    # Priority 2: media:thumbnail
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        url = entry.media_thumbnail[0].get('url')
        if url and is_valid_image_url(url):
            return url

    # Priority 3: enclosure with image MIME type
    if hasattr(entry, 'enclosures'):
        for enclosure in entry.enclosures:
            if 'type' in enclosure and enclosure.get('type', '').startswith('image/'):
                url = enclosure.get('href') or enclosure.get('url')
                if url and is_valid_image_url(url):
                    return url

    # Priority 4: links with image type
    if hasattr(entry, 'links'):
        for link in entry.links:
            if 'type' in link and link.get('type', '').startswith('image/'):
                url = link.get('href')
                if url and is_valid_image_url(url):
                    return url

    return None


def is_google_placeholder_image(url: str) -> bool:
    """
    Detect if an image is a Google News placeholder.
    Returns True if the image should be rejected.
    """
    if not url or not isinstance(url, str):
        return False

    url_lower = url.lower()

    # Reject Google News and Google User Content images
    google_patterns = [
        'news.google.com',
        'googleusercontent.com',
        'gstatic.com/images',
        'google.com/logos'
    ]

    for pattern in google_patterns:
        if pattern in url_lower:
            return True

    return False


def resolve_publisher_url(url: str) -> str:
    """
    Follow redirects from Google News RSS links to get real publisher URL.
    Google News RSS links look like: news.google.com/rss/articles/...
    This resolves to the actual publisher site (cnn.com, nytimes.com, etc.)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        # Follow redirects to get final URL
        response = requests.get(url, headers=headers,
                                timeout=10, allow_redirects=True)

        # Return the final URL after all redirects
        return response.url

    except Exception:
        # If redirect fails, return original URL
        return url


def extract_publisher_image(url: str) -> str:
    """
    Extract image from publisher article URL using priority order:
    1. OpenGraph og:image
    2. Twitter card image
    3. link rel="image_src"
    4. First large img tag
    
    For Google News RSS links, follows redirects to get real publisher URL first.
    Rejects Google placeholder images.
    """
    try:
        # If this is a Google News RSS link, resolve to real publisher URL
        if 'news.google.com' in url:
            url = resolve_publisher_url(url)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Priority 1: OpenGraph og:image
        og_image = soup.find('meta', property='og:image')
        if not og_image:
            og_image = soup.find('meta', attrs={'name': 'og:image'})

        if og_image and og_image.get('content'):
            image_url = og_image['content']
            if not image_url.startswith('http'):
                image_url = urljoin(url, image_url)
            if not is_google_placeholder_image(image_url) and is_valid_image_url(image_url):
                return image_url

        # Priority 2: Twitter card image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if not twitter_image:
            twitter_image = soup.find('meta', property='twitter:image')
        
        if twitter_image and twitter_image.get('content'):
            image_url = twitter_image['content']
            if not image_url.startswith('http'):
                image_url = urljoin(url, image_url)
            if not is_google_placeholder_image(image_url) and is_valid_image_url(image_url):
                return image_url

        # Priority 3: link rel="image_src"
        image_src_link = soup.find('link', rel='image_src')
        if image_src_link and image_src_link.get('href'):
            image_url = image_src_link['href']
            if not image_url.startswith('http'):
                image_url = urljoin(url, image_url)
            if not is_google_placeholder_image(image_url) and is_valid_image_url(image_url):
                return image_url

        # Priority 4: First large img tag (likely article image)
        img_tags = soup.find_all('img')
        for img in img_tags:
            # Check both src and data-src (lazy loading)
            image_url = img.get('src') or img.get('data-src')
            if not image_url:
                continue
                
            # Skip small images (likely icons/logos)
            width = img.get('width')
            height = img.get('height')
            if width and height:
                try:
                    if int(width) < 200 or int(height) < 200:
                        continue
                except (ValueError, TypeError):
                    pass
            
            # Make absolute URL
            if not image_url.startswith('http'):
                image_url = urljoin(url, image_url)
            
            # Validate and return if valid
            if not is_google_placeholder_image(image_url) and is_valid_image_url(image_url):
                return image_url

        return None

    except Exception:
        # Silent failure - never block article ingestion
        return None


def get_category_fallback_image(category: str) -> str:
    """Get category-specific static fallback image"""
    return CATEGORY_FALLBACKS.get(category, '/static/default-news.jpg')


def get_article_image(entry, category: str) -> str:
    """
    Get article image using strict priority pipeline:
    1. RSS media images (media:content, media:thumbnail, enclosure)
    2. Publisher images (OpenGraph, Twitter card, link rel, img tags)
    3. Free deterministic placeholder (Picsum Photos - direct URLs)
    4. Category default static image

    Never raises exceptions - always returns a valid image URL.
    """
    try:
        # Step 1: Try RSS media images
        rss_image = extract_rss_image(entry)
        if rss_image:
            return rss_image

        # Step 2: Try OpenGraph extraction from publisher
        if hasattr(entry, 'link') and entry.link:
            og_image = extract_publisher_image(entry.link)
            if og_image:
                return og_image

        # Step 3: Free deterministic placeholder (Picsum Photos)
        if hasattr(entry, 'title') and hasattr(entry, 'link'):
            picsum_image = get_free_headline_image(
                entry.title,
                category,
                entry.link
            )
            return picsum_image

    except Exception:
        # Silent failure - fall through to category default
        pass

    # Step 4: Category default (last resort)
    return get_category_fallback_image(category)


def fetch_and_store_news(db: Session):
    """
    Fetch RSS feeds and store articles with images.
    Never blocks ingestion due to image failures.
    """
    for category, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
        except Exception:
            # Skip this category if feed parsing fails
            continue

        for entry in feed.entries[:10]:
            try:
                # Check if article already exists
                existing = db.query(Article).filter(
                    Article.url == entry.link).first()

                if existing:
                    # Update image if it's invalid, missing, or a Google placeholder
                    should_update = (
                        not existing.image_url or
                        existing.image_url == '/static/default-news.jpg' or
                        existing.image_url.startswith('/static/fallback-') or
                        not is_valid_image_url(existing.image_url) or
                        is_google_placeholder_image(existing.image_url)
                    )

                    if should_update:
                        try:
                            existing.image_url = get_article_image(
                                entry, category)
                            db.commit()
                        except Exception:
                            db.rollback()

                    continue

                # Get image using priority pipeline (never fails)
                image_url = get_article_image(entry, category)

                # Parse published date
                published_at = datetime.utcnow()
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        published_at = datetime(*entry.published_parsed[:6])
                    except Exception:
                        pass

                # Clean summary from HTML tags
                raw_summary = entry.get('summary', '')
                clean_summary = strip_html_tags(raw_summary)[:500]

                # Create article - never fail due to image
                article = Article(
                    title=entry.title,
                    summary=clean_summary,
                    url=entry.link,
                    image_url=image_url,
                    category=category,
                    published_at=published_at
                )

                db.add(article)

            except Exception:
                # Skip this article if there's any error
                # Never block entire ingestion
                continue

        # Commit per category
        try:
            db.commit()
        except Exception:
            db.rollback()