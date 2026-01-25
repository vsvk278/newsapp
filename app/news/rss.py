import feedparser
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import RSS_FEEDS
from app.models import Article

def fetch_and_store_news(db: Session):
    for category, feed_url in RSS_FEEDS.items():
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries[:10]:  # Limit to 10 articles per category
            # Check if article already exists
            existing = db.query(Article).filter(Article.url == entry.link).first()
            if existing:
                continue
            
            # Extract image URL if available
            image_url = None
            if hasattr(entry, 'media_content') and entry.media_content:
                image_url = entry.media_content[0].get('url')
            elif hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                image_url = entry.media_thumbnail[0].get('url')
            
            # Parse published date
            published_at = datetime.utcnow()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])
            
            # Create article
            article = Article(
                title=entry.title,
                summary=entry.get('summary', '')[:500],  # Limit summary length
                url=entry.link,
                image_url=image_url,
                category=category,
                published_at=published_at
            )
            
            db.add(article)
        
        db.commit()
