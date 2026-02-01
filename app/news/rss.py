import feedparser
import re
import urllib.parse
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import RSS_FEEDS
from app.models import Article


# ----------------------------
# Utilities
# ----------------------------

def strip_html_tags(text: str) -> str:
    """Remove HTML tags from text"""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def generate_image_from_headline(headline: str) -> str:
    """
    Generate a FREE, unique, relevant image using Unsplash Source API.
    No API key. No billing. Production-safe.
    """
    # Remove publisher suffix (e.g. " - BBC", " | The Guardian")
    clean_title = re.split(r"[-|]", headline)[0]

    # Normalize text for URL
    keywords = clean_title.replace("’", "").replace("'", "")
    query = urllib.parse.quote_plus(keywords)

    # Unsplash Source API (free)
    return f"https://source.unsplash.com/1200x800/?{query}"


def extract_image_url(entry):
    """Extract image URL from RSS entry with priority fallback"""

    # Priority 1: media:content
    if hasattr(entry, "media_content") and entry.media_content:
        url = entry.media_content[0].get("url")
        if url:
            return url

    # Priority 2: media:thumbnail
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        url = entry.media_thumbnail[0].get("url")
        if url:
            return url

    # Priority 3: links with image type
    if hasattr(entry, "links"):
        for link in entry.links:
            if link.get("type", "").startswith("image"):
                return link.get("href")

    return None


# ----------------------------
# Main fetch logic
# ----------------------------

def fetch_and_store_news(db: Session):
    for category, feed_url in RSS_FEEDS.items():
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:10]:  # Limit per category
            existing = db.query(Article).filter(
                Article.url == entry.link
            ).first()

            # ----------------------------
            # Existing article: upgrade image if needed
            # ----------------------------
            if existing:
                if not existing.image_url or existing.image_url == "/static/default-news.jpg":
                    rss_image_url = extract_image_url(entry)

                    if rss_image_url:
                        existing.image_url = rss_image_url
                    else:
                        existing.image_url = generate_image_from_headline(
                            existing.title
                        )

                    db.commit()

                continue  # Do not create duplicate article

            # ----------------------------
            # New article
            # ----------------------------

            rss_image_url = extract_image_url(entry)
            image_url = rss_image_url if rss_image_url else generate_image_from_headline(
                entry.title)

            published_at = datetime.utcnow()
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])

            raw_summary = entry.get("summary", "")
            clean_summary = strip_html_tags(raw_summary)[:500]

            article = Article(
                title=entry.title,
                summary=clean_summary,
                url=entry.link,
                image_url=image_url,
                category=category,
                published_at=published_at
            )

            db.add(article)

        db.commit()
